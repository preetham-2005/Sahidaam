# models/user.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    # =========================
    # CORE IDENTITY
    # =========================
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(120))

    village = db.Column(db.String(120))
    state = db.Column(db.String(120))

    # =========================
    # TRUST / GAMIFICATION
    # =========================
    trust_score = db.Column(db.Float, default=50.0)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)

    # =========================
    # ADMIN & SECURITY
    # =========================
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

    # =========================
    # OTP AUTH
    # =========================
    otp_code = db.Column(db.String(10))
    otp_expiry = db.Column(db.DateTime, index=True)

    # =========================
    # METADATA
    # =========================
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_login_source = db.Column(db.String(20))  # web / mobile / admin

    # =========================
    # RELATIONSHIPS (✅ FIXED)
    # =========================
    price_entries = db.relationship(
        "PriceEntry",
        backref="owner",     # ✅ NOT "user"
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    # =========================
    # PASSWORD METHODS
    # =========================
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # =========================
    # OTP METHODS
    # =========================
    def clear_otp(self):
        self.otp_code = None
        self.otp_expiry = None

    def is_otp_valid(self, otp: str) -> bool:
        return (
            self.otp_code == otp
            and self.otp_expiry
            and self.otp_expiry > datetime.utcnow()
        )

    def __repr__(self):
        return f"<User {self.username}>"
