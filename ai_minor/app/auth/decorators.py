from functools import wraps
from flask import session, jsonify, redirect, url_for, request

from app.auth.helpers import practice_user_logged_in


def require_recruiter(f):
    """JSON API guard for recruiter portal."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        from app.auth.helpers import get_portal_role, ROLE_RECRUITER
        if get_portal_role() != ROLE_RECRUITER:
            return jsonify({"error": "Recruiter authentication required"}), 401
        return f(*args, **kwargs)

    return wrapped


def require_recruiter_page(f):
    """HTML page guard — redirects to company dashboard login."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        from app.auth.helpers import get_portal_role, ROLE_RECRUITER
        if get_portal_role() != ROLE_RECRUITER:
            return redirect(url_for("company_bp.company_dashboard"))
        return f(*args, **kwargs)

    return wrapped


def require_practice_user(f):
    """JSON API guard for practice portal."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not practice_user_logged_in():
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return wrapped


def require_practice_user_page(f):
    """HTML page guard — redirects to practice landing."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not practice_user_logged_in():
            return redirect(url_for("practice.practice_home"))
        return f(*args, **kwargs)

    return wrapped


def require_candidate_page(f):
    """HTML guard for candidate portal pages."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        from app.auth.helpers import candidate_session_active
        if not candidate_session_active():
            return redirect(url_for("interview_portal.interview_access_gate"))
        return f(*args, **kwargs)

    return wrapped


def require_json(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Expected application/json"}), 400
        return f(*args, **kwargs)

    return wrapped


def json_error(message: str, code: int = 400):
    return jsonify({"error": message}), code
