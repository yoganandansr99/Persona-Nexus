"""Create recruiter-configured interviews (legacy + normalized collections)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.auth.helpers import ROLE_RECRUITER
from app.repositories import interviews_repo


def generate_ai_questions_from_model(question_count: int = 5, theme: str = "behavioral interview") -> List[str]:
    from app import groq_client
    default_questions = [
        "Tell me about yourself.",
        "What are your greatest strengths and weaknesses?",
        "Describe a challenge you overcame.",
        "How do you stay motivated when work gets difficult?",
        "Why should we hire you for this position?",
    ]

    if not groq_client or question_count <= 0:
        return default_questions[:question_count]

    prompt = (
        f"Generate {question_count} concise interview questions for a {theme} role. "
        "Return the questions as a JSON array only."
    )
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile"
        )
        content = response.choices[0].message.content.strip()
        import json
        questions = json.loads(content)
        if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
            return questions[:question_count]
    except Exception:
        pass

    return default_questions[:question_count]


def create_interview_for_recruiter(
    db,
    company_email: str,
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
    generate_ai_questions: bool = False,
    base_url: str = "http://localhost:5000",
) -> Dict[str, Any]:
    interview_id = str(uuid.uuid4())
    now = datetime.utcnow()
    rec = db.users.find_one({"email": company_email, "role": ROLE_RECRUITER})
    recruiter_id = str(rec["_id"]) if rec else None
    company_name = rec.get("company_name") or rec.get("name") or company_email if rec else company_email

    if generate_ai_questions and not custom_questions:
        custom_questions = ["Can you tell me a little about yourself and your background?"]

    norm = interviews_repo.create_interview_document(
        company_email,
        interview_id,
        custom_questions,
        title=title,
        candidate_email=candidate_email,
        candidate_name=candidate_name,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_minutes,
        num_questions=num_questions,
        difficulty=difficulty,
        minutes_per_question=minutes_per_question,
        recruiter_id=recruiter_id,
        is_dynamic=generate_ai_questions,
    )
    interviews_repo.insert_interview(db, norm)

    token = norm["token"]
    invite_link = f"/interview/{token}"
    invite_link_legacy = f"/candidate/join/{interview_id}"

    # Send emails if candidate email provided
    if candidate_email:
        try:
            from app.email import send_interview_invitation_email, send_recruiter_confirmation_email
            full_link = f"{base_url}{invite_link}"
            send_interview_invitation_email(
                candidate_email=candidate_email,
                candidate_name=candidate_name or "",
                recruiter_company=company_name,
                interview_title=title or "Interview",
                interview_link=full_link,
                token=token,
                start_time=start_time or "",
                end_time=end_time or "",
                duration_minutes=duration_minutes,
            )
            send_recruiter_confirmation_email(
                recruiter_email=company_email,
                recruiter_company=company_name,
                candidate_email=candidate_email,
                candidate_name=candidate_name or "",
                interview_title=title or "Interview",
                interview_link=full_link,
                token=token,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Email send error in interview_service: {e}")

    return {
        "interview_id": interview_id,
        "token": token,
        "invite_link": invite_link_legacy,
        "invite_link_token": invite_link,
    }
