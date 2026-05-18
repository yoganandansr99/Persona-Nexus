# 🎯 Persona Chroma — Project Overview

**AI-Powered Interview Platform** | Multi-Portal Architecture | Production Ready

---

## What is Persona Chroma?

An intelligent interview assessment system that analyzes personality, communication skills, and behavioral competencies through AI-powered video interviews. Three independent portals serve different users: practice students, recruiters, and candidates.

---

## 🎓 Three Main Portals

### 1. Practice Portal (`/practice`)
- Unlimited mock interviews for skill development
- Real-time AI personality analysis
- Performance tracking and historical reports
- Personality archetype classification (Yellow, Blue, Green, Red)

### 2. Recruiter Portal (`/recruiter`)
- Create and manage company interviews
- Send secure interview invitations to candidates
- Monitor candidate progress in real-time
- Receive automated reports with personality analysis
- Detect malpractice and disqualify candidates

### 3. Candidate Interview (`/interview`)
- Secure token-based interview access
- Webcam + microphone video recording
- Real-time focus monitoring (anti-cheating)
- Question-by-question flow with auto-skip
- Instant PDF report generation

---

## 🤖 AI Analysis Engine

**Personality Detection**: 4 archetypes (Yellow/Social, Blue/Empathetic, Green/Analytical, Red/Assertive)

**Emotion Recognition**: Happy, Sad, Angry, Neutral, Surprised, Fearful, Disgusted (DeepFace)

**Speech Analysis**: Tone, pitch, energy, sentiment, clarity (Whisper + VADER)

**Behavioral Metrics**: Focus score, blink rate, head movement (MediaPipe)

**Relevance Scoring**: AI-powered answer evaluation (Groq LLM)

---

## 📧 Email System

- OTP verification (10-minute expiry)
- Interview invitations with secure tokens
- Automated report delivery (PDF attached)
- Malpractice alerts to candidates and recruiters
- Support ticket notifications

---

## 🗄️ Tech Stack

**Backend**: Flask 3.1 + Python 3.11  
**Database**: MongoDB (Atlas Cloud)  
**AI/ML**: Whisper, MediaPipe, DeepFace, Groq LLM  
**Email**: Flask-Mail + Gmail SMTP  
**Frontend**: Jinja2 + HTML/CSS + JavaScript  
**Async**: ThreadPoolExecutor (5 workers)

---

## 🔐 Security Features

- Email-based OTP authentication
- Role-based access control (practice_user, recruiter, candidate)
- Token-based interview access
- Session management
- Real-time malpractice detection
- Automatic disqualification (10-second distraction limit)

---

## 📊 Database Schema

**users**: name, email, password_hash, role, company_name, verified, otp_code  
**interviews**: recruiter_id, candidate_name, questions, difficulty, start_time, end_time, token  
**reports**: interview_id, candidate_id, personality_type, scores, emotion_analysis, pdf_path

---

## ✨ Key Features

✅ Unlimited practice interviews  
✅ Professional PDF reports with personality insights  
✅ Real-time emotion and behavior analysis  
✅ Automatic malpractice detection  
✅ Interview scheduling with time windows  
✅ Per-question auto-skip after timeout  
✅ Dual email notifications (candidate + recruiter)  
✅ Performance analytics dashboard  

---

## 🚀 Status

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Email System**: Fixed (app context resolved)  
**All Features**: Implemented and tested  
**Documentation**: Complete (8 files, 87.7 KB)

---

## 📖 Quick Start

1. **Setup**: `pip install -r requirements.txt` → Configure `.env` → `python run.py`
2. **Practice**: Visit `/practice` → Signup → Take mock interview → Get report
3. **Recruiter**: Visit `/recruiter` → Create interview → Send to candidate → Monitor
4. **Candidate**: Receive email → Click link → Enter token → Complete interview

---

## 🎯 Use Cases

- **Students**: Practice interviews, get personality feedback, improve communication
- **Companies**: Screen candidates, assess personality fit, generate reports
- **Recruiters**: Manage interviews, track candidates, make data-driven decisions

---

**Created**: May 2026 | **Ready for GitHub** ✅
