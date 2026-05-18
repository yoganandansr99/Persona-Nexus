"""
One-time migration: copy legacy Mongo collections into normalized ones.

Run manually when ready (staging first):
  python scripts/migrate_mongo_collections.py

Requires MONGO_URI in environment. Does NOT delete legacy data.
"""
from __future__ import annotations

import os
import secrets
import sys
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

# Project root: ai_minor/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main() -> int:
    load_dotenv(os.path.join(ROOT, ".env"))

    uri = os.environ.get("MONGO_URI")
    if not uri:
        print("MONGO_URI not set")
        return 1
    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    client.admin.command("ping")
    db = client["AI_interview"]

    for u in db.Users.find():
        if db.users.find_one({"email": u.get("email"), "role": "practice_user"}):
            continue
        db.users.insert_one(
            {
                "role": "practice_user",
                "name": u.get("name", ""),
                "email": u.get("email"),
                "password_hash": u.get("password"),
                "created_at": u.get("created_at"),
                "migrated_from_users": True,
            }
        )
    for c in db.Companies.find():
        if db.users.find_one({"email": c.get("email"), "role": "recruiter"}):
            continue
        db.users.insert_one(
            {
                "role": "recruiter",
                "name": c.get("company_name", ""),
                "email": c.get("email"),
                "company_name": c.get("company_name", ""),
                "password_hash": c.get("password"),
                "created_at": c.get("created_at"),
                "migrated_from_companies": True,
            }
        )

    for inv in db.CompanyInterviews.find():
        if db.interviews.find_one({"interview_id": inv.get("interview_id")}):
            continue
        token = secrets.token_urlsafe(24)
        db.interviews.insert_one(
            {
                "recruiter_email": inv.get("company_email"),
                "company_email": inv.get("company_email"),
                "candidate_email": "",
                "title": "Interview",
                "interview_id": inv.get("interview_id"),
                "token": token,
                "questions": inv.get("custom_questions") or [],
                "difficulty": inv.get("difficulty") or {},
                "start_time": inv.get("start_time") or "",
                "end_time": inv.get("end_time") or "",
                "created_at": inv.get("created_at", datetime.utcnow()),
                "migrated": True,
            }
        )

    for row in db.Persona_chroma.find():
        if (
            row.get("message")
            == "If you are reading this in MongoDB Atlas, your connection is working perfectly!"
        ):
            continue
        if db.reports.find_one(
            {"candidate_email": row.get("email"), "created_at": row.get("created_at")}
        ):
            continue
        rd = row.get("report_data") or {}
        db.reports.insert_one(
            {
                "candidate_email": row.get("email", ""),
                "interview_id": None,
                "interview_token": None,
                "practice_user_id": None,
                "source": "migrated",
                "primary_color": row.get("primary_color", ""),
                "scores": {
                    "confidence": row.get("confidence", 0),
                    "fluency": row.get("fluency", 0),
                    "engagement": row.get("engagement", 0),
                    "empathy": row.get("empathy", 0),
                    "overall_performance": 0,
                    "avg_score": 0,
                },
                "report_data": rd,
                "malpractice": row.get("malpractice", False),
                "created_at": row.get("created_at"),
            }
        )

    print("Migration finished (additive only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
