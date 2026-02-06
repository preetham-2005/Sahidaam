from extensions import db

class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))  # emoji or icon name

    min_score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "min_score": self.min_score,
            "max_score": self.max_score
        }
