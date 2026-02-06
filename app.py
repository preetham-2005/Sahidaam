from flask import Flask, render_template
from flask_session import Session
from extensions import db
from config import Config


def create_app():
    app = Flask(__name__)

    # =========================
    # LOAD CONFIG
    # =========================
    app.config.from_object(Config)

    # =========================
    # INIT EXTENSIONS
    # =========================
    db.init_app(app)
    Session(app)

    # =========================
    # HOME ROUTE
    # =========================
    @app.route("/")
    def index():
        return render_template("index.html")

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    from routes.auth import auth_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # =========================
    # DB INIT
    # =========================
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
