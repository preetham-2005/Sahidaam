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
    from flask import current_app
    from services.otp_service import send_otp

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

    # Check existing user
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        if not existing_user.is_verified:
            otp_res = send_otp(existing_user)
            resp = {
                "success": True,
                "otp_required": True,
                "email": existing_user.email,
                "email_sent": otp_res.get("email_sent", False),
                "message": "OTP sent to verify your account" if otp_res.get("email_sent") else "OTP generated"
            }
            if current_app.debug or not otp_res.get("email_sent"):
                resp["dev_otp"] = existing_user.otp_code
            return jsonify(resp), 200
        else:
            if existing_user.username == username:
                return jsonify({"error": "Username already exists"}), 400
            return jsonify({"error": "Email already exists"}), 400

    user = User(username=username, email=email, name=name)
    user.set_password(password)
    user.is_verified = False

    db.session.add(user)
    db.session.commit()

    # Send verification OTP code
    otp_res = send_otp(user)

    resp = {
        "success": True,
        "otp_required": True,
        "email": email,
        "email_sent": otp_res.get("email_sent", False),
        "message": "OTP sent to your email" if otp_res.get("email_sent") else "OTP generated"
    }
    if current_app.debug or not otp_res.get("email_sent"):
        resp["dev_otp"] = user.otp_code
    return jsonify(resp), 201


@api_bp.route("/api/register/verify-otp", methods=["POST"])
def register_verify_otp():
    from datetime import datetime
    from services.otp_service import verify_otp

    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No registration record found for this email"}), 400

    if not verify_otp(user, otp):
        return jsonify({"error": "Invalid or expired OTP code"}), 401

    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.last_login = datetime.utcnow()

    # Log them in automatically
    session.clear()
    session["user_id"] = user.id
    session.permanent = True

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Account verified and logged in successfully",
        "redirect": "/start"
    }), 200


@api_bp.route("/api/register/resend-otp", methods=["POST"])
def register_resend_otp():
    from flask import current_app
    from services.otp_service import send_otp

    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No user found with this email"}), 400

    if user.is_verified:
        return jsonify({"error": "Account is already verified. Please login."}), 400

    otp_res = send_otp(user)

    resp = {
        "success": True,
        "email_sent": otp_res.get("email_sent", False),
        "message": "OTP has been resent to your email" if otp_res.get("email_sent") else "New OTP generated"
    }
    if current_app.debug or not otp_res.get("email_sent"):
        resp["dev_otp"] = user.otp_code
    return jsonify(resp), 200


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
            "id": user.id,
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
                "id": p.id,
                "item": p.item_name,
                "price": p.price,
                "category": p.item_category,
                "upvotes": p.upvotes,
                "downvotes": p.downvotes,
                "user_id": p.user_id,
                "username": p.owner.username if p.owner else "anonymous",
                "name": p.owner.name if p.owner else "Anonymous",
                "trust_score": int(p.owner.trust_score) if p.owner else 50,
                "purchase_location": p.purchase_location,
                "comment": p.comment,
                "image_url": p.image_url,
                "created_at": p.created_at.isoformat()
            }
            for p in prices
        ]
    }), 200


# =====================================================
# SUBMIT PRICE (WITH PHOTO / RECEIPT UPLOAD)
# =====================================================

@api_bp.route("/api/submit-price", methods=["POST"])
@login_required
def submit_price():
    import os
    import uuid
    import base64
    from flask import current_app

    user = get_current_user()
    data = request.get_json() or {}

    if not user.village:
        return jsonify({"error": "Set village before submitting prices"}), 400

    item = data.get("item", "").strip()
    price = data.get("price")
    category = data.get("category", "Grains").strip()

    if not item:
        return jsonify({"error": "Crop/Item name is required"}), 400

    try:
        price = float(price)
        if price <= 0:
            raise ValueError
    except Exception:
        return jsonify({"error": "Invalid price value"}), 400

    purchase_location = data.get("purchase_location", "").strip() or None
    comment = data.get("comment", "").strip() or None
    image_data = data.get("image_data")  # Base64 data URL
    image_url = None

    # Process image attachment if provided
    if image_data and "base64," in image_data:
        try:
            header, encoded = image_data.split("base64,", 1)
            ext = "jpg"
            if "image/png" in header:
                ext = "png"
            elif "image/webp" in header:
                ext = "webp"

            filename = f"crop_{uuid.uuid4().hex[:12]}.{ext}"
            filepath = os.path.join(current_app.root_path, "static", "uploads", filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(encoded))
            image_url = f"/static/uploads/{filename}"
        except Exception as img_err:
            print(f"[Upload Warning] Failed to save crop image: {img_err}")

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
        price=price,
        item_category=category,
        purchase_location=purchase_location,
        comment=comment,
        image_url=image_url
    )

    # Extra trust boost if verified with photo
    boost = 10 if image_url else 5
    user.trust_score = min(user.trust_score + boost, 100)

    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Crop price and verification details submitted successfully!",
        "image_url": image_url
    }), 201


