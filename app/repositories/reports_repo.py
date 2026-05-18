"""Unified `reports` collection."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def insert_normalized_report(
    db,
    *,
    candidate_email: str,
    interview_id: Optional[str],
    interview_token: Optional[str],
    practice_user_id: Optional[str],
    source: str,
    primary_color: str,
    confidence: int,
    fluency: int,
    engagement: int,
    empathy: int,
    malpractice: bool,
    report_data: dict,
    overall_performance: float,
    avg_score: float,
) -> Any:
    doc = {
        "candidate_email": candidate_email,
        "interview_id": interview_id,
        "interview_token": interview_token,
        "practice_user_id": practice_user_id,
        "source": source,
        "primary_color": primary_color,
        "scores": {
            "confidence": confidence,
            "fluency": fluency,
            "engagement": engagement,
            "empathy": empathy,
            "overall_performance": overall_performance,
            "avg_score": avg_score,
        },
        "report_data": report_data,
        "malpractice": malpractice,
        "created_at": datetime.utcnow(),
    }
    return db.reports.insert_one(doc)


def list_reports_for_email(db, email: str, limit: int = 30) -> list:
    cur = (
        db.reports.find({"candidate_email": email, "malpractice": {"$ne": True}})
        .sort("created_at", -1)
        .limit(limit)
    )
    return list(cur)
