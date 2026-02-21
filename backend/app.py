from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"]       = os.environ.get("SECRET_KEY", "change-me")
    app.config["JWT_EXPIRY_HOURS"] = int(os.environ.get("JWT_EXPIRY_HOURS", 24))
    app.config["MONGO_URI"]        = os.environ.get("MONGO_URI", "mongodb://localhost:27017/notvault")

    allowed = os.environ.get("ALLOWED_ORIGINS", "*")
    origins = [o.strip() for o in allowed.split(",")] if "," in allowed else allowed

    CORS(app, resources={r"/api/*": {
        "origins": origins,
        "methods": ["GET","POST","PUT","DELETE","OPTIONS"],
        "allow_headers": ["Content-Type","Authorization"]
    }})

    from config.db import init_db
    init_db(app)

    from routes.auth      import auth_bp
    from routes.subjects  import subjects_bp
    from routes.chapters  import chapters_bp
    from routes.notes     import notes_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(subjects_bp,  url_prefix="/api/subjects")
    app.register_blueprint(chapters_bp,  url_prefix="/api/chapters")
    app.register_blueprint(notes_bp,     url_prefix="/api/notes")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    @app.route("/")
    def root():
        return {"message": "NoteVault API is live 🚀", "status": "ok"}, 200

    @app.route("/api/health")
    def health():
        return {"status": "ok", "app": "NoteVault API", "version": "1.0.0"}, 200

    return app

# Vercel needs app at module level
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀  NoteVault API → http://localhost:{port}\n")
    app.run(debug=True, port=port)