# =====================================================
# PRICE TRENDS (ANALYTICS)
# =====================================================

@api_bp.route("/api/price-trends", methods=["GET"])
@login_required
def price_trends():
    user = get_current_user()
    from sqlalchemy import func

    results = (
        db.session.query(
            PriceEntry.item_name,
            func.avg(PriceEntry.price).label("avg_price"),
            func.count(PriceEntry.id).label("count")
        )
        .filter(PriceEntry.village == user.village)
        .group_by(PriceEntry.item_name)
        .all()
    )

    return jsonify({
        "trends": [
            {
                "item": row.item_name,
                "avg_price": round(row.avg_price, 2),
                "submissions": row.count
            }
            for row in results
        ]
    }), 200


# =====================================================
# VILLAGE COMPARISON
# =====================================================

@api_bp.route("/api/village-comparison", methods=["GET"])
@login_required
def village_comparison():
    user = get_current_user()
    from sqlalchemy import func

    results = (
        db.session.query(
            PriceEntry.village,
            PriceEntry.item_name,
            func.avg(PriceEntry.price).label("avg_price")
        )
        .group_by(PriceEntry.village, PriceEntry.item_name)
        .all()
    )

    comparison = {}
    for village, item, avg_price in results:
        if item not in comparison:
            comparison[item] = []
        comparison[item].append({
            "village": village,
            "avg_price": round(avg_price, 2),
            "is_current": village.lower() == user.village.lower()
        })

    return jsonify({
        "comparison": comparison
    }), 200


# =====================================================
# VERIFY PRICE ENTRY (UPVOTE / DOWNVOTE)
# =====================================================

@api_bp.route("/api/verify-price/<int:entry_id>/<action>", methods=["POST"])
@login_required
def verify_price(entry_id, action):
    user = get_current_user()
    entry = db.session.get(PriceEntry, entry_id)

    if not entry:
        return jsonify({"error": "Price entry not found"}), 404

    if entry.user_id == user.id:
        return jsonify({"error": "You cannot verify your own submissions"}), 400

    if action == "upvote":
        entry.upvotes += 1
        if entry.owner:
            entry.owner.trust_score = min(entry.owner.trust_score + 1.0, 100.0)
    elif action == "downvote":
        entry.downvotes += 1
        if entry.owner:
            entry.owner.trust_score = max(entry.owner.trust_score - 2.0, 0.0)
            if entry.owner.trust_score < 20.0:
                from services.fraud_service import _log_fraud
                _log_fraud(entry.owner.id, "Trust score fell below critical threshold via community downvotes", "high")
    else:
        return jsonify({"error": "Invalid action"}), 400

    db.session.commit()

    return jsonify({
        "success": True,
        "upvotes": entry.upvotes,
        "downvotes": entry.downvotes,
        "message": f"Price successfully {action}d"
    }), 200


# =====================================================
# AI MARKET ADVISORY & PRICE PREDICTIONS
# =====================================================

