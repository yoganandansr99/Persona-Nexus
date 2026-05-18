"""Unified `interviews` collection."""
from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any, List, Optional

def create_interview_document(
    recruiter_email: str,
    interview_id: str,
    custom_questions: List[str],
    *,
    title: str = "",
    candidate_email: str = "",
    candidate_name: str = "",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    num_questions: Optional[int] = None,
    difficulty: Optional[dict] = None,
    minutes_per_question: Optional[int] = None,
    recruiter_id: Optional[str] = None,
    is_dynamic: bool = False,
) -> dict:
    token = secrets.token_urlsafe(24)
    now = datetime.utcnow()
    return {
        "recruiter_id": recruiter_id,
        "recruiter_email": recruiter_email,
        "company_email": recruiter_email,
        "candidate_email": candidate_email or "",
        "candidate_name": candidate_name or "",
        "title": title or "Interview",
        "interview_id": interview_id,
        "token": token,
        "questions": custom_questions,
        "is_dynamic": is_dynamic,
        "difficulty": difficulty or {"easy": 1, "medium": 1, "hard": 1},
        "start_time": start_time or "",
        "end_time": end_time or "",
        "duration_minutes": duration_minutes,
        "num_questions": num_questions or (len(custom_questions) if custom_questions else None),
        "minutes_per_question": minutes_per_question,
        "created_at": now,
    }


def insert_interview(db, doc: dict) -> Any:
    return db.interviews.insert_one(doc)


def find_by_token(db, token: str) -> Optional[dict]:
    return db.interviews.find_one({"token": token})


def find_recruiter_interviews(db, recruiter_email: str, limit: int = 50) -> list:
    cur = (
        db.interviews.find({"recruiter_email": recruiter_email})
        .sort("created_at", -1)
        .limit(limit)
    )
    return list(cur)
