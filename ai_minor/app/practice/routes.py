"""Practice portal — unlimited mock interviews; reuses core /initiate → /interview pipeline."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import random

from app.auth.decorators import require_practice_user_page, require_json
from app.auth.helpers import set_practice_session, practice_user_logged_in
from app.repositories import users_repo, reports_repo
from app.email import send_otp_email
from werkzeug.security import check_password_hash

practice_bp = Blueprint("practice", __name__, url_prefix="/practice")


@practice_bp.route("/")
def practice_home():
    return render_template(
        "practice/practice_landing.html", logged_in=practice_user_logged_in()
    )


@practice_bp.route("/dashboard")
@require_practice_user_page
def practice_dashboard():
    from app.db import db

    rows = []
    email = session.get("user_email") or ""
    if db is not None and email:
        try:
            rows = reports_repo.list_reports_for_email(db, email, limit=40)
        except Exception:
            rows = []
    return render_template(
        "practice/practice_dashboard.html",
        user_email=email,
        user_name=session.get("user_name", ""),
        history=rows,
    )


@practice_bp.route("/api/signup", methods=["POST"])
@require_json
def practice_api_signup():
    from app.db import db

    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    if db.users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400
    
    otp_code = str(random.randint(100000, 999999))
    session['temp_practice_data'] = {
        "name": name,
        "email": email,
        "password": password,
    }
    session['practice_verification_otp'] = otp_code
    session['practice_otp_expiry'] = datetime.utcnow().timestamp() + 600

    try:
        send_otp_email(email, otp_code)
    except Exception as e:
        return jsonify({"error": f"Failed to send OTP email. {str(e)}"}), 500

    return jsonify({"message": "OTP sent to email", "require_otp": True}), 201


@practice_bp.route("/api/verify_signup", methods=["POST"])
@require_json
def practice_api_verify_signup():
    from app.db import db

    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    
    data = request.get_json() or {}
    user_otp = data.get('otp', '').strip()
    real_otp = session.get('practice_verification_otp')
    expiry = session.get('practice_otp_expiry', 0)

    if not real_otp:
        return jsonify({"error": "No pending registration found. Please try registering again."}), 400

    if datetime.utcnow().timestamp() > expiry:
        session.pop('practice_verification_otp', None)
        session.pop('temp_practice_data', None)
        return jsonify({"error": "OTP expired. Please try registering again."}), 400

    if user_otp != real_otp:
        return jsonify({"error": "Invalid OTP. Try again."}), 400

    practice_data = session.get('temp_practice_data')
    if not practice_data:
        return jsonify({"error": "Session expired."}), 400

    try:
        uid = users_repo.insert_practice_user(db, practice_data['name'], practice_data['email'], practice_data['password'])
    except Exception as e:
        return jsonify({"error": "Failed to create account. " + str(e)}), 500

    session.pop('practice_verification_otp', None)
    session.pop('temp_practice_data', None)
    session.pop('practice_otp_expiry', None)

    return jsonify({"message": "Account created successfully", "user_id": str(uid)}), 201


@practice_bp.route("/api/login", methods=["POST"])
@require_json
def practice_api_login():
    from app.db import db

    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    u = users_repo.find_practice_user_by_email(db, email)
    if not u or not check_password_hash(u["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401
    set_practice_session(str(u["_id"]), email, u.get("name", ""))
    return jsonify({"message": "Login successful"})


@practice_bp.route("/api/logout", methods=["POST"])
def practice_api_logout():
    session.pop("logged_in_user", None)
    session.pop("portal_role", None)
    session.pop("user_email", None)
    session.pop("user_name", None)
    return jsonify({"message": "Logged out"})


@practice_bp.route("/begin")
@require_practice_user_page
def practice_begin_interview():
    """Form POSTs to legacy /initiate (OTP + existing interview pipeline)."""
    name = session.get("user_name") or ""
    email = session.get("user_email") or ""
    return render_template(
        "practice/practice_begin.html", default_name=name, default_email=email
    )

@practice_bp.route("/start_session", methods=["POST"])
@require_practice_user_page
def practice_start_session():
    name = request.form.get("username") or session.get("user_name", "")
    email = request.form.get("email") or session.get("user_email", "")
    age = request.form.get("age", "")
    gender = request.form.get("gender", "")
    num_questions = int(request.form.get("num_questions", 3))
    
    session["user_data"] = {
        "name": name,
        "email": email,
        "age": age,
        "gender": gender,
    }
    session["num_questions"] = num_questions
    session["is_practice"] = True
    
    # Remove any company state if present
    session.pop("is_candidate", None)
    session.pop("company_email", None)
    session.pop("interview_token", None)
    session.pop("current_interview_id", None)
    session.pop("custom_questions", None)
    
    from flask import url_for, redirect
    return redirect(url_for("start_interview_session"))
