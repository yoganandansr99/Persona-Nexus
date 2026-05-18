# Role-based session helpers and decorators for multi-portal access.
from app.auth.helpers import (
    ROLE_PRACTICE_USER,
    ROLE_RECRUITER,
    ROLE_CANDIDATE_SESSION,
    set_practice_session,
    clear_portal_session,
    get_portal_role,
    practice_user_logged_in,
    recruiter_session_email,
)
from app.auth.decorators import require_practice_user, require_json, json_error

__all__ = [
    "ROLE_PRACTICE_USER",
    "ROLE_RECRUITER",
    "ROLE_CANDIDATE_SESSION",
    "set_practice_session",
    "clear_portal_session",
    "get_portal_role",
    "practice_user_logged_in",
    "recruiter_session_email",
    "require_practice_user",
    "require_json",
    "json_error",
]
