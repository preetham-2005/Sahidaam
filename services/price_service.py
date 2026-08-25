from models.price import PriceEntry
from extensions import db

def submit_price(user, data):
    entry = PriceEntry(
        user_id=user.id,
        village=user.village,
        item_name=data["item"],
        price=float(data["price"])
    )
    db.session.add(entry)
    user.trust_score = min(user.trust_score + 5, 100)
    db.session.commit()
    return entry
