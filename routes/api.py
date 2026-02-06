from flask import Blueprint, request, jsonify, session
from extensions import db
from models.user import User
from models.price import PriceEntry
from helpers.auth import get_current_user, login_required
from services.fraud_service import detect_fraud

api_bp = Blueprint("api", __name__)

# =====================================================
# REGISTER (API)
# =====================================================

@api_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm = data.get("confirm_password", "")
    name = data.get("name", username)

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if "@" not in email:
        return jsonify({"error": "Invalid email address"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(username=username, email=email, name=name)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "redirect": "/login"
    }), 201


# =====================================================
# SET VILLAGE
# =====================================================

@api_bp.route("/api/set-village", methods=["POST"])
@login_required
def set_village():
    user = get_current_user()
    data = request.get_json() or {}

    village = data.get("village", "").strip()
    state = data.get("state", "").strip()

    if not village:
        return jsonify({"error": "Village is required"}), 400

    user.village = village
    user.state = state if state else None
    db.session.commit()

    return jsonify({
        "success": True,
        "redirect": "/dashboard"
    }), 200


# =====================================================
# DASHBOARD SUMMARY DATA
# =====================================================

@api_bp.route("/api/dashboard-data", methods=["GET"])
@login_required
def dashboard_data():
    user = get_current_user()

    if not user.village:
        return jsonify({"error": "Village not set"}), 400

    prices = PriceEntry.query.filter_by(village=user.village).all()

    return jsonify({
        "items": len({p.item_name for p in prices}),
        "contributors": len({p.user_id for p in prices}),
        "submissions": len(prices),
        "score": int(user.trust_score),
        "user": {
            "name": user.name,
            "village": user.village,
            "score": int(user.trust_score)
        }
    }), 200


# =====================================================
# ✅ LIVE PRICES (FIXED ISSUE)
# =====================================================

@api_bp.route("/api/live-prices", methods=["GET"])
@login_required
def live_prices():
    user = get_current_user()

    prices = (
        PriceEntry.query
        .filter_by(village=user.village)
        .order_by(PriceEntry.created_at.desc())
        .all()
    )

    return jsonify({
        "prices": [
            {
                "item": p.item_name,
                "price": p.price,
                "user_id": p.user_id,
                "created_at": p.created_at.isoformat()
            }
            for p in prices
        ]
    }), 200


# =====================================================
# SUBMIT PRICE
# =====================================================

@api_bp.route("/api/submit-price", methods=["POST"])
@login_required
def submit_price():
    user = get_current_user()
    data = request.get_json() or {}

    if not user.village:
        return jsonify({"error": "Set village before submitting prices"}), 400

    item = data.get("item", "").strip()
    price = data.get("price")

    if not item:
        return jsonify({"error": "Item name is required"}), 400

    try:
        price = float(price)
        if price <= 0:
            raise ValueError
    except Exception:
        return jsonify({"error": "Invalid price value"}), 400

    # 🔐 Fraud detection
    suspicious, reasons = detect_fraud(user, user.village)
    if suspicious:
        return jsonify({
            "error": "Suspicious activity detected",
            "reasons": reasons
        }), 429

    entry = PriceEntry(
        user_id=user.id,
        village=user.village,
        item_name=item,
        price=price
    )

    user.trust_score = min(user.trust_score + 5, 100)

    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Price submitted successfully"
    }), 201
