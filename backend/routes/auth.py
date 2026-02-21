"""
routes/auth.py — User Authentication
  POST /api/auth/signup   → Register new user
  POST /api/auth/login    → Login, get JWT token
  GET  /api/auth/me       → Get current user profile (protected)
  PUT  /api/auth/me       → Update profile (protected)
  POST /api/auth/logout   → Logout (client-side token drop, acknowledged here)
"""

from flask import Blueprint, request, jsonify, current_app, g
from pymongo.errors import DuplicateKeyError
from models.user import (
    new_user_doc, verify_password, generate_token, serialize_user
)
from middleware.auth import token_required
from config.db import get_db

auth_bp = Blueprint("auth", __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_signup(data: dict):
    errors = []
    if not data.get("username") or len(data["username"].strip()) < 3:
        errors.append("Username must be at least 3 characters")
    if not data.get("email") or "@" not in data["email"]:
        errors.append("Valid email is required")
    if not data.get("password") or len(data["password"]) < 6:
        errors.append("Password must be at least 6 characters")
    return errors


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user account."""
    data = request.get_json(silent=True) or {}

    # Validate input
    errors = _validate_signup(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    db = get_db()
    try:
        doc    = new_user_doc(data["username"], data["email"], data["password"])
        result = db.users.insert_one(doc)
        user   = db.users.find_one({"_id": result.inserted_id})

        token = generate_token(
            str(result.inserted_id),
            current_app.config["SECRET_KEY"],
            current_app.config.get("JWT_EXPIRY_HOURS", 24),
        )

        return jsonify({
            "message": "Account created successfully! 🎉",
            "token":   token,
            "user":    serialize_user(user),
        }), 201

    except DuplicateKeyError as e:
        field = "email" if "email" in str(e) else "username"
        return jsonify({"error": f"That {field} is already registered"}), 409

    except Exception as e:
        return jsonify({"error": "Server error during signup", "detail": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return a JWT token."""
    data = request.get_json(silent=True) or {}

    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db   = get_db()
    user = db.users.find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(
        str(user["_id"]),
        current_app.config["SECRET_KEY"],
        current_app.config.get("JWT_EXPIRY_HOURS", 24),
    )

    return jsonify({
        "message": "Login successful! Welcome back 👋",
        "token":   token,
        "user":    serialize_user(user),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_profile():
    """Return the current authenticated user's profile."""
    return jsonify({"user": serialize_user(g.user)}), 200


@auth_bp.route("/me", methods=["PUT"])
@token_required
def update_profile():
    """Update the current user's username or avatar."""
    data = request.get_json(silent=True) or {}
    db   = get_db()

    updates = {}
    if "username" in data and len(data["username"].strip()) >= 3:
        updates["username"] = data["username"].strip()
    if "avatar" in data:
        updates["avatar"] = data["avatar"]

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    from datetime import datetime
    updates["updated_at"] = datetime.utcnow().isoformat()

    db.users.update_one({"_id": g.user["_id"]}, {"$set": updates})
    updated = db.users.find_one({"_id": g.user["_id"]})

    return jsonify({
        "message": "Profile updated!",
        "user": serialize_user(updated),
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    """
    Acknowledge logout. The client should discard the JWT token.
    (Stateless JWT — real blacklisting would require a token store.)
    """
    return jsonify({"message": "Logged out successfully. See you soon! 👋"}), 200
