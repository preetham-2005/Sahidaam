import random
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app
from extensions import mail, db


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(user):
    """
    Generates OTP, saves it to DB, and attempts to send email via SMTP.
    Returns a dict with delivery status and OTP.
    """
    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=10)

    # Save OTP to database
    user.otp_code = otp
    user.otp_expiry = expiry
    db.session.commit()

    email_sent = False
    error_msg = None

    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")

    # Send email if SMTP is configured
    if mail_username and mail_password:
        try:
            sender = current_app.config.get("MAIL_DEFAULT_SENDER") or mail_username
            msg = Message(
                subject="🌾 Your SahiDaam OTP Verification Code",
                sender=sender,
                recipients=[user.email],
                html=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0c1120; color: #f0f4f8; margin: 0; padding: 20px; }}
                        .container {{ max-width: 520px; margin: 0 auto; background-color: #111827; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); padding: 32px; }}
                        .header {{ text-align: center; margin-bottom: 24px; }}
                        .logo {{ font-size: 32px; font-weight: bold; color: #00c896; }}
                        .badge {{ display: inline-block; background: rgba(0, 200, 150, 0.15); color: #00f5b4; padding: 6px 14px; border-radius: 50px; font-size: 13px; font-weight: 600; margin-top: 8px; }}
                        .otp-box {{ background: #1a2235; border: 2px dashed #00c896; border-radius: 12px; text-align: center; padding: 20px; margin: 24px 0; }}
                        .otp-code {{ font-size: 38px; font-weight: 800; letter-spacing: 8px; color: #00f5b4; margin: 0; font-family: monospace; }}
                        .info {{ color: #94a3b8; font-size: 14px; line-height: 1.6; margin: 12px 0; }}
                        .footer {{ text-align: center; margin-top: 32px; font-size: 12px; color: #64748b; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 16px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🌾 SahiDaam</div>
                            <div class="badge">Village Market Intelligence</div>
                        </div>
                        <p style="font-size: 16px;">Hello <strong>{user.name or user.username}</strong>,</p>
                        <p class="info">Use the verification code below to complete your SahiDaam login or registration:</p>
                        
                        <div class="otp-box">
                            <p class="otp-code">{otp}</p>
                        </div>
                        
                        <p class="info">⏳ This OTP code is valid for <strong>10 minutes</strong>. Never share this code with anyone.</p>
                        <p class="info">If you did not request this OTP, you can safely ignore this email.</p>
                        
                        <div class="footer">
                            © 2026 SahiDaam · Empowering Rural Bharat with Transparent Market Data
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            mail.send(msg)
            email_sent = True
            print(f"[SMTP Success] Verification OTP successfully sent to {user.email}")
        except Exception as e:
            error_msg = str(e)
            print(f"[SMTP Error] Could not send email to {user.email}: {e}")
    else:
        error_msg = "SMTP not configured (MAIL_USERNAME/MAIL_PASSWORD not set in environment or .env)"
        print(f"[SMTP Notice] Development OTP for {user.email} is: {otp}")

    return {
        "success": True,
        "email_sent": email_sent,
        "otp": otp,
        "error": error_msg
    }


def verify_otp(user, otp):
    """
    Verifies OTP validity
    """
    if not user.otp_code or not user.otp_expiry:
        return False

    if datetime.utcnow() > user.otp_expiry:
        return False

    if user.otp_code.strip() != otp.strip():
        return False

    # Clear OTP after successful verification
    user.otp_code = None
    user.otp_expiry = None
    db.session.commit()

    return True
