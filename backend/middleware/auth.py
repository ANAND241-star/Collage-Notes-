"""
middleware/auth.py — JWT token verification middleware
"""

import jwt
import os
from functools import wraps
from flask import request, jsonify, current_app, g
from bson import ObjectId
from config.db import get_db


def token_required(f):
    """
    Decorator that protects routes with JWT authentication.
    Attaches the current user to Flask's `g.user` and `g.user_id`.

    Usage:
        @app.route("/api/some-route")
        @token_required
        def my_route():
            user = g.user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Accept token from Authorization header: "Bearer <token>"
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        # Also accept from query string (for convenience in dev)
        if not token:
            token = request.args.get("token")

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401

        try:
            secret = current_app.config["SECRET_KEY"]
            payload = jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired — please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        db = get_db()
        user = db.users.find_one({"_id": ObjectId(payload["user_id"])})
        if not user:
            return jsonify({"error": "User not found"}), 401

        # Attach to Flask globals for use in route handlers
        g.user    = user
        g.user_id = str(user["_id"])

        return f(*args, **kwargs)
    return decorated
