"""
models/user.py — User document helpers
"""

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from bson import ObjectId


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_token(user_id: str, secret: str, expiry_hours: int = 24) -> str:
    """Create a signed JWT for the given user_id."""
    payload = {
        "user_id": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def serialize_user(user: dict) -> dict:
    """Return a safe, serializable user dict (no password)."""
    return {
        "id":         str(user["_id"]),
        "username":   user.get("username", ""),
        "email":      user.get("email", ""),
        "created_at": user.get("created_at", ""),
        "avatar":     user.get("avatar", "🎓"),
    }


def new_user_doc(username: str, email: str, password: str) -> dict:
    """Build a new user document ready to insert into MongoDB."""
    return {
        "username":   username.strip(),
        "email":      email.strip().lower(),
        "password":   hash_password(password),
        "avatar":     "🎓",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
