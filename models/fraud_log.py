# models/fraud_log.py

from datetime import datetime
from extensions import db


class FraudLog(db.Model):
    __tablename__ = "fraud_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    reason = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(50), default="low", index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<FraudLog user={self.user_id} severity={self.severity}>"
