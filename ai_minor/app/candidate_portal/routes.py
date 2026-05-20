"""Company interview entry: secure token URL + manual access code (AI pipeline unchanged)."""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.auth.helpers import set_candidate_session, ROLE_CANDIDATE_SESSION
from app.repositories import interviews_repo

interview_portal_bp = Blueprint("interview_portal", __name__)


def _apply_interview_document(doc: dict) -> None:
    session["is_candidate"] = True
    session["portal_role"] = ROLE_CANDIDATE_SESSION
    session["company_email"] = doc.get("recruiter_email") or doc.get("company_email")
    session["custom_questions"] = doc.get("questions") or []
    session["interview_token"] = doc.get("token")
    session["current_interview_id"] = doc.get("interview_id")
    session["minutes_per_question"] = doc.get("minutes_per_question")
    session["num_questions"] = doc.get("num_questions") or len(doc.get("questions") or [])
    session["duration_minutes"] = doc.get("duration_minutes")
    session["is_dynamic"] = doc.get("is_dynamic", False)


@interview_portal_bp.route("/interview/access", methods=["GET", "POST"])
def interview_access_gate():
    """Candidates paste the access key the recruiter sent (same as token in invite link)."""
    err = None
    if request.method == "POST":
        raw = (request.form.get("access_code") or "").strip()
        token = raw.replace(" ", "")
        if not token:
            err = "Enter the access code your recruiter sent you."
        else:
            from app.db import db

            if db is None:
                return render_template("interview/access_gate.html", error="Database unavailable."), 503
            doc = interviews_repo.find_by_token(db, token)
            if not doc:
                return render_template(
                    "interview/access_gate.html",
                    error="That access code was not found. Ask your recruiter for a new link or code.",
                ), 400
            _apply_interview_document(doc)
            return redirect(url_for("interview_portal.interview_start"))
    return render_template("interview/access_gate.html", error=err)


@interview_portal_bp.route("/interview/<token>")
def interview_entry_by_token(token: str):
    from app.db import db

    if db is None:
        return render_template("interview/invalid_code.html", db_down=True), 503
    doc = interviews_repo.find_by_token(db, token.strip())
    if not doc:
        return render_template("interview/invalid_code.html", attempted=True), 404

    _apply_interview_document(doc)
    return redirect(url_for("interview_portal.interview_start"))


@interview_portal_bp.route("/interview/start", methods=["GET", "POST"])
def interview_start():
    from app.db import db
    from app.auth.helpers import ROLE_CANDIDATE_SESSION

    token = session.get("interview_token")
    if not token:
        return redirect(url_for("interview_portal.interview_access_gate"))

    if db is None:
        return render_template("interview/invalid_code.html", db_down=True), 503

    doc = interviews_repo.find_by_token(db, token.strip())
    if not doc:
        return render_template("interview/invalid_code.html", attempted=True), 404

    if doc.get("is_completed"):
        return render_template(
            "interview/start.html",
            interview=doc,
            error="This interview link has already been used and is no longer valid.",
            default_name=doc.get("candidate_name", ""),
            default_email=doc.get("candidate_email", ""),
            default_age="",
            default_gender="",
        )

    import datetime
    now_dt = datetime.datetime.now()
    
    start_time_str = doc.get("start_time")
    if start_time_str:
        try:
            start_dt = datetime.datetime.fromisoformat(start_time_str)
            if now_dt < start_dt:
                return render_template(
                    "interview/start.html",
                    interview=doc,
                    error=f"This interview is scheduled to start at {start_dt.strftime('%B %d, %Y %I:%M %p')}. Please come at that time.",
                    default_name=doc.get("candidate_name", ""),
                    default_email=doc.get("candidate_email", ""),
                    default_age="",
                    default_gender="",
                )
        except Exception:
            pass

    end_time_str = doc.get("end_time")
    if end_time_str:
        try:
            end_dt = datetime.datetime.fromisoformat(end_time_str)
            if now_dt > end_dt:
                return render_template(
                    "interview/start.html",
                    interview=doc,
                    error=f"This interview expired at {end_dt.strftime('%B %d, %Y %I:%M %p')}.",
                    default_name=doc.get("candidate_name", ""),
                    default_email=doc.get("candidate_email", ""),
                    default_age="",
                    default_gender="",
                )
        except Exception:
            pass

    if request.method == "POST":
        name = (request.form.get("name") or doc.get("candidate_name") or "").strip()
        email = (request.form.get("email") or doc.get("candidate_email") or "").strip().lower()
        age = (request.form.get("age") or "").strip()
        gender = (request.form.get("gender") or "").strip()

        if not name or not email:
            return render_template(
                "interview/start.html",
                interview=doc,
                error="Name and email are required to begin the interview.",
                default_name=name,
                default_email=email,
                default_age=age,
                default_gender=gender,
            )

        import random
        import time
        from app.email import send_otp_email
        
        otp_code = str(random.randint(100000, 999999))
        session['temp_user_data'] = {
            "name": name,
            "email": email,
            "age": age,
            "gender": gender,
        }
        session['verification_otp'] = otp_code
        session['otp_expiry'] = time.time() + 600
        session['otp_attempts'] = 0

        session["portal_role"] = ROLE_CANDIDATE_SESSION
        session["is_candidate"] = True
        session["custom_questions"] = doc.get("questions") or []
        session["company_email"] = doc.get("recruiter_email") or doc.get("company_email")

        try:
            send_otp_email(email, otp_code)
        except Exception as e:
            return render_template(
                "interview/start.html",
                interview=doc,
                error="Failed to send OTP to your email. Please try again.",
                default_name=name,
                default_email=email,
                default_age=age,
                default_gender=gender,
            )

        return redirect(url_for("verify_otp_page"))

    return render_template(
        "interview/start.html",
        interview=doc,
        error=None,
        default_name=doc.get("candidate_name", ""),
        default_email=doc.get("candidate_email", ""),
        default_age="",
        default_gender="",
    )
