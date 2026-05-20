"""Recruiter portal — /recruiter serves its own dashboard UI."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response

from app.auth.helpers import set_recruiter_session, get_portal_role, ROLE_RECRUITER
from app.auth.decorators import require_recruiter
from app.repositories import users_repo
from app.services.interview_service import create_interview_for_recruiter
from werkzeug.security import check_password_hash

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/recruiter")


# ── Pages ──────────────────────────────────────────────────────────────────

@recruiter_bp.route("/")
def recruiter_home():
    """Recruiter dashboard — own UI, not the legacy company page."""
    return render_template("recruiter/recruiter_dashboard.html")


import random
import time

# ── Auth APIs ──────────────────────────────────────────────────────────────

@recruiter_bp.route("/api/send_otp", methods=["POST"])
def recruiter_api_send_otp():
    """Step 1 of signup — validate inputs and send OTP to email."""
    from app.db import db
    from app.email import send_otp_email
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400

    data         = request.get_json() or {}
    email        = (data.get("email") or "").strip().lower()
    company_name = (data.get("company_name") or "").strip()
    password     = data.get("password") or ""

    if not email or not company_name or not password:
        return jsonify({"error": "Company name, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 400

    # Generate OTP and store in session temporarily
    otp = str(random.randint(100000, 999999))
    session["recruiter_signup_otp"]      = otp
    session["recruiter_signup_otp_expiry"] = time.time() + 600   # 10 minutes
    session["recruiter_signup_pending"]  = {
        "email": email,
        "company_name": company_name,
        "password": password,
    }

    send_otp_email(email, otp)
    return jsonify({"message": "OTP sent to your email. Please verify to complete registration."}), 200


@recruiter_bp.route("/api/verify_otp", methods=["POST"])
def recruiter_api_verify_otp():
    """Step 2 of signup — verify OTP and create account."""
    from app.db import db
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400

    data     = request.get_json() or {}
    otp_input = (data.get("otp") or "").strip()

    stored_otp    = session.get("recruiter_signup_otp")
    otp_expiry    = session.get("recruiter_signup_otp_expiry", 0)
    pending       = session.get("recruiter_signup_pending")

    if not stored_otp or not pending:
        return jsonify({"error": "No pending registration. Please start signup again."}), 400
    if time.time() > otp_expiry:
        session.pop("recruiter_signup_otp", None)
        session.pop("recruiter_signup_otp_expiry", None)
        session.pop("recruiter_signup_pending", None)
        return jsonify({"error": "OTP expired. Please register again."}), 400
    if otp_input != stored_otp:
        return jsonify({"error": "Invalid OTP. Please try again."}), 400

    # OTP correct — create the account
    email        = pending["email"]
    company_name = pending["company_name"]
    password     = pending["password"]

    # Double-check email not taken (race condition guard)
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 400

    users_repo.insert_recruiter_user(db, email, password, company_name)

    # Clean up session
    session.pop("recruiter_signup_otp", None)
    session.pop("recruiter_signup_otp_expiry", None)
    session.pop("recruiter_signup_pending", None)

    return jsonify({"message": "Account verified and created successfully. You can now log in."}), 201


@recruiter_bp.route("/api/signup", methods=["POST"])
def recruiter_api_signup():
    from app.db import db
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400

    data = request.get_json() or {}
    email        = (data.get("email") or "").strip().lower()
    company_name = (data.get("company_name") or "").strip()
    password     = data.get("password") or ""

    if not email or not company_name or not password:
        return jsonify({"error": "company_name, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 400

    users_repo.insert_recruiter_user(db, email, password, company_name)
    return jsonify({"message": "Company account created."}), 201


@recruiter_bp.route("/api/login", methods=["POST"])
def recruiter_api_login():
    from app.db import db
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400

    data     = request.get_json() or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    company = users_repo.find_recruiter_by_email(db, email)
    if not company or not check_password_hash(company["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    set_recruiter_session(email, company.get("company_name") or company.get("name"))
    return jsonify({"message": "Login successful", "company_email": email})


@recruiter_bp.route("/api/logout", methods=["POST"])
def recruiter_api_logout():
    session.pop("company_email", None)
    session.pop("portal_role", None)
    session.pop("company_name", None)
    return jsonify({"message": "Logged out"})


# ── Interview APIs ─────────────────────────────────────────────────────────

@recruiter_bp.route("/api/create_interview", methods=["POST"])
@require_recruiter
def recruiter_api_create_interview():
    from app.db import db
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400

    data = request.get_json() or {}
    company_email = (data.get("company_email") or "").strip().lower() or session.get("company_email", "")
    if not company_email:
        return jsonify({"error": "Not authenticated. Please log in first."}), 401

    qs = data.get("custom_questions") or []
    if isinstance(qs, str):
        qs = [q.strip() for q in qs.split("\n\n") if q.strip()]

    difficulty = data.get("difficulty") or {"easy": 1, "medium": 1, "hard": 1}
    if isinstance(difficulty, str):
        try:
            import json
            difficulty = json.loads(difficulty)
        except Exception:
            difficulty = {"easy": 1, "medium": 1, "hard": 1}

    num_questions = data.get("num_questions")
    if isinstance(num_questions, str) and num_questions.isdigit():
        num_questions = int(num_questions)

    minutes_per_question = data.get("minutes_per_question")
    if isinstance(minutes_per_question, str) and minutes_per_question.isdigit():
        minutes_per_question = int(minutes_per_question)

    raw_generate_ai = data.get("generate_ai_questions")
    use_ai_questions = str(raw_generate_ai).lower() in ("1", "true", "yes", "on")

    # Build full interview link using request host
    base_url = request.host_url.rstrip("/")

    result = create_interview_for_recruiter(
        db,
        company_email,
        qs,
        title            = data.get("title") or "",
        candidate_email  = data.get("candidate_email") or "",
        candidate_name   = data.get("candidate_name") or "",
        start_time       = data.get("start_time"),
        end_time         = data.get("end_time"),
        duration_minutes = data.get("duration_minutes"),
        num_questions    = num_questions,
        difficulty       = difficulty,
        minutes_per_question = minutes_per_question,
        generate_ai_questions = use_ai_questions,
        base_url         = base_url,
    )

    return jsonify({
        "message"          : "Interview created successfully.",
        "invite_link"      : result["invite_link"],
        "invite_link_token": result["invite_link_token"],
        "interview_id"     : result["interview_id"],
        "token"            : result["token"],
    }), 201


@recruiter_bp.route("/api/interviews", methods=["GET"])
@require_recruiter
def recruiter_api_list_interviews():
    from app.db import db
    from app.repositories import interviews_repo
    if db is None:
        return jsonify({"error": "Database not connected"}), 500

    email = (request.args.get("company_email") or "").strip().lower() or session.get("company_email", "")
    if not email:
        return jsonify({"error": "company_email required"}), 400

    rows = interviews_repo.find_recruiter_interviews(db, email, limit=50)
    out  = []
    for r in rows:
        out.append({
            "title"              : r.get("title"),
            "candidate_email"    : r.get("candidate_email"),
            "candidate_name"     : r.get("candidate_name", ""),
            "interview_id"       : r.get("interview_id"),
            "token"              : r.get("token"),
            "invite_link"        : f"/candidate/join/{r.get('interview_id')}",
            "invite_link_token"  : f"/interview/{r.get('token')}",
            "pass_key_required"  : bool(r.get("pass_key")),
            "num_questions"      : r.get("num_questions"),
            "difficulty"         : r.get("difficulty"),
            "created_at"         : r.get("created_at").isoformat() if r.get("created_at") else None,
        })
    return jsonify({"interviews": out})


@recruiter_bp.route("/api/reports", methods=["GET"])
@require_recruiter
def recruiter_api_reports():
    from app.db import db
    from app.repositories import interviews_repo
    if db is None:
        return jsonify({"error": "Database not connected"}), 500

    company_email = session.get("company_email", "")
    if not company_email:
        return jsonify({"error": "Not authenticated."}), 401

    interviews = interviews_repo.find_recruiter_interviews(db, company_email, limit=200)
    interview_ids = [iv.get("interview_id") for iv in interviews if iv.get("interview_id")]
    if not interview_ids:
        return jsonify({"reports": []})

    records = db.reports.find({"interview_id": {"$in": interview_ids}}).sort("created_at", -1).limit(200)
    out = []
    for r in records:
        out.append({
            "report_id": str(r.get("_id")),
            "candidate_email": r.get("candidate_email"),
            "primary_color": r.get("primary_color"),
            "scores": r.get("scores", {}),
            "source": r.get("source"),
            "malpractice": r.get("malpractice", False),
            "created_at": r.get("created_at").isoformat() if r.get("created_at") else None,
            "interview_id": r.get("interview_id"),
            "interview_token": r.get("interview_token"),
        })
    return jsonify({"reports": out})


@recruiter_bp.route("/api/reports/<report_id>/download", methods=["GET"])
@require_recruiter
def recruiter_api_report_download(report_id):
    from app.db import db
    from bson import ObjectId
    from app.utils import create_pdf_bytes
    from app.repositories import interviews_repo

    company_email = session.get("company_email", "")
    if db is None or not company_email:
        return jsonify({"error": "Not authenticated or DB unavailable."}), 401

    report_doc = db.reports.find_one({"_id": ObjectId(report_id)})
    if not report_doc:
        return jsonify({"error": "Report not found."}), 404

    interview_doc = db.interviews.find_one({"interview_id": report_doc.get("interview_id")})
    if not interview_doc or interview_doc.get("recruiter_email") != company_email:
        return jsonify({"error": "Access denied."}), 403

    report_data = report_doc.get("report_data", {})
    if not report_data:
        return jsonify({"error": "No report content available."}), 400

    user_info = report_data.get("user", {"name": report_doc.get("candidate_email", "Candidate" ,), "age": "N/A", "gender": "N/A"})
    pdf_bytes = create_pdf_bytes(
        user_info,
        report_data.get("profile", {}),
        report_data.get("question_details", []),
        report_data.get("overall_emotion_percentages", {}),
        report_data.get("behavioral_metrics", {}),
    )
    return Response(pdf_bytes, mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})
