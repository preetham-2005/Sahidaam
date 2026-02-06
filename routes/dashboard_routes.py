from flask import Blueprint, jsonify, request
from helpers.auth import login_required, get_current_user
from services.leaderboard_service import (
    get_time_based_leaderboard,
    get_global_leaderboard,
    get_paginated_leaderboard
)

dashboard_bp = Blueprint("dashboard_bp", __name__)


# =========================
# Weekly / Monthly
# =========================
@dashboard_bp.route("/api/leaderboard/<period>")
@login_required
def leaderboard_period(period):
    user = get_current_user()

    if period not in ["weekly", "monthly"]:
        return jsonify({"error": "Invalid period"}), 400

    days = 7 if period == "weekly" else 30

    data = get_time_based_leaderboard(
        village=user.village,
        days=days
    )

    return jsonify(data), 200


# =========================
# Global Leaderboard
# =========================
@dashboard_bp.route("/api/leaderboard/global")
@login_required
def global_leaderboard():
    return jsonify(get_global_leaderboard()), 200


# =========================
# Paginated Village Leaderboard
# =========================
@dashboard_bp.route("/api/leaderboard")
@login_required
def paginated_leaderboard():
    user = get_current_user()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    return jsonify(
        get_paginated_leaderboard(
            village=user.village,
            page=page,
            per_page=per_page
        )
    ), 200
