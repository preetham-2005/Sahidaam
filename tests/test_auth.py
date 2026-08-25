import requests

BASE_URL = "http://127.0.0.1:5000"

def test_all():
    session = requests.Session()

    print("\n--- 1. Testing Google Auth (Continue with Google) ---")
    res = session.post(f"{BASE_URL}/api/auth/google", json={
        "email": "kisan.google.test@gmail.com",
        "name": "Kisan Google User"
    })
    print(f"Google Auth Status: {res.status_code}, Response: {res.json()}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.json().get("success") is True

    print("\n--- 2. Testing Set Village for Google User ---")
    res_village = session.post(f"{BASE_URL}/api/set-village", json={
        "village": "Rampur",
        "state": "Telangana"
    })
    print(f"Set Village Status: {res_village.status_code}, Response: {res_village.json()}")
    assert res_village.status_code == 200

    print("\n--- 3. Testing Price Submission by Google User ---")
    res_price = session.post(f"{BASE_URL}/api/submit-price", json={
        "item": "Rice",
        "price": 38.5,
        "category": "Grains",
        "purchase_location": "Rampur Mandi",
        "comment": "Fresh Sona Masoori harvest"
    })
    print(f"Submit Price Status: {res_price.status_code}, Response: {res_price.json()}")
    assert res_price.status_code == 201

    import time
    ts = int(time.time())
    test_user = f"farmer_{ts}"
    test_email = f"farmer_{ts}@gmail.com"

    print("\n--- 4. Testing Registration with OTP ---")
    reg_session = requests.Session()
    res_reg = reg_session.post(f"{BASE_URL}/api/register", json={
        "name": "New Farmer",
        "username": test_user,
        "email": test_email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    print(f"Register Status: {res_reg.status_code}, Response: {res_reg.json()}")
    assert res_reg.status_code in [200, 201]
    otp = res_reg.json().get("dev_otp")
    assert otp is not None, "Expected OTP code in response"
    print(f"Received OTP: {otp}")

    print("\n--- 5. Testing Verify Registration OTP ---")
    res_ver = reg_session.post(f"{BASE_URL}/api/register/verify-otp", json={
        "email": test_email,
        "otp": otp
    })
    print(f"Verify OTP Status: {res_ver.status_code}, Response: {res_ver.json()}")
    assert res_ver.status_code == 200
    assert res_ver.json().get("success") is True

    print("\n--- 6. Testing Email OTP Login ---")
    login_session = requests.Session()
    res_otp_req = login_session.post(f"{BASE_URL}/api/login/email", json={
        "email": test_email
    })
    print(f"Email Login Request Status: {res_otp_req.status_code}, Response: {res_otp_req.json()}")
    assert res_otp_req.status_code == 200
    login_otp = res_otp_req.json().get("dev_otp")
    print(f"Received Login OTP: {login_otp}")

    res_otp_ver = login_session.post(f"{BASE_URL}/api/login/email/verify", json={
        "email": test_email,
        "otp": login_otp
    })
    print(f"Email Login Verify Status: {res_otp_ver.status_code}, Response: {res_otp_ver.json()}")
    assert res_otp_ver.status_code == 200
    assert res_otp_ver.json().get("success") is True

    print("\n--- 7. Testing Standard Password Login ---")
    pw_session = requests.Session()
    res_pw = pw_session.post(f"{BASE_URL}/api/login", json={
        "username": test_user,
        "password": "Password123!"
    })
    print(f"Password Login Status: {res_pw.status_code}, Response: {res_pw.json()}")
    assert res_pw.status_code == 200
    assert res_pw.json().get("success") is True

    print("\n[SUCCESS] ALL AUTHENTICATION AND GOOGLE LOGIN TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all()
