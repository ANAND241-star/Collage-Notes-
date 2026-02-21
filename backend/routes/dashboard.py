"""
routes/dashboard.py — Dashboard analytics API
  GET /api/dashboard/stats    → Full dashboard stats for current user
  GET /api/dashboard/activity → Last 35 days of activity heatmap data
"""

from flask import Blueprint, jsonify, g
from bson import ObjectId
from datetime import datetime, timedelta
from middleware.auth import token_required
from config.db import get_db
import re

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
@token_required
def get_stats():
    """
    Return comprehensive dashboard stats:
      - total subjects, chapters, notes, words
      - recent 7 notes
      - subject breakdown (note counts)
      - top tags
      - 35-day activity heatmap
      - streak info
    """
    db  = get_db()
    uid = ObjectId(g.user_id)

    # ── Counts ────────────────────────────────────────────────────────────────
    total_subjects = db.subjects.count_documents({"user_id": uid})
    total_chapters = db.chapters.count_documents({"user_id": uid})
    total_notes    = db.notes.count_documents({"user_id": uid})

    # ── Word count ────────────────────────────────────────────────────────────
    all_notes  = list(db.notes.find({"user_id": uid}, {"content": 1}))
    total_words = 0
    for n in all_notes:
        plain = re.sub(r"<[^>]+>", "", n.get("content", ""))
        words = plain.strip().split()
        total_words += len(words) if words else 0

    # ── Recent notes ──────────────────────────────────────────────────────────
    recent_raw = list(
        db.notes.find({"user_id": uid})
                .sort("updated_at", -1)
                .limit(7)
    )
    recent_notes = []
    for note in recent_raw:
        subj = db.subjects.find_one({"_id": note.get("subject_id")}, {"name": 1})
        ch   = db.chapters.find_one({"_id": note.get("chapter_id")},  {"name": 1})
        plain   = re.sub(r"<[^>]+>", "", note.get("content", ""))
        snippet = plain[:120] + ("…" if len(plain) > 120 else "")
        recent_notes.append({
            "id":           str(note["_id"]),
            "title":        note.get("title", "Untitled"),
            "snippet":      snippet,
            "tags":         note.get("tags", ""),
            "modified":     note.get("modified", ""),
            "updated_at":   note.get("updated_at", ""),
            "subject_id":   str(note.get("subject_id", "")),
            "subject_name": subj["name"] if subj else "Unknown",
            "chapter_id":   str(note.get("chapter_id", "")),
            "chapter_name": ch["name"]   if ch   else "Unknown",
        })

    # ── Subject breakdown ─────────────────────────────────────────────────────
    subjects_raw = list(db.subjects.find({"user_id": uid}).sort("name", 1))
    subject_breakdown = []
    for subj in subjects_raw:
        note_count = db.notes.count_documents({"subject_id": subj["_id"]})
        ch_count   = db.chapters.count_documents({"subject_id": subj["_id"]})
        subject_breakdown.append({
            "id":            str(subj["_id"]),
            "name":          subj["name"],
            "color":         subj.get("color", "#6C63FF"),
            "icon":          subj.get("icon", "📚"),
            "note_count":    note_count,
            "chapter_count": ch_count,
        })

    # ── Top tags ──────────────────────────────────────────────────────────────
    tag_freq: dict = {}
    all_tags_raw = list(db.notes.find({"user_id": uid}, {"tags": 1}))
    for n in all_tags_raw:
        for tag in (n.get("tags") or "").split(","):
            tag = tag.strip()
            if tag:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1
    top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:12]
    top_tags = [{"tag": t, "count": c} for t, c in top_tags]

    # ── Activity heatmap (last 35 days) ───────────────────────────────────────
    end_date   = datetime.utcnow()
    start_date = end_date - timedelta(days=34)
    start_str  = start_date.strftime("%Y-%m-%d")

    activity_raw = list(db.activity.find({
        "user_id": uid,
        "date":    {"$gte": start_str},
    }))
    activity_map = {a["date"]: a["count"] for a in activity_raw}

    heatmap = []
    for i in range(35):
        d   = start_date + timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        heatmap.append({"date": key, "count": activity_map.get(key, 0)})

    # ── Streak calculation ────────────────────────────────────────────────────
    streak = 0
    check  = datetime.utcnow()
    while True:
        key = check.strftime("%Y-%m-%d")
        if activity_map.get(key, 0) > 0:
            streak += 1
            check  -= timedelta(days=1)
        else:
            break

    return jsonify({
        "stats": {
            "total_subjects": total_subjects,
            "total_chapters": total_chapters,
            "total_notes":    total_notes,
            "total_words":    total_words,
        },
        "recent_notes":      recent_notes,
        "subject_breakdown": subject_breakdown,
        "top_tags":          top_tags,
        "heatmap":           heatmap,
        "streak_days":       streak,
        "unique_tags":       len(tag_freq),
    }), 200


@dashboard_bp.route("/activity", methods=["GET"])
@token_required
def get_activity():
    """Return full activity log for the current user."""
    db  = get_db()
    uid = ObjectId(g.user_id)

    activity = list(
        db.activity.find({"user_id": uid}, {"_id": 0, "user_id": 0})
                   .sort("date", -1)
                   .limit(365)
    )
    return jsonify({"activity": activity, "total_days": len(activity)}), 200
