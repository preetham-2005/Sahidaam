from models.price import Price
from models import db

def submit_price(user, data):
    entry = Price(
        user_id=user.id,
        village=user.village,
        item_name=data["item"],
        price=float(data["price"]),
        unit=data.get("unit", "per kg")
    )
    db.session.add(entry)
    user.trust_score += 5
    db.session.commit()
    return entry
