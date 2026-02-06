import random
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from extensions import mail, db


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(user):
    """
    Generates OTP, saves it to DB, and sends email
    """

    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=10)

    # Save OTP
    user.otp_code = otp
    user.otp_expiry = expiry
    db.session.commit()

    # Send email
    msg = Message(
        subject="Your SahiDaam OTP",
        recipients=[user.email],
        html=f"""
        <h2>🌾 SahiDaam Login OTP</h2>
        <p>Hello {user.name or user.username},</p>

        <p>Your One-Time Password is:</p>
        <h1 style="letter-spacing:4px;">{otp}</h1>

        <p>This OTP is valid for <b>10 minutes</b>.</p>
        <p>If you didn’t request this, ignore this email.</p>

        <br>
        <small>— SahiDaam Team</small>
        """
    )

    mail.send(msg)


def verify_otp(user, otp):
    """
    Verifies OTP validity
    """
    if not user.otp_code or not user.otp_expiry:
        return False

    if datetime.utcnow() > user.otp_expiry:
        return False

    if user.otp_code != otp:
        return False

    # Clear OTP after success
    user.otp_code = None
    user.otp_expiry = None
    db.session.commit()

    return True
