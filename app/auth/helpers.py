"""Unified session keys (additive — legacy keys like logged_in_user remain)."""
from __future__ import annotations

from typing import Optional

from flask import session

ROLE_PRACTICE_USER = "practice_user"
ROLE_RECRUITER = "recruiter"
ROLE_CANDIDATE_SESSION = "candidate"


def set_practice_session(user_id: str, email: str, name: str) -> None:
    session["logged_in_user"] = user_id
    session["portal_role"] = ROLE_PRACTICE_USER
    session["user_email"] = email
    session["user_name"] = name


def set_recruiter_session(email: str, company_name: Optional[str] = None) -> None:
    session["company_email"] = email
    session["portal_role"] = ROLE_RECRUITER
    if company_name:
        session["company_name"] = company_name


def set_candidate_session(token: str, interview_id: str, company_email: str | None = None) -> None:
    session["is_candidate"] = True
    session["portal_role"] = ROLE_CANDIDATE_SESSION
    session["interview_token"] = token
    session["current_interview_id"] = interview_id
    if company_email:
        session["company_email"] = company_email


def clear_portal_session() -> None:
    for key in (
        "portal_role",
        "user_email",
        "user_name",
        "company_name",
        "company_email",
        "is_candidate",
        "interview_token",
        "current_interview_id",
        "custom_questions",
        "interview_pass_key",
    ):
        session.pop(key, None)


def get_portal_role() -> Optional[str]:
    return session.get("portal_role")


def practice_user_logged_in() -> bool:
    return bool(session.get("logged_in_user")) and session.get("portal_role") == ROLE_PRACTICE_USER


def candidate_session_active() -> bool:
    return session.get("portal_role") == ROLE_CANDIDATE_SESSION and bool(session.get("is_candidate"))


def recruiter_session_email() -> Optional[str]:
    """Recruiter email when logged in as recruiter (same key used for candidate CC)."""
    return session.get("company_email")
