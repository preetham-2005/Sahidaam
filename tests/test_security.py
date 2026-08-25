import requests

BASE_URL = "http://127.0.0.1:5000"

def test_security_suite():
    session = requests.Session()

    print("--- 1. Testing Security HTTP Headers ---")
    res = session.get(f"{BASE_URL}/")
    print(f"Status: {res.status_code}")
    print(f"X-Frame-Options: {res.headers.get('X-Frame-Options')}")
    print(f"X-Content-Type-Options: {res.headers.get('X-Content-Type-Options')}")
    print(f"X-XSS-Protection: {res.headers.get('X-XSS-Protection')}")
    print(f"Referrer-Policy: {res.headers.get('Referrer-Policy')}")
    print(f"Permissions-Policy: {res.headers.get('Permissions-Policy')}")

    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"

    print("\n--- 2. Testing Brute Force & Rate Limiter on Failed Logins ---")
    # Simulate 6 rapid wrong password attempts
    blocked = False
    for i in range(6):
        r = session.post(f"{BASE_URL}/api/login", json={
            "username": "nonexistent_hacker_test",
            "password": "wrong_password"
        })
        print(f"Attempt {i+1}: Status {r.status_code}, Response: {r.json().get('error')}")
        if r.status_code == 429:
            blocked = True
            break
    
    assert blocked, "Brute force rate limiter should block after 5 failed attempts with 429"
    print("[SUCCESS] Brute-force protection verified: Attacker blocked with HTTP 429!")

    print("\n--- 3. Testing Safe 404 Error Handler ---")
    res_404 = session.get(f"{BASE_URL}/api/non-existent-endpoint-12345")
    print(f"404 Status: {res_404.status_code}, JSON: {res_404.json()}")
    assert res_404.status_code == 404
    assert "error" in res_404.json()

    print("\n--- 4. Testing Google Auth & Clean Dashboard Access ---")
    res_auth = session.post(f"{BASE_URL}/api/auth/google", json={
        "email": "secure.farmer@gmail.com",
        "name": "Secure Farmer"
    })
    assert res_auth.status_code == 200
    print(f"Google Auth: {res_auth.status_code}")

    print("\n[SUCCESS] ALL ENTERPRISE SECURITY PROTECTIONS TESTED AND VERIFIED CLEANLY!")

if __name__ == "__main__":
    test_security_suite()
