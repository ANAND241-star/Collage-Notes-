"""
models/note.py — Document builders and serializers for
                  Subject, Chapter, and Note collections
"""

from datetime import datetime
from bson import ObjectId


# ── Serializers ───────────────────────────────────────────────────────────────

def serialize_id(doc: dict) -> dict:
    """Convert _id ObjectId → string 'id' field."""
    if doc and "_id" in doc:
        doc = dict(doc)
        doc["id"] = str(doc.pop("_id"))
        # Also stringify any ObjectId references
        for key in ("user_id", "subject_id", "chapter_id"):
            if key in doc and isinstance(doc[key], ObjectId):
                doc[key] = str(doc[key])
    return doc


def serialize_subject(doc: dict) -> dict:
    d = serialize_id(dict(doc))
    return d


def serialize_chapter(doc: dict) -> dict:
    d = serialize_id(dict(doc))
    return d


def serialize_note(doc: dict) -> dict:
    d = serialize_id(dict(doc))
    return d


# ── Document builders ─────────────────────────────────────────────────────────

def new_subject_doc(user_id: str, name: str, color: str = "#6C63FF", icon: str = "📚") -> dict:
    now = datetime.utcnow().isoformat()
    return {
        "user_id":    ObjectId(user_id),
        "name":       name.strip(),
        "color":      color,
        "icon":       icon,
        "created_at": now,
        "updated_at": now,
    }


def new_chapter_doc(user_id: str, subject_id: str, name: str, icon: str = "📑") -> dict:
    now = datetime.utcnow().isoformat()
    return {
        "user_id":    ObjectId(user_id),
        "subject_id": ObjectId(subject_id),
        "name":       name.strip(),
        "icon":       icon,
        "created_at": now,
        "updated_at": now,
    }


def new_note_doc(user_id: str, subject_id: str, chapter_id: str,
                 title: str = "New Note", content: str = "", tags: str = "") -> dict:
    now = datetime.utcnow().isoformat()
    return {
        "user_id":    ObjectId(user_id),
        "subject_id": ObjectId(subject_id),
        "chapter_id": ObjectId(chapter_id),
        "title":      title.strip() or "Untitled",
        "content":    content,
        "tags":       tags,
        "created_at": now,
        "updated_at": now,
        "modified":   _human_time(),
    }


def _human_time() -> str:
    return datetime.utcnow().strftime("%d %b %Y, %I:%M %p")
