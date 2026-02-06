from flask import (
    Blueprint, request, jsonify,
    session, redirect, url_for, render_template
)
from datetime import datetime

from extensions import db
from models.user import User
from services.otp_service import send_otp, verify_otp

auth_bp = Blueprint("auth", __name__)

# =====================================================
# AUTH PAGES
# =====================================================

@auth_bp.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("auth.start"))
    return render_template("login.html")


@auth_bp.route("/register")
def register_page():
    if session.get("user_id"):
        return redirect(url_for("auth.start"))
    return render_template("register.html")


# ✅ FIX 1: ADD THIS ROUTE (VERY IMPORTANT)
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
# PASSWORD LOGIN API
# =====================================================

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json() or {}

        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "User not found"}), 401

        if not user.check_password(password):
            return jsonify({"error": "Invalid password"}), 401

        if user.is_blocked:
            return jsonify({"error": "Account blocked"}), 403

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
        return jsonify({"error": "Server error"}), 500


# =====================================================
# EMAIL OTP LOGIN — STEP 1
# =====================================================

@auth_bp.route("/api/login/email", methods=["POST"])
def email_login_request():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email or "@" not in email:
        return jsonify({"error": "Valid email required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not registered"}), 404

    if user.is_blocked:
        return jsonify({"error": "Account blocked"}), 403

    send_otp(user)

    return jsonify({
        "success": True,
        "message": "OTP sent to email"
    }), 200


# =====================================================
# EMAIL OTP LOGIN — STEP 2
# =====================================================

@auth_bp.route("/api/login/email/verify", methods=["POST"])
def email_login_verify():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid request"}), 400

    if not verify_otp(user, otp):
        return jsonify({"error": "Invalid or expired OTP"}), 401

    user.is_verified = True
    user.last_login = datetime.utcnow()

    session.clear()
    session["user_id"] = user.id
    session.permanent = True

    db.session.commit()

    return jsonify({
        "success": True,
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
