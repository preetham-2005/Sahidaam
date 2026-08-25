import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # =========================
    # CORE SECURITY
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "sahidaam-dev-secret-key-2026")

    # =========================
    # DATABASE
    # =========================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'sahidaam.db')}"
    ).replace("postgres://", "postgresql://")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # =========================
    # SESSION & SECURITY
    # =========================
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    
    # 16 MB max content length to mitigate payload flooding DoS
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # =========================
    # EMAIL (OTP / VERIFICATION)
    # =========================
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ["true", "1", "yes"]

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME or "noreply@sahidaam.com")

    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

    # =========================
    # GOOGLE AUTH (OAUTH / GSI)
    # =========================
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # =========================
    # OTP SETTINGS
    # =========================
    OTP_EXPIRY_MINUTES = 10

    # =========================
    # JWT (MOBILE)
    # =========================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # =========================
    # ENVIRONMENT
    # =========================
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development" or os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]
