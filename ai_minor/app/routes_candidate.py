from flask import Blueprint, request, session, redirect, url_for

candidate_bp = Blueprint('candidate_bp', __name__, url_prefix='/candidate')

@candidate_bp.route('/join/<interview_id>', methods=['GET'])
def join_interview(interview_id):
    from app.db import db
    interview = db.interviews.find_one({"interview_id": interview_id})
    
    if not interview:
        return "Interview link is invalid or expired.", 404
        
    # Mark this specific session as a company-sponsored candidate
    session['is_candidate'] = True
    session['company_email'] = interview['company_email']
    session['custom_questions'] = interview.get('custom_questions', [])
    session['is_dynamic'] = interview.get('is_dynamic', False)
    
    session["current_interview_id"] = interview_id
    session["interview_token"] = None
    return redirect(url_for('welcome', portal_entry='1'))