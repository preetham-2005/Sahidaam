from extensions import db

class UserBadge(db.Model):
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    badge_id = db.Column(
        db.Integer,
        db.ForeignKey("badges.id"),
        nullable=False
    )

    earned_at = db.Column(db.DateTime, server_default=db.func.now())
