import logging
from concurrent.futures import ThreadPoolExecutor
from flask_mail import Message
from app import app, mail

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=5)


def _send_in_thread(msg):
    """Send a pre-built Message object in a background thread with its own app context."""
    def _task():
        with app.app_context():
            try:
                mail.send(msg)
                logger.info(f"Email sent to {msg.recipients}")
            except Exception as e:
                logger.error(f"Failed to send email to {msg.recipients}: {e}", exc_info=True)
    executor.submit(_task)


def get_email_template(title, body_content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0; }}
            .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }}
            .header {{ background: linear-gradient(135deg, #4f46e5, #3b82f6); padding: 40px 20px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; }}
            .header p {{ margin: 10px 0 0 0; font-size: 16px; color: #e0e7ff; }}
            .content {{ padding: 40px 30px; color: #374151; line-height: 1.8; font-size: 16px; }}
            .content h2 {{ color: #111827; font-size: 22px; margin-top: 0; margin-bottom: 20px; border-bottom: 2px solid #f3f4f6; padding-bottom: 10px; }}
            .footer {{ background-color: #f9fafb; padding: 25px; text-align: center; font-size: 13px; color: #6b7280; border-top: 1px solid #e5e7eb; }}
            .info-box {{ background-color: #f5f3ff; border: 1px solid #ddd6fe; border-left: 5px solid #6d28d9; padding: 20px; margin: 25px 0; border-radius: 8px; }}
            .info-box strong {{ color: #4338ca; font-size: 18px; display: block; margin-bottom: 5px; }}
            .otp-code {{ font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #4f46e5; text-align: center; margin: 25px 0; background: #f0fdf4; padding: 15px; border-radius: 8px; border: 1px dashed #4ade80; }}
            .feature-list {{ padding-left: 20px; margin-bottom: 25px; }}
            .feature-list li {{ margin-bottom: 10px; color: #4b5563; }}
            .highlight {{ color: #4f46e5; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Persona Nexus</h1>
                <p>AI-Powered Interview Platform</p>
            </div>
            <div class="content">
                <h2>{title}</h2>
                {body_content}
            </div>
            <div class="footer">
                <p>&copy; 2025 Persona Nexus. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


# ── 1. OTP ────────────────────────────────────────────────────────────────
def send_otp_email(user_email, otp_code):
    if not user_email:
        return
    
    def _create_and_send():
        with app.app_context():
            try:
                body = f"""
                <p>Hello,</p>
                <p>Use the code below to verify your identity. It is valid for <strong>10 minutes</strong>.</p>
                <div class="otp-code">{otp_code}</div>
                <p>If you did not request this, ignore this email.</p>
                """
                msg = Message("Verify Your Email — Persona Nexus", recipients=[user_email])
                msg.html = get_email_template("Email Verification", body)
                mail.send(msg)
                logger.info(f"OTP email sent to {user_email}")
            except Exception as e:
                logger.error(f"Failed to send OTP email to {user_email}: {e}", exc_info=True)
    
    executor.submit(_create_and_send)


# ── 2. WELCOME ────────────────────────────────────────────────────────────
def send_welcome_email(user_email, user_name):
    if not user_email:
        return
    
    def _create_and_send():
        with app.app_context():
            try:
                body = f"""
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>Your email has been verified and your session is ready.</p>
                <div class="info-box">
                    <strong>💡 Tip:</strong> Ensure you are in a well-lit room and speak clearly for the best analysis results.
                </div>
                <p>Good luck!</p>
                """
                msg = Message("Welcome to Persona Nexus", recipients=[user_email])
                msg.html = get_email_template("Ready to Start", body)
                mail.send(msg)
                logger.info(f"Welcome email sent to {user_email}")
            except Exception as e:
                logger.error(f"Failed to send welcome email to {user_email}: {e}", exc_info=True)
    
    executor.submit(_create_and_send)


# ── 3. REPORT (candidate + recruiter copy) ────────────────────────────────
def send_report_email(user_email, user_name, primary_color, pdf_bytes,
                      overall_performance="N/A", avg_score="N/A",
                      is_candidate=False, company_email=None):
    if not user_email:
        return

    def _create_and_send():
        with app.app_context():
            try:
                desc_map = {
                    "Yellow": "Social & Enthusiastic",
                    "Blue":   "Empathetic & Relationship-oriented",
                    "Green":  "Analytical & Logical",
                    "Red":    "Assertive & Goal-oriented",
                }
                color_desc = next((v for k, v in desc_map.items() if k in primary_color), "Unique Personality")

                candidate_body = f"""
                <p>Hello <span class="highlight">{user_name}</span>,</p>
                <p>Congratulations on completing your AI Personality Interview!</p>
                <div class="info-box">
                    <strong>Your Primary Archetype: {primary_color}</strong>
                    <em style="font-size:15px;color:#4b5563;">{color_desc}</em><br><br>
                    <strong>Overall Performance: {overall_performance}/100</strong><br>
                    <strong>Average Score: {avg_score}/100</strong>
                </div>
                <p>Your detailed <strong>PDF Report</strong> is attached — it includes personality breakdown,
                communication analysis, and personalised growth tips.</p>
                """

                # Email to candidate
                candidate_msg = Message(
                    f"Your Interview Report — {primary_color}",
                    recipients=[user_email]
                )
                candidate_msg.html = get_email_template("Analysis Complete", candidate_body)
                candidate_msg.attach("Personality_Report.pdf", "application/pdf", pdf_bytes)
                mail.send(candidate_msg)
                logger.info(f"Report email sent to candidate {user_email}")

                # Email to recruiter (company interview only)
                if is_candidate and company_email:
                    recruiter_body = f"""
                    <p>Hello,</p>
                    <p>Candidate <strong>{user_name}</strong> has completed their interview.</p>
                    <div class="info-box">
                        <strong>Candidate Summary</strong>
                        <ul style="list-style:none;padding:0;margin:8px 0 0;">
                            <li>👤 <strong>Name:</strong> {user_name}</li>
                            <li>🎨 <strong>Archetype:</strong> {primary_color}</li>
                            <li>📊 <strong>Score:</strong> {overall_performance}/100</li>
                        </ul>
                    </div>
                    <p>The full PDF report is attached for your review.</p>
                    """
                    recruiter_msg = Message(
                        f"Candidate Report: {user_name}",
                        recipients=[company_email]
                    )
                    recruiter_msg.html = get_email_template("Candidate Analysis Report", recruiter_body)
                    recruiter_msg.attach("Candidate_Report.pdf", "application/pdf", pdf_bytes)
                    mail.send(recruiter_msg)
                    logger.info(f"Report email sent to recruiter {company_email}")
            except Exception as e:
                logger.error(f"Failed to send report email: {e}", exc_info=True)
    
    executor.submit(_create_and_send)


# ── 4. MALPRACTICE (candidate + recruiter) ────────────────────────────────
def send_malpractice_email(user_name, user_email, is_candidate=False, company_email=None):
    if not user_email:
        return

    def _create_and_send():
        with app.app_context():
            try:
                candidate_body = f"""
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>Your AI Personality Interview has been <strong>terminated and disqualified</strong>.</p>
                <div class="info-box" style="border-left:5px solid #ef4444;">
                    <strong style="color:#dc2626;">Reason for Disqualification</strong>
                    <p>Our system detected repeated violations of the focus monitoring rules (exceeded 10-second warning limit).</p>
                </div>
                <p>No report will be generated for this session.</p>
                """

                candidate_msg = Message(
                    "Interview Disqualified — Malpractice Detected",
                    recipients=[user_email]
                )
                candidate_msg.html = get_email_template("Interview Disqualified", candidate_body)
                mail.send(candidate_msg)
                logger.info(f"Malpractice email sent to candidate {user_email}")

                if is_candidate and company_email:
                    recruiter_body = f"""
                    <p>Hello,</p>
                    <p>A candidate was flagged for <strong>malpractice</strong> during their interview.</p>
                    <div class="info-box" style="border-left:5px solid #ef4444;">
                        <strong style="color:#dc2626;">Candidate Details</strong>
                        <ul style="list-style:none;padding:0;margin:8px 0 0;">
                            <li>👤 <strong>Name:</strong> {user_name}</li>
                            <li>✉️ <strong>Email:</strong> {user_email}</li>
                        </ul>
                    </div>
                    <p>The candidate exceeded the 10-second distraction limit. They have been disqualified and no report was generated.</p>
                    """
                    recruiter_msg = Message(
                        f"URGENT: Malpractice Detected — {user_name}",
                        recipients=[company_email]
                    )
                    recruiter_msg.html = get_email_template("Malpractice Alert", recruiter_body)
                    mail.send(recruiter_msg)
                    logger.info(f"Malpractice alert sent to recruiter {company_email}")
            except Exception as e:
                logger.error(f"Failed to send malpractice email: {e}", exc_info=True)
    
    executor.submit(_create_and_send)


# ── 5. INTERVIEW INVITATION (recruiter → candidate) ───────────────────────
def send_interview_invitation_email(candidate_email, candidate_name, recruiter_company,
                                    interview_title, interview_link, token,
                                    start_time="", end_time="", duration_minutes=None):
    if not candidate_email:
        return

    def _create_and_send():
        with app.app_context():
            try:
                duration_text = f"{duration_minutes} minutes" if duration_minutes else "No fixed duration"
                time_text = f"{start_time} – {end_time}" if start_time and end_time else "Flexible — use the link below"

                body = f"""
                <p>Hello <strong>{candidate_name or 'Candidate'}</strong>,</p>
                <p>You have been invited to complete an AI-powered interview for <strong>{recruiter_company}</strong>.</p>
                <div class="info-box">
                    <strong>📋 Interview Details</strong>
                    <ul style="list-style:none;padding:0;margin:10px 0 0;">
                        <li style="margin-bottom:8px;">🏢 <strong>Company:</strong> {recruiter_company}</li>
                        <li style="margin-bottom:8px;">📝 <strong>Title:</strong> {interview_title}</li>
                        <li style="margin-bottom:8px;">⏰ <strong>Scheduled:</strong> {time_text}</li>
                        <li style="margin-bottom:8px;">⌛ <strong>Duration:</strong> {duration_text}</li>
                        <li style="margin-bottom:8px;">🔑 <strong>Access Token:</strong>
                            <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px;">{token}</code>
                        </li>
                    </ul>
                </div>
                <p style="text-align:center;margin:30px 0;">
                    <a href="{interview_link}"
                       style="background:linear-gradient(135deg,#4f46e5,#6366f1);color:white;padding:14px 32px;
                              border-radius:50px;text-decoration:none;font-weight:700;font-size:16px;display:inline-block;">
                        Start Interview →
                    </a>
                </p>
                <p style="font-size:13px;color:#9ca3af;">
                    💡 <em>Find a quiet, well-lit room. Have your webcam and microphone ready before starting.</em>
                </p>
                """

                msg = Message(
                    f"Interview Invitation — {interview_title} at {recruiter_company}",
                    recipients=[candidate_email]
                )
                msg.html = get_email_template(f"Interview Invitation — {interview_title}", body)
                mail.send(msg)
                logger.info(f"Interview invitation sent to {candidate_email}")
            except Exception as e:
                logger.error(f"Failed to send interview invitation to {candidate_email}: {e}", exc_info=True)
    
    executor.submit(_create_and_send)


# ── 6. RECRUITER CONFIRMATION ─────────────────────────────────────────────
def send_recruiter_confirmation_email(recruiter_email, recruiter_company, candidate_email,
                                      candidate_name, interview_title, interview_link, token):
    if not recruiter_email:
        return

    def _create_and_send():
        with app.app_context():
            try:
                body = f"""
                <p>Hello <strong>{recruiter_company}</strong>,</p>
                <p>Your interview has been created and the invitation has been sent to the candidate.</p>
                <div class="info-box">
                    <strong>✅ Interview Summary</strong>
                    <ul style="list-style:none;padding:0;margin:10px 0 0;">
                        <li style="margin-bottom:8px;">📝 <strong>Title:</strong> {interview_title}</li>
                        <li style="margin-bottom:8px;">👤 <strong>Candidate:</strong> {candidate_name or 'Not specified'}</li>
                        <li style="margin-bottom:8px;">✉️ <strong>Candidate Email:</strong> {candidate_email or 'Not specified'}</li>
                        <li style="margin-bottom:8px;">🔑 <strong>Access Token:</strong>
                            <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px;">{token}</code>
                        </li>
                    </ul>
                </div>
                <p>Candidate interview link:<br>
                   <a href="{interview_link}" style="color:#4f46e5;word-break:break-all;">{interview_link}</a>
                </p>
                <p style="font-size:13px;color:#9ca3af;">
                    You will receive the candidate's report automatically once they complete the interview.
                </p>
                """

                msg = Message(
                    f"Interview Created — {interview_title}",
                    recipients=[recruiter_email]
                )
                msg.html = get_email_template("Interview Invitation Sent", body)
                mail.send(msg)
                logger.info(f"Recruiter confirmation sent to {recruiter_email}")
            except Exception as e:
                logger.error(f"Failed to send recruiter confirmation to {recruiter_email}: {e}", exc_info=True)
    
    executor.submit(_create_and_send)


# ── 7. SUPPORT ────────────────────────────────────────────────────────────
def send_support_email(user_name, user_email, query):
    def _create_and_send():
        with app.app_context():
            try:
                admin_email = "yoganandanyoganadan@gmail.com"
                body = f"""
                <p>Hello Admin,</p>
                <p>New support request from the Persona Nexus platform.</p>
                <div class="info-box">
                    <strong>Support Request</strong>
                    <ul style="list-style:none;padding:0;margin:10px 0 0;">
                        <li style="margin-bottom:8px;">👤 <strong>Name:</strong> {user_name}</li>
                        <li style="margin-bottom:8px;">✉️ <strong>Email:</strong> {user_email}</li>
                    </ul>
                    <hr style="border:0;border-top:1px solid #ddd6fe;margin:15px 0;">
                    <p style="margin:0;white-space:pre-wrap;"><strong>Query:</strong><br>{query}</p>
                </div>
                """
                msg = Message(f"Support Query from {user_name}", recipients=[admin_email])
                msg.html = get_email_template("New Support Ticket", body)
                mail.send(msg)
                logger.info(f"Support email sent for {user_name}")
            except Exception as e:
                logger.error(f"Failed to send support email: {e}", exc_info=True)
    
    executor.submit(_create_and_send)