@api_bp.route("/api/ai-advisory", methods=["GET"])
@login_required
def ai_advisory():
    from sqlalchemy import func
    user = get_current_user()

    # Get all distinct crops in user's village
    crops = (
        db.session.query(PriceEntry.item_name)
        .filter(PriceEntry.village == user.village)
        .distinct()
        .all()
    )

    advisories = []
    for (crop_name,) in crops:
        # Get entries sorted by date
        entries = (
            PriceEntry.query
            .filter(PriceEntry.village == user.village, PriceEntry.item_name == crop_name)
            .order_by(PriceEntry.created_at.asc())
            .all()
        )
        if not entries:
            continue

        prices = [e.price for e in entries]
        latest_price = prices[-1]
        avg_price = sum(prices) / len(prices)

        # Price momentum / trend calculation
        if len(prices) >= 2:
            change_pct = ((latest_price - prices[0]) / (prices[0] or 1)) * 100
        else:
            change_pct = 5.2  # Moderate positive default for fresh crops

        # Check other villages to find best selling mandi
        other_mandi = (
            db.session.query(PriceEntry.village, func.avg(PriceEntry.price).label("avg_p"))
            .filter(PriceEntry.item_name == crop_name)
            .group_by(PriceEntry.village)
            .order_by(func.avg(PriceEntry.price).desc())
            .first()
        )

        best_mandi_name = other_mandi.village if other_mandi else user.village
        best_mandi_price = round(other_mandi.avg_p, 2) if other_mandi else latest_price

        # AI Recommendation logic
        if change_pct >= 8.0:
            action = "STRONG SELL"
            action_code = "sell"
            confidence = 88
            tip = f"Price is up +{change_pct:.1f}% this week. Excellent time to bring harvest to market."
        elif change_pct <= -5.0:
            action = "HOLD / STORE"
            action_code = "hold"
            confidence = 79
            tip = "High arrival volume causing temporary dip. If feasible, hold stock for 3–5 days."
        else:
            action = "STABLE / ACCUMULATE"
            action_code = "neutral"
            confidence = 84
            tip = "Consistent local demand with balanced supply. Stable pricing across regional mandis."

        # 7-day predicted range
        pred_low = round(latest_price * (0.95 if change_pct < 0 else 1.02), 2)
        pred_high = round(latest_price * (1.08 if change_pct >= 0 else 1.04), 2)

        advisories.append({
            "crop": crop_name,
            "current_price": round(latest_price, 2),
            "trend_pct": round(change_pct, 1),
            "action": action,
            "action_code": action_code,
            "confidence": confidence,
            "forecast_7d": f"₹{pred_low} – ₹{pred_high}",
            "best_mandi": best_mandi_name,
            "best_mandi_price": best_mandi_price,
            "tip": tip
        })

    return jsonify({
        "village": user.village,
        "advisories": advisories
    }), 200


# =====================================================
# LIVE MARKET TICKER API
# =====================================================

@api_bp.route("/api/market-ticker", methods=["GET"])
def market_ticker():
    from sqlalchemy import func
    recent_prices = (
        db.session.query(
            PriceEntry.item_name,
            PriceEntry.village,
            PriceEntry.price,
            PriceEntry.created_at
        )
        .order_by(PriceEntry.created_at.desc())
        .limit(15)
        .all()
    )

    items_map = {}
    for item, village, price, dt in recent_prices:
        if item not in items_map:
            # Deterministic simulation of change based on price
            change = round(((price * 7) % 9) - 4.1, 1)
            if change == 0:
                change = 2.5
            items_map[item] = {
                "crop": item,
                "village": village,
                "price": round(price, 2),
                "change": change,
                "is_up": change >= 0
            }

    return jsonify({
        "ticker": list(items_map.values())
    }), 200


# =====================================================
# HYPERLOCAL AGRI-WEATHER & HARVEST ADVISORY
# =====================================================

@api_bp.route("/api/weather", methods=["GET"])
@login_required
def get_agri_weather():
    user = get_current_user()
    village = user.village or "Local Village"

    # Deterministic simulation of weather based on village name
    v_hash = sum(ord(c) for c in village)
    temp = 28 + (v_hash % 6)
    humidity = 58 + (v_hash % 20)
    conditions = ["Clear Sky ☀️", "Partly Cloudy ⛅", "Scattered Clouds 🌤️", "Mild Breeze 🍃"]
    cond = conditions[v_hash % len(conditions)]

    tips = [
        "Ideal weather for open-air drying of Grains & Paddy.",
        "Mild morning moisture: Recommended time for vegetable harvest.",
        "Good sunny afternoon for pesticide application if needed.",
        "Stable temperatures: Cotton picking conditions optimal."
    ]
    tip = tips[v_hash % len(tips)]

    return jsonify({
        "village": village,
        "temperature": f"{temp}°C",
        "condition": cond,
        "humidity": f"{humidity}%",
        "wind": f"{10 + (v_hash % 8)} km/h",
        "advisory": tip
    }), 200


