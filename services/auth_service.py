from models.user import User
from extensions import db

def register_user(data):
    username = data["username"]
    email = data["email"]
    password = data["password"]

    if User.query.filter_by(username=username).first():
        raise ValueError("Username exists")

    if User.query.filter_by(email=email).first():
        raise ValueError("Email exists")

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return user
