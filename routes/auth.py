import os
import json
import base64
import time
from datetime import datetime
from collections import defaultdict
from flask import (
    Blueprint, request, jsonify,
    session, redirect, url_for, render_template, current_app
)

from extensions import db
from models.user import User
from services.otp_service import send_otp, verify_otp

auth_bp = Blueprint("auth", __name__)

# =====================================================
# BRUTE-FORCE PROTECTION & RATE LIMITER
# =====================================================
_failed_attempts = defaultdict(list)  # ip/identifier -> [timestamps]

def is_rate_limited(identifier, max_attempts=5, window_seconds=300):
    """Check if identifier exceeded max failed attempts in window."""
    now = time.time()
    # Prune old attempts
    _failed_attempts[identifier] = [t for t in _failed_attempts[identifier] if now - t < window_seconds]
    return len(_failed_attempts[identifier]) >= max_attempts

def record_failed_attempt(identifier):
    """Record a failed attempt timestamp."""
    _failed_attempts[identifier].append(time.time())

def clear_attempts(identifier):
    """Reset failed attempts on successful authentication."""
    if identifier in _failed_attempts:
        del _failed_attempts[identifier]

# =====================================================
# AUTH PAGES
# =====================================================

@auth_bp.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("auth.start"))
    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")
    return render_template("login.html", google_client_id=google_client_id)


@auth_bp.route("/register")
def register_page():
    if session.get("user_id"):
        return redirect(url_for("auth.start"))
    google_client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")
    return render_template("register.html", google_client_id=google_client_id)


@auth_bp.route("/village-selection")
def village_selection_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    return render_template("village_selection.html")


@auth_bp.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    
    user_id = session.get("user_id")
    user = db.session.get(User, user_id)
    
    if not user or user.is_blocked:
        session.clear()
        return redirect(url_for("auth.login_page"))
    
    if not user.village:
        return redirect(url_for("auth.village_selection_page"))
    
    return render_template("dashboard.html")


@auth_bp.route("/start")
def start():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login_page"))

    user = db.session.get(User, user_id)
    if not user or user.is_blocked:
        session.clear()
        return redirect(url_for("auth.login_page"))

    if user.village:
        return redirect("/dashboard")

    return redirect("/village-selection")


# =====================================================
# GOOGLE AUTH API (CONTINUE WITH GOOGLE)
# =====================================================

@auth_bp.route("/api/auth/google", methods=["POST"])
def api_google_auth():
    """
    Handles Continue with Google authentication.
    Accepts Google GSI Credential token or direct Google profile info.
    Auto-creates and verifies users, then logs them in.
    """
    try:
        data = request.get_json() or {}
        credential = data.get("credential")  # Google ID token if using GSI
        email = data.get("email", "").strip().lower()
        name = data.get("name", "").strip()

        # If Google JWT ID token was passed by Google Identity Services SDK
        if credential:
            try:
                # Decode JWT payload (payload is part index 1)
                parts = credential.split(".")
                if len(parts) >= 2:
                    padding = '=' * (4 - len(parts[1]) % 4)
                    payload_bytes = base64.urlsafe_b64decode(parts[1] + padding)
                    payload = json.loads(payload_bytes.decode('utf-8'))
                    
                    email = payload.get("email", email).lower()
                    name = payload.get("name", name) or email.split("@")[0]
            except Exception as jwt_err:
                print(f"[Google Auth] Warning decoding JWT: {jwt_err}")

        if not email or "@" not in email:
            return jsonify({"error": "Valid Google email address required"}), 400

        # Find or create user
        user = User.query.filter_by(email=email).first()
        is_new_user = False

        if not user:
            # Generate a unique base username from email prefix
            base_username = email.split("@")[0].replace(".", "_")[:20]
            candidate_username = base_username
            counter = 1
            while User.query.filter_by(username=candidate_username).first():
                candidate_username = f"{base_username[:15]}_{counter}"
                counter += 1

            user = User(
                username=candidate_username,
                email=email,
                name=name or candidate_username,
                is_verified=True,
                email_verified_at=datetime.utcnow()
            )
            # Set a secure random password hash for OAuth accounts
            user.set_password(os.urandom(24).hex())
            db.session.add(user)
            db.session.commit()
            is_new_user = True
        else:
            if user.is_blocked:
                return jsonify({"error": "This account is blocked"}), 403
            
            # Ensure Google account is marked verified
            user.is_verified = True
            if not user.email_verified_at:
                user.email_verified_at = datetime.utcnow()
            if name and not user.name:
                user.name = name

        user.last_login = datetime.utcnow()
        user.last_login_source = "google_oauth"
        db.session.commit()

        # Establish user session
        session.clear()
        session["user_id"] = user.id
        session.permanent = True

        return jsonify({
            "success": True,
            "message": "Google authentication successful",
            "is_new_user": is_new_user,
            "redirect": "/start",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "village": user.village
            }
        }), 200

    except Exception as e:
        print(f"[Google Auth Error] {e}")
        return jsonify({"error": f"Google authentication failed: {str(e)}"}), 500


