"""
routes/subjects.py — Subject CRUD
  GET    /api/subjects          → List all subjects for current user
  POST   /api/subjects          → Create a new subject
  GET    /api/subjects/<id>     → Get one subject (with chapters + note counts)
  PUT    /api/subjects/<id>     → Update name / color / icon
  DELETE /api/subjects/<id>     → Delete subject + all its chapters + notes
"""

from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError
from middleware.auth import token_required
from models.note import new_subject_doc, serialize_subject
from config.db import get_db

subjects_bp = Blueprint("subjects", __name__)


def _valid_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


# ── Routes ────────────────────────────────────────────────────────────────────

@subjects_bp.route("", methods=["GET"])
@token_required
def list_subjects():
    """Return all subjects for the current user, with chapter & note counts."""
    db = get_db()
    uid = ObjectId(g.user_id)

    subjects = list(db.subjects.find({"user_id": uid}).sort("name", 1))

    result = []
    for subj in subjects:
        s = serialize_subject(subj)
        # Count chapters
        s["chapter_count"] = db.chapters.count_documents({"subject_id": subj["_id"]})
        # Count notes
        s["note_count"] = db.notes.count_documents({"subject_id": subj["_id"]})
        result.append(s)

    return jsonify({"subjects": result, "total": len(result)}), 200


@subjects_bp.route("", methods=["POST"])
@token_required
def create_subject():
    """Create a new subject."""
    data  = request.get_json(silent=True) or {}
    name  = (data.get("name") or "").strip()
    color = data.get("color", "#6C63FF")
    icon  = data.get("icon", "📚")

    if not name:
        return jsonify({"error": "Subject name is required"}), 400
    if len(name) > 80:
        return jsonify({"error": "Subject name must be under 80 characters"}), 400

    db = get_db()
    try:
        doc    = new_subject_doc(g.user_id, name, color, icon)
        result = db.subjects.insert_one(doc)
        created = db.subjects.find_one({"_id": result.inserted_id})
        s = serialize_subject(created)
        s["chapter_count"] = 0
        s["note_count"]    = 0
        return jsonify({"message": f'Subject "{name}" created! 🎓', "subject": s}), 201

    except DuplicateKeyError:
        return jsonify({"error": f'Subject "{name}" already exists'}), 409


@subjects_bp.route("/<subject_id>", methods=["GET"])
@token_required
def get_subject(subject_id):
    """Get a single subject with all its chapters and their note counts."""
    oid = _valid_id(subject_id)
    if not oid:
        return jsonify({"error": "Invalid subject ID"}), 400

    db = get_db()
    subj = db.subjects.find_one({"_id": oid, "user_id": ObjectId(g.user_id)})
    if not subj:
        return jsonify({"error": "Subject not found"}), 404

    s = serialize_subject(subj)

    # Attach chapters
    chapters = list(db.chapters.find({"subject_id": oid}).sort("name", 1))
    chs = []
    for ch in chapters:
        c = serialize_subject(ch)   # same serializer works
        c["note_count"] = db.notes.count_documents({"chapter_id": ch["_id"]})
        chs.append(c)

    s["chapters"]      = chs
    s["chapter_count"] = len(chs)
    s["note_count"]    = db.notes.count_documents({"subject_id": oid})

    return jsonify({"subject": s}), 200


@subjects_bp.route("/<subject_id>", methods=["PUT"])
@token_required
def update_subject(subject_id):
    """Update a subject's name, color, or icon."""
    oid = _valid_id(subject_id)
    if not oid:
        return jsonify({"error": "Invalid subject ID"}), 400

    db   = get_db()
    subj = db.subjects.find_one({"_id": oid, "user_id": ObjectId(g.user_id)})
    if not subj:
        return jsonify({"error": "Subject not found"}), 404

    data    = request.get_json(silent=True) or {}
    updates = {}
    if "name"  in data and data["name"].strip():
        updates["name"]  = data["name"].strip()
    if "color" in data:
        updates["color"] = data["color"]
    if "icon"  in data:
        updates["icon"]  = data["icon"]

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    from datetime import datetime
    updates["updated_at"] = datetime.utcnow().isoformat()

    try:
        db.subjects.update_one({"_id": oid}, {"$set": updates})
        updated = serialize_subject(db.subjects.find_one({"_id": oid}))
        return jsonify({"message": "Subject updated!", "subject": updated}), 200
    except DuplicateKeyError:
        return jsonify({"error": f'Subject "{updates.get("name")}" already exists'}), 409


@subjects_bp.route("/<subject_id>", methods=["DELETE"])
@token_required
def delete_subject(subject_id):
    """Delete a subject and cascade-delete all its chapters and notes."""
    oid = _valid_id(subject_id)
    if not oid:
        return jsonify({"error": "Invalid subject ID"}), 400

    db   = get_db()
    subj = db.subjects.find_one({"_id": oid, "user_id": ObjectId(g.user_id)})
    if not subj:
        return jsonify({"error": "Subject not found"}), 404

    # Cascade delete
    notes_del    = db.notes.delete_many({"subject_id": oid}).deleted_count
    chapters_del = db.chapters.delete_many({"subject_id": oid}).deleted_count
    db.subjects.delete_one({"_id": oid})

    return jsonify({
        "message":          f'Subject "{subj["name"]}" deleted',
        "chapters_deleted": chapters_del,
        "notes_deleted":    notes_del,
    }), 200
