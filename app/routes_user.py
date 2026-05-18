from flask import Blueprint, request, jsonify, session, render_template
from werkzeug.security import check_password_hash
from datetime import datetime

from app.auth.helpers import set_practice_session
from app.repositories import users_repo

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')

@user_bp.route('/portal', methods=['GET'])
def user_portal():
    return render_template('user_portal.html')

@user_bp.route('/signup', methods=['POST'])
def user_signup():
    from app.db import db
    if db is None: return jsonify({"error": "DB not connected"}), 500
    
    data = request.json
    email = data.get('email')
    
    if db.users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400
        
    users_repo.insert_practice_user(db, data.get('name'), email, data.get('password'))
    return jsonify({"message": "Account created. You can now take unlimited practice tests."}), 201

@user_bp.route('/login', methods=['POST'])
def user_login():
    from app.db import db
    data = request.json
    email = data.get('email')
    user = users_repo.find_practice_user_by_email(db, email)
    if user and check_password_hash(user['password_hash'], data.get('password')):
        set_practice_session(str(user['_id']), email, user.get('name', ''))
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401
