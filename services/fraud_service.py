"""
Fraud Detection Service v2 (ML-ready)
Logs suspicious activity for audit & admin review
"""

from datetime import datetime, timedelta
from extensions import db
from models.price import PriceEntry
from models.fraud_log import FraudLog


# =====================================================
# PUBLIC API (USED BY routes/api.py)
# =====================================================
def is_user_suspicious(user, village=None):
    """
    Backward-compatible wrapper used by API layer

    Returns:
    True  -> suspicious
    False -> safe
    """
    suspicious, _ = detect_fraud(user, village)
    return suspicious


# =====================================================
# CORE FRAUD DETECTION ENGINE
# =====================================================
def detect_fraud(user, village=None):
    """
    ML-ready fraud detection engine

    Returns:
    (is_suspicious: bool, reasons: list[str])
    """

    reasons = []

    # -------------------------
    # RULE 1: Rate limit (spam)
    # -------------------------
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    recent_count = (
        PriceEntry.query
        .filter(
            PriceEntry.user_id == user.id,
            PriceEntry.created_at >= one_hour_ago
        )
        .count()
    )

    if recent_count >= 5:
        reasons.append("Too many price submissions in last hour")
        _log_fraud(
            user_id=user.id,
            reason="Rate limit exceeded",
            severity="high"
        )

    # -------------------------
    # RULE 2: New user abuse
    # -------------------------
    if user.created_at >= datetime.utcnow() - timedelta(hours=2) and recent_count >= 3:
        reasons.append("New user submitting prices too frequently")
        _log_fraud(
            user_id=user.id,
            reason="New user spam pattern",
            severity="medium"
        )

    # -------------------------
    # FUTURE ML HOOK
    # -------------------------
    # features = extract_features(user)
    # ml_score = ml_model.predict(features)

    return bool(reasons), reasons


# =====================================================
# INTERNAL FRAUD LOGGER
# =====================================================
def _log_fraud(user_id, reason, severity="low"):
    """
    Persist fraud signals for admin audit & ML training
    """

    log = FraudLog(
        user_id=user_id,
        reason=reason,
        severity=severity
    )

    db.session.add(log)
    db.session.commit()
