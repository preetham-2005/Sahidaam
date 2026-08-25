from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models.user import User
from models.price import PriceEntry
from services.badge_service import calculate_badge


# =========================
# Village Weekly / Monthly Leaderboard
# =========================
def get_time_based_leaderboard(village, days=7, limit=10):
    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.session.query(
            User.id,
            User.name,
            User.username,
            User.trust_score,
            func.count(PriceEntry.id).label("contributions")
        )
        .join(PriceEntry, PriceEntry.user_id == User.id)
        .filter(
            PriceEntry.village == village,
            PriceEntry.created_at >= since
        )
        .group_by(User.id)
        .order_by(
            User.trust_score.desc(),
            func.count(PriceEntry.id).desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "rank": index + 1,
            "name": row.name,
            "username": row.username,
            "trust_score": round(row.trust_score, 2),
            "contributions": row.contributions,
            "badge": calculate_badge(row.trust_score, row.contributions)
        }
        for index, row in enumerate(results)
    ]


# =========================
# Global Leaderboard
# =========================
def get_global_leaderboard(limit=10):
    results = (
        db.session.query(
            User.id,
            User.name,
            User.username,
            User.trust_score,
            func.count(PriceEntry.id).label("contributions")
        )
        .join(PriceEntry, PriceEntry.user_id == User.id)
        .group_by(User.id)
        .order_by(
            User.trust_score.desc(),
            func.count(PriceEntry.id).desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "rank": index + 1,
            "name": row.name,
            "username": row.username,
            "trust_score": round(row.trust_score, 2),
            "contributions": row.contributions,
            "badge": calculate_badge(row.trust_score, row.contributions)
        }
        for index, row in enumerate(results)
    ]


# =========================
# Paginated Village Leaderboard
# =========================
def get_paginated_leaderboard(village, page=1, per_page=10):
    base_query = (
        db.session.query(
            User.id,
            User.name,
            User.username,
            User.trust_score,
            func.count(PriceEntry.id).label("contributions")
        )
        .join(PriceEntry, PriceEntry.user_id == User.id)
        .filter(PriceEntry.village == village)
        .group_by(User.id)
        .order_by(User.trust_score.desc())
    )

    # ✅ Correct total count
    total_users = (
        db.session.query(func.count(func.distinct(User.id)))
        .join(PriceEntry, PriceEntry.user_id == User.id)
        .filter(PriceEntry.village == village)
        .scalar()
    )

    results = (
        base_query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "page": page,
        "per_page": per_page,
        "total": total_users,
        "data": [
            {
                "name": row.name,
                "username": row.username,
                "trust_score": round(row.trust_score, 2),
                "contributions": row.contributions,
                "badge": calculate_badge(row.trust_score, row.contributions)
            }
            for row in results
        ]
    }