# =====================================================
# PASSWORD LOGIN API (BRUTE-FORCE HARDENED)
# =====================================================

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    try:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
        data = request.get_json() or {}

        username = data.get("username", "").strip()
        password = data.get("password", "")

        # Check IP/Username rate limits
        if is_rate_limited(f"login_{ip}") or is_rate_limited(f"login_{username}"):
            return jsonify({
                "error": "Too many failed login attempts. Please wait 5 minutes before trying again."
            }), 429

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = User.query.filter(
            (User.username == username) | (User.email == username.lower())
        ).first()

        if not user or not user.check_password(password):
            record_failed_attempt(f"login_{ip}")
            record_failed_attempt(f"login_{username}")
            return jsonify({"error": "Invalid username or password"}), 401

        if not user.is_verified:
            otp_res = send_otp(user)
            resp = {
                "error": "Account email is unverified. Verification OTP generated.",
                "unverified": True,
                "email": user.email,
                "email_sent": otp_res.get("email_sent", False)
            }
            if current_app.debug or not otp_res.get("email_sent"):
                resp["dev_otp"] = user.otp_code
            return jsonify(resp), 403

        if user.is_blocked:
            return jsonify({"error": "Account is blocked"}), 403

        # Successful login: clear brute-force records
        clear_attempts(f"login_{ip}")
        clear_attempts(f"login_{username}")

        session.clear()
        session["user_id"] = user.id
        session.permanent = True

        user.last_login = datetime.utcnow()
        user.last_login_source = "web"
        db.session.commit()

        return jsonify({
            "success": True,
            "redirect": "/start"
        }), 200
    
    except Exception as err:
        print(f"Login error: {err}")
        return jsonify({"error": "Server error processing login"}), 500


# =====================================================
# EMAIL OTP LOGIN — STEP 1 (REQUEST OTP)
# =====================================================

@auth_bp.route("/api/login/email", methods=["POST"])
def email_login_request():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if is_rate_limited(f"otp_{ip}", max_attempts=8, window_seconds=600):
        return jsonify({"error": "Too many OTP requests. Please wait a few minutes."}), 429

    if not email or "@" not in email:
        return jsonify({"error": "Valid email address required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No account found with this email. Please register first."}), 404

    if user.is_blocked:
        return jsonify({"error": "Account is blocked"}), 403

    record_failed_attempt(f"otp_{ip}")
    otp_res = send_otp(user)

    msg = "OTP sent to your Gmail inbox!" if otp_res.get("email_sent") else "OTP generated successfully!"
    resp = {
        "success": True,
        "message": msg,
        "email_sent": otp_res.get("email_sent", False)
    }
    
    if current_app.debug or not otp_res.get("email_sent"):
        resp["dev_otp"] = user.otp_code

    return jsonify(resp), 200


# =====================================================
# EMAIL OTP LOGIN — STEP 2 (VERIFY OTP - BRUTE FORCE HARDENED)
# =====================================================

@auth_bp.route("/api/login/email/verify", methods=["POST"])
def email_login_verify():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    if is_rate_limited(f"otp_verify_{ip}") or is_rate_limited(f"otp_verify_{email}"):
        return jsonify({"error": "Too many incorrect OTP attempts. Please request a new OTP."}), 429

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid request"}), 400

    if user.is_blocked:
        return jsonify({"error": "Account is blocked"}), 403

    if not verify_otp(user, otp):
        record_failed_attempt(f"otp_verify_{ip}")
        record_failed_attempt(f"otp_verify_{email}")
        return jsonify({"error": "Invalid or expired OTP code"}), 401

    clear_attempts(f"otp_verify_{ip}")
    clear_attempts(f"otp_verify_{email}")

    user.is_verified = True
    if not user.email_verified_at:
        user.email_verified_at = datetime.utcnow()
    user.last_login = datetime.utcnow()

    session.clear()
    session["user_id"] = user.id
    session.permanent = True

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "OTP verified successfully",
        "redirect": "/start"
    }), 200


# =====================================================
# LOGOUT
# =====================================================

@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({
        "success": True,
        "redirect": "/"
    }), 200
