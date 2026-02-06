import os
from datetime import timedelta

class Config:
    # =========================
    # CORE SECURITY
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "sahidaam-dev-secret")

    # =========================
    # DATABASE
    # =========================
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///sahidaam.db"
    ).replace("postgres://", "postgresql://")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # =========================
    # SESSION (WEB)
    # =========================
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"

    # =========================
    # EMAIL (OTP / VERIFICATION)
    # =========================
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

    # =========================
    # OTP
    # =========================
    OTP_EXPIRY_MINUTES = 10

    # =========================
    # JWT (MOBILE)
    # =========================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # =========================
    # ENV
    # =========================
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"
