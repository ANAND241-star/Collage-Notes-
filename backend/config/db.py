"""
config/db.py — MongoDB connection via PyMongo
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure
import os

# Global db reference used across the app
mongo_client = None
db = None


def init_db(app):
    """Connect to MongoDB and attach `db` to the app + global scope."""
    global mongo_client, db

    uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/notvault")

    try:
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        mongo_client.admin.command("ping")
        db_name = uri.split("/")[-1].split("?")[0] or "notvault"
        db = mongo_client[db_name]
        app.db = db
        _create_indexes()
        print(f"✅  MongoDB connected → {db_name}")
    except ConnectionFailure as e:
        print(f"❌  MongoDB connection failed: {e}")
        raise


def _create_indexes():
    """Create all indexes for performance + uniqueness constraints."""
    # Users
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)

    # Subjects
    db.subjects.create_index([("user_id", ASCENDING)])
    db.subjects.create_index([("user_id", ASCENDING), ("name", ASCENDING)], unique=True)

    # Chapters
    db.chapters.create_index([("subject_id", ASCENDING)])
    db.chapters.create_index([("subject_id", ASCENDING), ("name", ASCENDING)], unique=True)

    # Notes — text index for full-text search
    db.notes.create_index([("chapter_id", ASCENDING)])
    db.notes.create_index([("user_id", ASCENDING)])
    db.notes.create_index([("modified", DESCENDING)])
    db.notes.create_index([
        ("title", TEXT),
        ("content", TEXT),
        ("tags", TEXT)
    ], name="notes_text_search")

    # Activity
    db.activity.create_index([("user_id", ASCENDING), ("date", ASCENDING)], unique=True)

    print("✅  MongoDB indexes created")


def get_db():
    """Return the active db instance."""
    return db