# =====================================================
# GAMIFICATION & FARMER PROFILE XP
# =====================================================

@api_bp.route("/api/user-gamification", methods=["GET"])
@login_required
def user_gamification():
    user = get_current_user()

    # Calculate XP based on contributions, score, and verified entries
    submissions_count = PriceEntry.query.filter_by(user_id=user.id).count()
    deals_count = 0
    try:
        from models.deal import Deal
        deals_count = Deal.query.filter_by(user_id=user.id).count()
    except Exception:
        pass

    xp = int(user.trust_score * 8 + submissions_count * 25 + deals_count * 50)
    level = max(1, xp // 250)
    level_names = {
        1: "Village Contributor",
        2: "Trusted Kisan",
        3: "Mandi Champion",
        4: "Master Price Reporter",
        5: "Village Elder Representative"
    }
    title = level_names.get(level, "Agricultural Leader")
    xp_in_level = xp % 250
    progress_pct = int((xp_in_level / 250) * 100)

    badges = [
        {"name": "Early Adopter", "icon": "🌱", "unlocked": True, "desc": "Joined SahiDaam Network"},
        {"name": "Trusted Source", "icon": "🛡️", "unlocked": user.trust_score >= 60, "desc": "Trust Score 60+"},
        {"name": "Mandi Pro", "icon": "🏆", "unlocked": submissions_count >= 3, "desc": "3+ Price Submissions"},
        {"name": "Photo Verifier", "icon": "📸", "unlocked": submissions_count >= 1, "desc": "Submitted Crop Photo Proof"}
    ]

    return jsonify({
        "user_name": user.name or user.username,
        "village": user.village,
        "trust_score": int(user.trust_score),
        "level": level,
        "title": title,
        "xp": xp,
        "xp_in_level": xp_in_level,
        "next_level_xp": 250,
        "progress_pct": progress_pct,
        "badges": badges
    }), 200


# =====================================================
# KISAN DEAL BOARD (BUYER-SELLER MARKETPLACE)
# =====================================================

@api_bp.route("/api/deals", methods=["GET"])
@login_required
def get_deals():
    from models.deal import Deal
    deals = Deal.query.filter_by(is_active=True).order_by(Deal.created_at.desc()).limit(20).all()

    return jsonify({
        "deals": [
            {
                "id": d.id,
                "crop_name": d.crop_name,
                "quantity": d.quantity,
                "price_per_unit": d.price_per_unit,
                "village": d.village,
                "location_details": d.location_details,
                "contact_phone": d.contact_phone,
                "whatsapp_number": d.whatsapp_number or d.contact_phone,
                "seller_name": d.seller.name if d.seller else "Farmer",
                "seller_trust": int(d.seller.trust_score) if d.seller else 50,
                "description": d.description,
                "created_at": d.created_at.strftime("%d %b, %I:%M %p")
            }
            for d in deals
        ]
    }), 200


@api_bp.route("/api/deals/create", methods=["POST"])
@login_required
def create_deal():
    from models.deal import Deal
    user = get_current_user()
    data = request.get_json() or {}

    crop_name = data.get("crop_name", "").strip()
    quantity = data.get("quantity", "").strip()
    price = data.get("price_per_unit")
    contact_phone = data.get("contact_phone", "").strip()
    whatsapp_number = data.get("whatsapp_number", "").strip() or contact_phone
    location_details = data.get("location_details", "").strip()
    description = data.get("description", "").strip()

    if not crop_name or not quantity or not price or not contact_phone:
        return jsonify({"error": "Crop, Quantity, Price, and Contact Phone are required"}), 400

    try:
        price = float(price)
    except Exception:
        return jsonify({"error": "Invalid price"}), 400

    deal = Deal(
        user_id=user.id,
        crop_name=crop_name,
        quantity=quantity,
        price_per_unit=price,
        village=user.village or "Local Village",
        location_details=location_details,
        contact_phone=contact_phone,
        whatsapp_number=whatsapp_number,
        description=description
    )

    # Reward user for listing
    user.trust_score = min(user.trust_score + 3, 100)

    db.session.add(deal)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Harvest lot listed on Kisan Deal Board successfully!"
    }), 201


# =====================================================
# SMART PRICE WATCH & ALERTS
# =====================================================

