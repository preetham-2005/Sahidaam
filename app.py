import os
from flask import Flask, render_template, jsonify, request
from flask_session import Session
from sqlalchemy import text
from extensions import db, mail, jwt
from config import Config


def create_app():
    app = Flask(__name__)

    # =========================
    # LOAD CONFIG
    # =========================
    app.config.from_object(Config)

    # Ensure uploads directory exists
    uploads_dir = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # =========================
    # INIT EXTENSIONS
    # =========================
    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    Session(app)

    # =========================
    # SECURITY HEADERS MIDDLEWARE
    # =========================
    @app.after_request
    def set_security_headers(response):
        # Prevent Clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Cross-Site Scripting filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Hardware Feature Policy
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(self)"
        return response

    # =========================
    # SAFE GLOBAL ERROR HANDLERS
    # =========================
    @app.errorhandler(413)
    def request_entity_too_large(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Payload too large. Max file upload size is 16MB."}), 413
        return render_template("index.html"), 413

    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Requested resource was not found."}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "An internal server error occurred. Please try again later."}), 500
        return render_template("index.html"), 500

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
    from routes.dashboard_routes import dashboard_bp
    from helpers.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    # =========================
    # DB INIT & SAFE MIGRATIONS
    # =========================
    with app.app_context():
        db.create_all()
        # Safe migration check for new image_url column in price_entry
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE price_entry ADD COLUMN image_url VARCHAR(255)"))
                conn.commit()
        except Exception:
            pass  # Column already exists

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
