"""
routes/notes.py — Notes CRUD + full-text search
  GET    /api/notes?chapter_id=<id>     → List notes in a chapter
  GET    /api/notes/search?q=<query>    → Full-text search across all user notes
  POST   /api/notes                     → Create a note
  GET    /api/notes/<id>                → Get a single note
  PUT    /api/notes/<id>                → Update note (title, content, tags)
  DELETE /api/notes/<id>                → Delete a note
"""

from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from middleware.auth import token_required
from models.note import new_note_doc, serialize_note
from config.db import get_db

notes_bp = Blueprint("notes", __name__)


def _valid_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


def _human_now():
    return datetime.utcnow().strftime("%d %b %Y, %I:%M %p")


# ── Routes ────────────────────────────────────────────────────────────────────

@notes_bp.route("/search", methods=["GET"])
@token_required
def search_notes():
    """
    Full-text search across all notes belonging to the current user.
    Uses MongoDB $text index on title + content + tags.
    Falls back to regex if no text index match.
    """
    query = (request.args.get("q") or "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    limit = min(int(request.args.get("limit", 20)), 50)
    db    = get_db()
    uid   = ObjectId(g.user_id)

    # Try MongoDB full-text search first
    try:
        raw = list(db.notes.find(
            {"$text": {"$search": query}, "user_id": uid},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
    except Exception:
        # Fallback: case-insensitive regex across title, content, tags
        rx  = {"$regex": query, "$options": "i"}
        raw = list(db.notes.find({
            "user_id": uid,
            "$or": [{"title": rx}, {"content": rx}, {"tags": rx}]
        }).sort("updated_at", -1).limit(limit))

    # Enrich with subject + chapter names
    results = []
    for note in raw:
        n = serialize_note(note)
        subj = db.subjects.find_one({"_id": note.get("subject_id")})
        ch   = db.chapters.find_one({"_id": note.get("chapter_id")})
        n["subject_name"] = subj["name"] if subj else "Unknown"
        n["chapter_name"] = ch["name"]   if ch   else "Unknown"
        # Trim content for snippet
        import re
        plain = re.sub(r"<[^>]+>", "", n.get("content", ""))
        n["snippet"] = plain[:150] + ("…" if len(plain) > 150 else "")
        results.append(n)

    return jsonify({"results": results, "total": len(results), "query": query}), 200


@notes_bp.route("", methods=["GET"])
@token_required
def list_notes():
    """List all notes in a chapter, sorted by last modified."""
    chapter_id = request.args.get("chapter_id")
    if not chapter_id:
        return jsonify({"error": "chapter_id query param is required"}), 400

    cid = _valid_id(chapter_id)
    if not cid:
        return jsonify({"error": "Invalid chapter_id"}), 400

    db = get_db()
    # Verify chapter belongs to user
    ch = db.chapters.find_one({"_id": cid, "user_id": ObjectId(g.user_id)})
    if not ch:
        return jsonify({"error": "Chapter not found"}), 404

    notes = list(db.notes.find({"chapter_id": cid}).sort("updated_at", -1))
    result = []
    for note in notes:
        n = serialize_note(note)
        # Trim content to snippet
        import re
        plain     = re.sub(r"<[^>]+>", "", n.get("content", ""))
        n["snippet"] = plain[:120] + ("…" if len(plain) > 120 else "")
        result.append(n)

    return jsonify({"notes": result, "total": len(result)}), 200


@notes_bp.route("", methods=["POST"])
@token_required
def create_note():
    """Create a new note."""
    data       = request.get_json(silent=True) or {}
    chapter_id = data.get("chapter_id", "")
    subject_id = data.get("subject_id", "")
    title      = (data.get("title") or "New Note").strip()
    content    = data.get("content", "")
    tags       = data.get("tags", "")

    if not chapter_id or not subject_id:
        return jsonify({"error": "chapter_id and subject_id are required"}), 400

    cid = _valid_id(chapter_id)
    sid = _valid_id(subject_id)
    if not cid or not sid:
        return jsonify({"error": "Invalid chapter_id or subject_id"}), 400

    db = get_db()
    ch = db.chapters.find_one({"_id": cid, "user_id": ObjectId(g.user_id)})
    if not ch:
        return jsonify({"error": "Chapter not found"}), 404

    doc    = new_note_doc(g.user_id, subject_id, chapter_id, title, content, tags)
    result = db.notes.insert_one(doc)

    # Record activity
    _record_activity(db, g.user_id)

    created = serialize_note(db.notes.find_one({"_id": result.inserted_id}))
    return jsonify({"message": f'Note "{title}" created! 📝', "note": created}), 201


@notes_bp.route("/<note_id>", methods=["GET"])
@token_required
def get_note(note_id):
    """Get a single note by ID."""
    nid = _valid_id(note_id)
    if not nid:
        return jsonify({"error": "Invalid note ID"}), 400

    db   = get_db()
    note = db.notes.find_one({"_id": nid, "user_id": ObjectId(g.user_id)})
    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify({"note": serialize_note(note)}), 200


@notes_bp.route("/<note_id>", methods=["PUT"])
@token_required
def update_note(note_id):
    """Update a note's title, content, and/or tags."""
    nid = _valid_id(note_id)
    if not nid:
        return jsonify({"error": "Invalid note ID"}), 400

    db   = get_db()
    note = db.notes.find_one({"_id": nid, "user_id": ObjectId(g.user_id)})
    if not note:
        return jsonify({"error": "Note not found"}), 404

    data    = request.get_json(silent=True) or {}
    updates = {}

    if "title" in data:
        updates["title"]   = (data["title"] or "Untitled").strip()
    if "content" in data:
        updates["content"] = data["content"]
    if "tags" in data:
        updates["tags"]    = data["tags"]

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    now = datetime.utcnow().isoformat()
    updates["updated_at"] = now
    updates["modified"]   = _human_now()

    db.notes.update_one({"_id": nid}, {"$set": updates})

    # Record activity
    _record_activity(db, g.user_id)

    updated = serialize_note(db.notes.find_one({"_id": nid}))
    return jsonify({"message": "Note saved! 💾", "note": updated}), 200


@notes_bp.route("/<note_id>", methods=["DELETE"])
@token_required
def delete_note(note_id):
    """Delete a note."""
    nid = _valid_id(note_id)
    if not nid:
        return jsonify({"error": "Invalid note ID"}), 400

    db   = get_db()
    note = db.notes.find_one({"_id": nid, "user_id": ObjectId(g.user_id)})
    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.notes.delete_one({"_id": nid})

    return jsonify({"message": f'Note "{note.get("title","Note")}" deleted'}), 200


# ── Internal helpers ──────────────────────────────────────────────────────────

def _record_activity(db, user_id: str):
    """Increment the save count for today in the activity collection."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    db.activity.update_one(
        {"user_id": ObjectId(user_id), "date": today},
        {"$inc": {"count": 1}},
        upsert=True,
    )