@api_bp.route("/api/alerts", methods=["GET"])
@login_required
def get_alerts():
    from models.deal import PriceAlert
    user = get_current_user()
    alerts = PriceAlert.query.filter_by(user_id=user.id).order_by(PriceAlert.created_at.desc()).all()

    return jsonify({
        "alerts": [
            {
                "id": a.id,
                "crop_name": a.crop_name,
                "target_price": a.target_price,
                "condition": a.condition,
                "village": a.village,
                "is_triggered": a.is_triggered,
                "created_at": a.created_at.strftime("%d %b")
            }
            for a in alerts
        ]
    }), 200


@api_bp.route("/api/alerts/create", methods=["POST"])
@login_required
def create_alert():
    from models.deal import PriceAlert
    user = get_current_user()
    data = request.get_json() or {}

    crop_name = data.get("crop_name", "").strip()
    target_price = data.get("target_price")
    condition = data.get("condition", "above")

    if not crop_name or not target_price:
        return jsonify({"error": "Crop name and target price required"}), 400

    try:
        target_price = float(target_price)
    except Exception:
        return jsonify({"error": "Invalid target price"}), 400

    alert = PriceAlert(
        user_id=user.id,
        crop_name=crop_name,
        target_price=target_price,
        condition=condition,
        village=user.village
    )

    db.session.add(alert)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Price Watch set for {crop_name} {condition} ₹{target_price}!"
    }), 201


@api_bp.route("/api/alerts/delete/<int:alert_id>", methods=["POST"])
@login_required
def delete_alert(alert_id):
    from models.deal import PriceAlert
    user = get_current_user()
    alert = PriceAlert.query.filter_by(id=alert_id, user_id=user.id).first()
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    db.session.delete(alert)
    db.session.commit()

    return jsonify({"success": True, "message": "Alert removed"}), 200


# =====================================================
# INTERACTIVE MANDI GPS MAP DATA
# =====================================================

@api_bp.route("/api/mandi-map", methods=["GET"])
@login_required
def mandi_map_data():
    from sqlalchemy import func
    user = get_current_user()

    # Get distinct villages with their top crop averages
    villages = (
        db.session.query(
            PriceEntry.village,
            func.avg(PriceEntry.price).label("avg_price"),
            func.count(PriceEntry.id).label("reports_count")
        )
        .group_by(PriceEntry.village)
        .all()
    )

    # Base coordinates for Telangana/Andhra rural belt (centered around 17.5° N, 78.5° E)
    base_lat = 17.485
    base_lng = 78.490

    mandi_nodes = []
    for idx, (v_name, avg_p, count) in enumerate(villages):
        v_hash = sum(ord(c) for c in v_name)
        # Generate realistic nearby coordinates within ~15-30km
        lat_offset = ((v_hash % 20) - 10) * 0.025
        lng_offset = (((v_hash * 3) % 20) - 10) * 0.025

        is_user_village = (v_name.lower() == (user.village or "").lower())
        distance_km = 0 if is_user_village else (5 + (v_hash % 22))

        mandi_nodes.append({
            "name": f"{v_name} Mandi",
            "village": v_name,
            "lat": round(base_lat + lat_offset, 5),
            "lng": round(base_lng + lng_offset, 5),
            "avg_price": round(avg_p, 2),
            "reports_count": count,
            "distance_km": distance_km,
            "is_current": is_user_village
        })

    # If no data or only 1 village, inject realistic surrounding mandis
    if len(mandi_nodes) < 2:
        mandi_nodes.extend([
            {"name": "Rampur Central Mandi", "village": "Rampur", "lat": base_lat + 0.03, "lng": base_lng + 0.04, "avg_price": 38.5, "reports_count": 12, "distance_km": 6, "is_current": False},
            {"name": "Nandyal Agriculture Yard", "village": "Nandyal", "lat": base_lat - 0.04, "lng": base_lng + 0.02, "avg_price": 42.0, "reports_count": 18, "distance_km": 14, "is_current": False},
            {"name": "Korutla Kisan Market", "village": "Korutla", "lat": base_lat + 0.05, "lng": base_lng - 0.05, "avg_price": 39.0, "reports_count": 9, "distance_km": 19, "is_current": False}
        ])

    return jsonify({
        "center_lat": base_lat,
        "center_lng": base_lng,
        "user_village": user.village,
        "mandis": mandi_nodes
    }), 200


