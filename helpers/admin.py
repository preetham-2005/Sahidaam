# routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from extensions import db
from models.user import User
from models.price import PriceEntry
from helpers.auth import login_required

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# =========================
# ADMIN ACCESS GUARD
# =========================
def admin_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login_page"))

        user = db.session.get(User, session["user_id"])
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access only"}), 403

        return f(*args, **kwargs)

    return wrapper


# =========================
# ADMIN DASHBOARD
# =========================
@admin_bp.route("/")
@admin_required
def admin_dashboard():
    stats = {
        "total_users": User.query.count(),
        "verified_users": User.query.filter_by(is_verified=True).count(),
        "blocked_users": User.query.filter_by(is_blocked=True).count(),
        "total_prices": PriceEntry.query.count()
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats
    )


# =========================
# USERS LIST
# =========================
@admin_bp.route("/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template(
        "admin/users.html",
        users=users
    )


# =========================
# BLOCK / UNBLOCK USER
# =========================
@admin_bp.route("/users/<int:user_id>/block", methods=["POST"])
@admin_required
def block_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_blocked = True
    db.session.commit()

    return jsonify({"success": True})


@admin_bp.route("/users/<int:user_id>/unblock", methods=["POST"])
@admin_required
def unblock_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_blocked = False
    db.session.commit()

    return jsonify({"success": True})


# =========================
# PROMOTE TO ADMIN
# =========================
@admin_bp.route("/users/<int:user_id>/promote", methods=["POST"])
@admin_required
def promote_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_admin = True
    db.session.commit()

    return jsonify({"success": True})


# =========================
# SYSTEM HEALTH (API)
# =========================
@admin_bp.route("/api/health")
@admin_required
def admin_health():
    return jsonify({
        "status": "ok",
        "users": User.query.count(),
        "prices": PriceEntry.query.count()
    })
