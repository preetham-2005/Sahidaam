from datetime import datetime
from extensions import db


class PriceEntry(db.Model):
    __tablename__ = "price_entry"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    village = db.Column(db.String(120), nullable=False)
    item_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    item_category = db.Column(db.String(50), nullable=False, default="Grains")
    purchase_location = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)  # Crop / receipt photo

    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PriceEntry {self.item_name} ₹{self.price}>"
