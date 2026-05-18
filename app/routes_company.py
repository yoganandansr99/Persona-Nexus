from flask import Blueprint, request, jsonify, session, render_template
from werkzeug.security import check_password_hash
from datetime import datetime
import logging

from app.auth.helpers import set_recruiter_session, ROLE_RECRUITER
from app.repositories import users_repo
from app.services.interview_service import create_interview_for_recruiter
from app.email import send_otp_email
import random

logger = logging.getLogger(__name__)

company_bp = Blueprint('company_bp', __name__, url_prefix='/company')

@company_bp.route('/dashboard', methods=['GET'])
def company_dashboard():
    return render_template('company_dashboard.html')

@company_bp.route('/test', methods=['GET'])
def test_otp():
    """Test endpoint to verify OTP flow"""
    logger.info('TEST ENDPOINT CALLED')
    return jsonify({
        "message": "Test OTP endpoint",
        "require_otp": True,
        "backend_status": "OK"
    }), 201

@company_bp.route('/signup', methods=['POST'])
def company_signup():
    from app.db import db
    logger.info('=== COMPANY SIGNUP CALLED ===')
    data = request.json
    email = data.get('email')
    logger.info(f'Signup request - Email: {email}, Company: {data.get("company_name")}')
    
    if not email:
        logger.warning('Email not provided')
        return jsonify({"error": "Email is required"}), 400

    if db.users.find_one({"email": email}):
        logger.warning(f'Company already exists: {email}')
        return jsonify({"error": "Company already exists"}), 400

    otp_code = str(random.randint(100000, 999999))
    logger.info(f'Generated OTP: {otp_code} for email: {email}')
    
    session['temp_company_data'] = {
        "email": email,
        "password": data.get('password'),
        "company_name": data.get('company_name')
    }
    session['company_verification_otp'] = otp_code
    session['company_otp_expiry'] = datetime.utcnow().timestamp() + 600

    try:
        logger.info(f'Sending OTP email to {email}')
        send_otp_email(email, otp_code)
        logger.info('OTP email sent successfully')
    except Exception as e:
        logger.error(f'Failed to send OTP email: {e}')
        return jsonify({"error": f"Failed to send OTP email. {str(e)}"}), 500

    logger.info('Returning require_otp: True')
    return jsonify({"message": "OTP sent", "require_otp": True}), 201

@company_bp.route('/verify_signup', methods=['POST'])
def verify_signup():
    from app.db import db
    logger.info('=== COMPANY VERIFY_SIGNUP CALLED ===')
    data = request.json
    user_otp = data.get('otp', '').strip()
    real_otp = session.get('company_verification_otp')
    expiry = session.get('company_otp_expiry', 0)

    logger.info(f'OTP verification - User OTP: {user_otp}, Real OTP: {real_otp}')

    if not real_otp:
        logger.warning('No pending registration found')
        return jsonify({"error": "No pending registration found. Please try registering again."}), 400

    if datetime.utcnow().timestamp() > expiry:
        logger.warning('OTP expired')
        session.pop('company_verification_otp', None)
        session.pop('temp_company_data', None)
        return jsonify({"error": "OTP expired. Please try registering again."}), 400

    if user_otp != real_otp:
        logger.warning(f'Invalid OTP - Expected: {real_otp}, Got: {user_otp}')
        return jsonify({"error": "Invalid OTP. Try again."}), 400

    comp_data = session.get('temp_company_data')
    if not comp_data:
        logger.warning('Session expired')
        return jsonify({"error": "Session expired."}), 400

    try:
        logger.info(f'Creating recruiter user for email: {comp_data["email"]}')
        users_repo.insert_recruiter_user(db, comp_data['email'], comp_data['password'], comp_data['company_name'])
        logger.info('Recruiter user created successfully')
    except Exception as e:
        logger.error(f'Failed to create recruiter user: {e}')
        return jsonify({"error": "Failed to create account. " + str(e)}), 500

    session.pop('company_verification_otp', None)
    session.pop('temp_company_data', None)
    session.pop('company_otp_expiry', None)

    logger.info('OTP verification successful')
    return jsonify({"message": "Account created successfully"}), 201

@company_bp.route('/login', methods=['POST'])
def company_login():
    from app.db import db
    logger.info('=== COMPANY LOGIN CALLED ===')
    data = request.json
    email = data.get('email')
    logger.info(f'Login attempt for email: {email}')
    
    company = users_repo.find_recruiter_by_email(db, email)
    if company and check_password_hash(company['password_hash'], data.get('password')):
        logger.info(f'Login successful for: {email}')
        set_recruiter_session(company['email'], company.get('company_name') or company.get('name'))
        return jsonify({"message": "Login successful", "company_email": company['email']})
    
    logger.warning(f'Login failed for: {email}')
    return jsonify({"error": "Invalid credentials"}), 401

@company_bp.route('/create_interview', methods=['POST'])
def create_interview():
    from app.db import db
    data = request.json or {}
    company_email = data.get('company_email')
    qs = data.get('custom_questions') or []
    result = create_interview_for_recruiter(
        db,
        company_email,
        qs,
        title=data.get('title') or '',
        candidate_email=data.get('candidate_email') or '',
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        duration_minutes=data.get('duration_minutes'),
        num_questions=data.get('num_questions'),
        difficulty=data.get('difficulty'),
    )
    return jsonify({
        "message": "Interview configured successfully.",
        "invite_link": result["invite_link"],
        "invite_link_token": result["invite_link_token"],
        "interview_id": result["interview_id"],
        "token": result["token"],
    }), 201