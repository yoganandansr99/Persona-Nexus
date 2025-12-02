from threading import Thread
from flask_mail import Message
from app import app, mail

def send_async_email(app, msg):
    """Helper function to send email in a background thread."""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Failed to send email: {e}")

def get_email_template(title, body_content):
    """
    Generates a beautiful HTML email template with inline CSS.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f7f9; margin: 0; padding: 0; }}
            .email-container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-top: 20px; margin-bottom: 20px; }}
            .header {{ background-color: #4f46e5; padding: 30px 20px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; }}
            .content {{ padding: 40px 30px; color: #333333; line-height: 1.6; font-size: 16px; }}
            .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; }}
            .info-box {{ background-color: #eef2ff; border-left: 4px solid #4f46e5; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .otp-code {{ font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #4f46e5; text-align: center; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>AI Personality Profiler</h1>
            </div>
            <div class="content">
                <h2>{title}</h2>
                {body_content}
            </div>
            <div class="footer">
                <p>&copy; 2025 AI Personality Team. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- 1. SEND OTP EMAIL ---
def send_otp_email(user_email, otp_code):
    """Sends the 6-digit verification code."""
    if not user_email: return

    subject = "Verify Your Email - AI Interview"
    
    body_content = f"""
    <p>Hello,</p>
    <p>You are about to start your AI Personality Interview. To verify your identity, please use the following code:</p>
    
    <div class="otp-code">
        {otp_code}
    </div>
    
    <p>Enter this code on the website to proceed.</p>
    <p><em>This code is valid for 10 minutes.</em></p>
    """

    msg = Message(subject, recipients=[user_email])
    msg.html = get_email_template("Verification Required", body_content)
    
    Thread(target=send_async_email, args=(app, msg)).start()

# --- 2. SEND WELCOME EMAIL (Optional - can be sent after verification) ---
def send_welcome_email(user_email, user_name):
    """Sends a welcome confirmation."""
    if not user_email: return

    subject = "Welcome to Your AI Interview"
    
    body_content = f"""
    <p>Hello <strong>{user_name}</strong>,</p>
    <p>Your email has been verified and your session is ready.</p>
    
    <div class="info-box">
        <strong>💡 Tip:</strong> Ensure you are in a well-lit room and speak clearly for the best analysis results.
    </div>
    
    <p>Good luck!</p>
    """

    msg = Message(subject, recipients=[user_email])
    msg.html = get_email_template("Ready to Start", body_content)
    
    Thread(target=send_async_email, args=(app, msg)).start()

# --- 3. SEND REPORT EMAIL ---
def send_report_email(user_email, user_name, primary_color, pdf_bytes):
    """Sends the final report with PDF attachment."""
    if not user_email: return

    subject = f"Your Personality Analysis: {primary_color}"
    
    # Simple description map
    desc_map = {
        "Yellow": "Social & Enthusiastic",
        "Blue": "Empathetic & Relationship-oriented",
        "Green": "Analytical & Logical",
        "Red": "Assertive & Goal-oriented"
    }
    # Find matching description
    color_desc = "Unique Personality"
    for key, val in desc_map.items():
        if key in primary_color:
            color_desc = val
            break

    body_content = f"""
    <p>Hello <strong>{user_name}</strong>,</p>
    <p>Your interview analysis is complete! Our AI models have processed your video, audio, and text responses.</p>
    
    <div class="info-box">
        <strong>Your Archetype:</strong> {primary_color}<br>
        <em>{color_desc}</em>
    </div>
    
    <p>We have attached a detailed <strong>PDF Report</strong> containing:</p>
    <ul>
        <li>Your personality breakdown.</li>
        <li>Communication style analysis (Tone & Focus).</li>
        <li>Personalized growth suggestions.</li>
    </ul>
    
    <p>Thank you for using our platform!</p>
    """

    msg = Message(subject, recipients=[user_email])
    msg.html = get_email_template("Analysis Complete", body_content)
    
    # Attach PDF
    msg.attach("Personality_Report.pdf", "application/pdf", pdf_bytes)

    Thread(target=send_async_email, args=(app, msg)).start()
