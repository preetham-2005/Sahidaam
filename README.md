# 🌾 SahiDaam — Village Market Price Intelligence & Kisan Deal Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

> **SahiDaam (सहीदाम / సహీదాం)** is an open, crowdsourced agricultural intelligence and trading platform designed for Indian farmers, village panchayats, and rural buyers. It provides real-time mandi prices, AI-driven Sell/Hold forecasts, direct farmer-to-buyer deals over WhatsApp, and community verification.

---

## 🌟 Key Features

### 1. 🔴 Live Market Stock-Ticker
* Stock-exchange style continuous glowing marquee ticker displaying real-time crop movements, percentage shifts, and mandi open statuses.

### 2. 🤖 AI Market Advisory & 7-Day Price Forecast
* Analyzes local mandi momentum and recommends actionable strategies:
  * **📈 STRONG SELL** *(Surging prices — optimal time to bring harvest to market)*
  * **⏳ HOLD / STORE** *(Temporary dip due to arrival surges)*
  * **⚖️ STABLE / ACCUMULATE** *(Balanced local demand)*
* Displays 7-day expected price ceilings & floors and the highest-paying nearby mandi.

### 3. 🤝 Kisan Deal Board (Direct Buyer-Seller Marketplace)
* Allows farmers to list harvest lots directly without middlemen commissions.
* Includes 1-click **"💬 Chat on WhatsApp with Farmer"** and **"📞 Call Farmer"** actions.

### 4. 🗺️ Interactive Mandi GPS Map (Leaflet.js)
* Visual price heatmap of neighboring mandis within a 25km radius with driving distances and price pins.

### 5. 🌤️ Hyperlocal Agri-Weather & Sowing Tips
* Live village temperature, humidity, and wind conditions with crop drying and harvesting advice.

### 6. 🏅 Farmer Gamification (XP & Badges)
* Contributor level progression (`Level 1 Village Contributor` → `Level 5 Village Elder`) with unlockable badges (*🌱 Early Member, 🛡️ Trusted 75+, 🏆 Mandi Pro, 📸 Photo Verifier*).

### 7. 🎙️ Voice Input & Indic Multilingual Support
* Speech-to-Text parsing in **English, Hindi (हिन्दी), and Telugu (తెలుగు)** for hands-free crop price entry.
* Instant UI localization across all pages.

### 8. 📸 Crop Photo & Mandi Slip Upload
* Attachment of crop proof or physical receipts earning a **+10 Trust Score bonus** and a verified photo badge.

### 9. 📄 1-Click Printable Mandi Slip Generator
* Generates an official, printable daily mandi rate certificate with village yard headers and verification stamps.

### 10. 🛡️ Enterprise Security Suite
* HTTP Security Headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`).
* **Brute-Force Lockout Shield (HTTP 429)** blocking attackers after 5 failed login attempts.
* `HttpOnly` and `SameSite=Lax` cookie protections.
* 16MB content upload protection and safe UUID file hashing.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.11+, Flask, Flask-SQLAlchemy, Flask-Session, Flask-Mail
* **Database:** PostgreSQL (Production on Render) / SQLite (Local Development)
* **Frontend:** Vanilla HTML5, Modern CSS (Agri-Design Tokens), Vanilla JavaScript (ES6+)
* **Mapping & Analytics:** Leaflet.js, OpenStreetMap, Chart.js
* **Speech & AI:** Web Speech API, Heuristic Market Momentum AI Engine
* **Authentication:** Google Identity Services (GSI) / 1-Click Google Modal, Email OTP (Gmail SMTP), Password PBKDF2

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/preetham-2005/Sahidaam.git
cd Sahidaam
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```

### 5. Run the Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## 🧪 Running Automated Tests

```bash
# Test Auth & Google Login
python tests/test_auth.py

# Test All 7 Features (Ticker, Weather, Deals, Map, Alerts)
python tests/test_features.py

# Test Enterprise Security & Brute-Force Shield
python tests/test_security.py
```

---

## ☁️ Deployment on Render (1-Click)

The repository is pre-configured with `render.yaml` for zero-configuration deployment:

1. Push your code to your GitHub repository.
2. Log in to [Render](https://render.com/) and click **"New +" → "Blueprint"**.
3. Select this repository.
4. Render will automatically:
   - Provision a managed **PostgreSQL** database.
   - Install dependencies and start the **Gunicorn** production server.
5. In Render Dashboard settings, provide your optional `MAIL_USERNAME`, `MAIL_PASSWORD`, and `GOOGLE_CLIENT_ID`.

---

## 👥 Contributing & License

Contributions are welcome! Please feel free to submit a Pull Request.

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  🌾 <i>Empowering Indian Farmers & Rural Communities with Transparent Pricing Intelligence.</i>
</p>
