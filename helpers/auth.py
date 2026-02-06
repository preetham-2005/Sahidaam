from functools import wraps
from flask import session, jsonify, redirect, url_for, request

from extensions import db
from models.user import User


# =====================================================
# Get currently logged-in user
# =====================================================
def get_current_user():
    """
    Returns User object if logged in, else None
    """
    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


# =====================================================
# Login required decorator (API + Browser safe)
# =====================================================
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_current_user()

        # Not logged in
        if not user:
            if request.path.startswith("/api"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("auth.login_page"))

        # Blocked user protection
        if getattr(user, "is_blocked", False):
            session.clear()
            if request.path.startswith("/api"):
                return jsonify({"error": "Account blocked"}), 403
            return redirect(url_for("auth.login_page"))

        return view(*args, **kwargs)

    return wrapped


# =====================================================
# Logout helper
# =====================================================
def logout_user():
    session.clear()
