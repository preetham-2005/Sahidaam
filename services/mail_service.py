from flask_mail import Message
from flask import current_app

def send_verification_email(mail, user, token):
    msg = Message(
        subject="Verify your SahiDaam account",
        recipients=[user.email],
        html=f"""
        <h2>Welcome to SahiDaam</h2>
        <p>Click to verify:</p>
        <a href="{current_app.config['BASE_URL']}/verify-email/{token}">
            Verify Email
        </a>
        """
    )
    mail.send(msg)
