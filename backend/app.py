"""
NoteVault Backend — Flask + MongoDB
Entry point
"""

from flask import Flask
from flask_cors import CORS
from config.db import init_db
from routes.auth import auth_bp
from routes.subjects import subjects_bp
from routes.chapters import chapters_bp
from routes.notes import notes_bp
from routes.dashboard import dashboard_bp
import os

def create_app():
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config["SECRET_KEY"]           = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    app.config["JWT_EXPIRY_HOURS"]     = int(os.getenv("JWT_EXPIRY_HOURS", 24))
    app.config["MONGO_URI"]            = os.getenv("MONGO_URI", "mongodb://localhost:27017/notvault")

    # ── CORS ───────────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

    # ── Database ───────────────────────────────────────────────────────────────
    init_db(app)

    # ── Blueprints ─────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(subjects_bp,  url_prefix="/api/subjects")
    app.register_blueprint(chapters_bp,  url_prefix="/api/chapters")
    app.register_blueprint(notes_bp,     url_prefix="/api/notes")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # ── Health check ───────────────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return {"status": "ok", "app": "NoteVault API", "version": "1.0.0"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    port  = int(os.getenv("PORT", 5000))
    print(f"\n🚀  NoteVault API running on http://localhost:{port}\n")
    app.run(debug=debug, port=port)
