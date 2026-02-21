"""
routes/chapters.py — Chapter CRUD
  GET    /api/chapters?subject_id=<id>   → List chapters in a subject
  POST   /api/chapters                   → Create a chapter
  PUT    /api/chapters/<id>              → Update chapter
  DELETE /api/chapters/<id>             → Delete chapter + its notes
"""

from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from middleware.auth import token_required
from models.note import new_chapter_doc, serialize_chapter
from config.db import get_db

chapters_bp = Blueprint("chapters", __name__)


def _valid_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


@chapters_bp.route("", methods=["GET"])
@token_required
def list_chapters():
    """List all chapters for a given subject_id."""
    subject_id = request.args.get("subject_id")
    if not subject_id:
        return jsonify({"error": "subject_id query param is required"}), 400

    sid = _valid_id(subject_id)
    if not sid:
        return jsonify({"error": "Invalid subject_id"}), 400

    db = get_db()
    # Verify subject belongs to user
    subj = db.subjects.find_one({"_id": sid, "user_id": ObjectId(g.user_id)})
    if not subj:
        return jsonify({"error": "Subject not found"}), 404

    chapters = list(db.chapters.find({"subject_id": sid}).sort("name", 1))
    result = []
    for ch in chapters:
        c = serialize_chapter(ch)
        c["note_count"] = db.notes.count_documents({"chapter_id": ch["_id"]})
        result.append(c)

    return jsonify({"chapters": result, "total": len(result)}), 200


@chapters_bp.route("", methods=["POST"])
@token_required
def create_chapter():
    """Create a new chapter inside a subject."""
    data       = request.get_json(silent=True) or {}
    subject_id = data.get("subject_id", "")
    name       = (data.get("name") or "").strip()
    icon       = data.get("icon", "📑")

    if not subject_id:
        return jsonify({"error": "subject_id is required"}), 400
    if not name:
        return jsonify({"error": "Chapter name is required"}), 400
    if len(name) > 100:
        return jsonify({"error": "Chapter name too long (max 100 chars)"}), 400

    sid = _valid_id(subject_id)
    if not sid:
        return jsonify({"error": "Invalid subject_id"}), 400

    db = get_db()
    subj = db.subjects.find_one({"_id": sid, "user_id": ObjectId(g.user_id)})
    if not subj:
        return jsonify({"error": "Subject not found"}), 404

    try:
        doc    = new_chapter_doc(g.user_id, subject_id, name, icon)
        result = db.chapters.insert_one(doc)
        created = serialize_chapter(db.chapters.find_one({"_id": result.inserted_id}))
        created["note_count"] = 0
        return jsonify({"message": f'Chapter "{name}" created! 📑', "chapter": created}), 201
    except DuplicateKeyError:
        return jsonify({"error": f'Chapter "{name}" already exists in this subject'}), 409


@chapters_bp.route("/<chapter_id>", methods=["PUT"])
@token_required
def update_chapter(chapter_id):
    """Update a chapter's name or icon."""
    cid = _valid_id(chapter_id)
    if not cid:
        return jsonify({"error": "Invalid chapter ID"}), 400

    db = get_db()
    ch = db.chapters.find_one({"_id": cid, "user_id": ObjectId(g.user_id)})
    if not ch:
        return jsonify({"error": "Chapter not found"}), 404

    data    = request.get_json(silent=True) or {}
    updates = {}
    if "name" in data and data["name"].strip():
        updates["name"] = data["name"].strip()
    if "icon" in data:
        updates["icon"] = data["icon"]

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    updates["updated_at"] = datetime.utcnow().isoformat()

    try:
        db.chapters.update_one({"_id": cid}, {"$set": updates})
        updated = serialize_chapter(db.chapters.find_one({"_id": cid}))
        return jsonify({"message": "Chapter updated!", "chapter": updated}), 200
    except DuplicateKeyError:
        return jsonify({"error": f'Chapter "{updates.get("name")}" already exists'}), 409


@chapters_bp.route("/<chapter_id>", methods=["DELETE"])
@token_required
def delete_chapter(chapter_id):
    """Delete a chapter and all its notes."""
    cid = _valid_id(chapter_id)
    if not cid:
        return jsonify({"error": "Invalid chapter ID"}), 400

    db = get_db()
    ch = db.chapters.find_one({"_id": cid, "user_id": ObjectId(g.user_id)})
    if not ch:
        return jsonify({"error": "Chapter not found"}), 404

    notes_del = db.notes.delete_many({"chapter_id": cid}).deleted_count
    db.chapters.delete_one({"_id": cid})

    return jsonify({
        "message":       f'Chapter "{ch["name"]}" deleted',
        "notes_deleted": notes_del,
    }), 200
