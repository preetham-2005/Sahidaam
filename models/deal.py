from datetime import datetime
from extensions import db


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    crop_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)  # e.g. "50 Bags / 25 Quintals"
    price_per_unit = db.Column(db.Float, nullable=False)
    village = db.Column(db.String(120), nullable=False)
    location_details = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=True)
    description = db.Column(db.String(300), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to user
    seller = db.relationship("User", backref=db.backref("deals", lazy="dynamic", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Deal {self.crop_name} {self.quantity} @ ₹{self.price_per_unit}>"


class PriceAlert(db.Model):
    __tablename__ = "price_alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    crop_name = db.Column(db.String(120), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), default="above")  # "above" or "below"
    village = db.Column(db.String(120), nullable=True)
    is_triggered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("alerts", lazy="dynamic", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<PriceAlert {self.crop_name} {self.condition} ₹{self.target_price}>"
