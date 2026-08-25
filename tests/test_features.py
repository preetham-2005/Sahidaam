import requests

BASE_URL = "http://127.0.0.1:5000"

def test_all_features():
    session = requests.Session()

    # 1. Login with Google
    res_auth = session.post(f"{BASE_URL}/api/auth/google", json={
        "email": "master.farmer@gmail.com",
        "name": "Master Kisan"
    })
    print(f"1. Google Auth Status: {res_auth.status_code}")
    assert res_auth.status_code == 200

    # 2. Set Village
    res_vil = session.post(f"{BASE_URL}/api/set-village", json={
        "village": "Rampur Central",
        "state": "Telangana"
    })
    print(f"2. Set Village Status: {res_vil.status_code}")
    assert res_vil.status_code == 200

    # 3. Test Live Ticker
    res_ticker = session.get(f"{BASE_URL}/api/market-ticker")
    print(f"3. Market Ticker: {res_ticker.status_code}, Items: {len(res_ticker.json().get('ticker', []))}")
    assert res_ticker.status_code == 200

    # 4. Test Weather
    res_weather = session.get(f"{BASE_URL}/api/weather")
    print(f"4. Agri-Weather: {res_weather.status_code}, Temp: {res_weather.json().get('temperature')}, Advisory: {res_weather.json().get('advisory')}")
    assert res_weather.status_code == 200

    # 5. Test Gamification
    res_game = session.get(f"{BASE_URL}/api/user-gamification")
    g = res_game.json()
    print(f"5. Gamification: {res_game.status_code}, Level: {g.get('level')} ({g.get('title')}), XP: {g.get('xp')}")
    assert res_game.status_code == 200

    # 6. Test Kisan Deal Board Create & List
    res_deal_create = session.post(f"{BASE_URL}/api/deals/create", json={
        "crop_name": "Sona Masoori Paddy",
        "quantity": "50 Bags (30 Quintals)",
        "price_per_unit": 2100.0,
        "contact_phone": "9876543210",
        "location_details": "Rampur Village Center"
    })
    print(f"6. Post Deal: {res_deal_create.status_code}, Response: {res_deal_create.json()}")
    assert res_deal_create.status_code == 201

    res_deals = session.get(f"{BASE_URL}/api/deals")
    deals = res_deals.json().get("deals", [])
    print(f"   Total Deals: {len(deals)}, First Deal: {deals[0]['crop_name']} @ {deals[0]['price_per_unit']}")
    assert len(deals) >= 1

    # 7. Test Mandi GPS Map Data
    res_map = session.get(f"{BASE_URL}/api/mandi-map")
    mandis = res_map.json().get("mandis", [])
    print(f"7. Mandi GPS Map: {res_map.status_code}, Total Nodes: {len(mandis)}")
    assert res_map.status_code == 200
    assert len(mandis) >= 1

    # 8. Test Smart Price Alerts
    res_alert_create = session.post(f"{BASE_URL}/api/alerts/create", json={
        "crop_name": "Tomato",
        "target_price": 32.0,
        "condition": "above"
    })
    print(f"8. Create Price Alert Status: {res_alert_create.status_code}")
    assert res_alert_create.status_code == 201

    res_alerts = session.get(f"{BASE_URL}/api/alerts")
    alerts = res_alerts.json().get("alerts", [])
    print(f"   Active Alerts: {len(alerts)}, Target: {alerts[0]['crop_name']} {alerts[0]['condition']} {alerts[0]['target_price']}")
    assert len(alerts) >= 1

    print("\n[SUCCESS] ALL 7 REAL-APPLICATION FEATURE SUITES TESTED AND VERIFIED CLEANLY!")

if __name__ == "__main__":
    test_all_features()
