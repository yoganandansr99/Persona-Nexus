# 🎯 Persona Nexus — AI-Powered Interview Platform

> An intelligent, multi-portal interview assessment system powered by AI. Analyze personality, communication skills, and behavioral competencies through real-time video interviews.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1+-green?logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-4.17+-green?logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Email System](#-email-system)
- [Database Schema](#-database-schema)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎓 Practice Portal
- **Unlimited Mock Interviews** — Practice as many times as you want
- **AI-Powered Feedback** — Real-time personality analysis
- **Performance Tracking** — View historical scores and progress
- **Personality Reports** — Detailed PDF reports with insights
- **Analytics Dashboard** — Track improvement over time

### 👔 Recruiter Portal
- **Interview Management** — Create and schedule interviews
- **Candidate Invitations** — Send secure interview links via email
- **Real-Time Monitoring** — Track candidate progress
- **Report Generation** — Automated PDF reports with personality analysis
- **Malpractice Detection** — Automatic disqualification for suspicious behavior
- **Dashboard Analytics** — View all candidate submissions

### 🎬 Candidate Interview Portal
- **Secure Token-Based Access** — Unique interview links per candidate
- **Webcam & Microphone Support** — Full video/audio capture
- **Real-Time Monitoring** — Focus detection and anti-cheating measures
- **Question-by-Question Flow** — Structured interview experience
- **Auto-Skip Functionality** — Per-question timeout handling
- **Instant Report Generation** — PDF report after completion

### 🤖 AI Analysis Engine
- **Personality Archetype Detection** — 4 personality types (Yellow, Blue, Green, Red)
- **Emotion Recognition** — Real-time facial emotion analysis (Happy, Sad, Angry, Neutral, etc.)
- **Speech Analysis** — Tone, pitch, energy, and sentiment analysis
- **Behavioral Metrics** — Focus score, blink rate, head movement detection
- **Relevance Scoring** — AI-powered answer relevance evaluation
- **Communication Assessment** — Speech clarity, pace, and confidence metrics

---

## 🏗️ Architecture

### Multi-Portal Design
```
Persona Nexus
├── Practice Portal (/practice)
│   ├── Signup/Login
│   ├── Mock Interviews
│   ├── Performance Dashboard
│   └── Report History
├── Recruiter Portal (/recruiter)
│   ├── Signup/Login (OTP Verification)
│   ├── Interview Management
│   ├── Candidate Tracking
│   └── Analytics Dashboard
├── Candidate Interview (/interview)
│   ├── Token-Based Access
│   ├── Video Interview
│   ├── Real-Time Analysis
│   └── Report Generation
└── User Management (/user)
    ├── Authentication
    ├── Profile Management
    └── Session Handling
```

### Technology Stack

#### Backend
- **Framework**: Flask 3.1+ (Python 3.11+)
- **Database**: MongoDB 4.17+ (Atlas Cloud)
- **Email**: Flask-Mail with Gmail SMTP
- **Task Queue**: ThreadPoolExecutor (async email/analysis)

#### AI/ML
- **Speech Recognition**: OpenAI Whisper
- **Face Detection**: MediaPipe Face Mesh
- **Emotion Recognition**: DeepFace
- **Sentiment Analysis**: VADER Sentiment Analyzer
- **LLM**: Groq API (Llama 2 70B)

#### Frontend
- **Templating**: Jinja2
- **Styling**: CSS3 + Bootstrap
- **Video Capture**: WebRTC (getUserMedia API)
- **Real-Time Updates**: AJAX + Fetch API

#### DevOps
- **Server**: Gunicorn (production)
- **Environment**: Python venv
- **Version Control**: Git

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (free tier available)
- Gmail account (for email notifications)
- Groq API key (free tier available)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/persona-nexus.git
cd persona-nexus/ai_minor
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the `ai_minor/` directory:

```env
# Flask Configuration
SECRET_KEY=your_secret_key_here_change_in_production

# Email Configuration (Gmail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_specific_password

# Database Configuration (MongoDB Atlas)
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/AI_interview?retryWrites=true&w=majority

# AI/ML APIs
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Step 5: Run Application
```bash
python run.py
```

The application will start at `http://localhost:5000`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | `your_secret_key` |
| `MAIL_USERNAME` | Gmail address for sending emails | `your_email@gmail.com` |
| `MAIL_PASSWORD` | Gmail app-specific password | `lcza opcj apfp kaoi` |
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://...` |
| `GROQ_API_KEY` | Groq API key for LLM | `gsk_...` |
| `GOOGLE_API_KEY` | Google API key | `AIzaSy...` |

### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password in `MAIL_PASSWORD`

### MongoDB Setup
1. Create a free cluster at https://www.mongodb.com/cloud/atlas
2. Create a database user with read/write permissions
3. Whitelist your IP address
4. Copy the connection string to `MONGO_URI`

### Groq API Setup
1. Sign up at https://console.groq.com
2. Create an API key
3. Add to `GROQ_API_KEY`

---

## 📖 Usage

### For Practice Users
1. Navigate to `/practice`
2. Sign up with email and password
3. Verify OTP sent to your email
4. Start a mock interview
5. Answer questions with webcam/microphone enabled
6. Receive instant AI-powered personality report

### For Recruiters
1. Navigate to `/recruiter`
2. Sign up with company email
3. Verify OTP sent to your email
4. Create an interview:
   - Set candidate name and email
   - Choose difficulty level
   - Set start/end times
   - Select question count
5. Send invitation to candidate
6. Monitor candidate progress
7. Download report after completion

### For Candidates (Company Interview)
1. Receive email with interview link and token
2. Click link or navigate to `/interview`
3. Enter access token
4. Complete interview within scheduled time window
5. Receive report via email

---

## 📁 Project Structure

```
ai_minor/
├── app/
│   ├── __init__.py                 # Flask app initialization
│   ├── routes.py                   # Main routes & interview logic
│   ├── analysis.py                 # AI analysis engine
│   ├── email.py                    # Email notification system
│   ├── utils.py                    # Utility functions & PDF generation
│   ├── db.py                       # MongoDB connection
│   ├── auth/
│   │   ├── decorators.py           # Auth decorators
│   │   ├── helpers.py              # Auth helper functions
│   │   └── __init__.py
│   ├── practice/
│   │   ├── routes.py               # Practice portal routes
│   │   └── __init__.py
│   ├── recruiter/
│   │   ├── routes.py               # Recruiter portal routes
│   │   └── __init__.py
│   ├── candidate_portal/
│   │   ├── routes.py               # Candidate interview routes
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── users_repo.py           # User database operations
│   │   ├── interviews_repo.py      # Interview database operations
│   │   ├── reports_repo.py         # Report database operations
│   │   └── __init__.py
│   ├── services/
│   │   ├── interview_service.py    # Interview business logic
│   │   └── __init__.py
│   ├── routes_user.py              # User management routes
│   ├── routes_company.py           # Company management routes
│   ├── routes_candidate.py         # Candidate routes
│   └── __pycache__/
├── templates/
│   ├── layouts/
│   │   └── base.html               # Base template
│   ├── interview/
│   │   ├── start.html              # Interview start page
│   │   ├── access_gate.html        # Token verification
│   │   └── invalid_code.html       # Invalid token page
│   ├── practice/
│   │   ├── practice_landing.html   # Practice portal home
│   │   ├── practice_dashboard.html # Practice dashboard
│   │   └── practice_begin.html     # Practice interview start
│   ├── recruiter/
│   │   └── recruiter_dashboard.html # Recruiter dashboard
│   ├── interview.html              # Interview page
│   ├── report.html                 # Report display page
│   ├── processing.html             # Processing status page
│   ├── welcome.html                # Welcome page
│   ├── user_portal.html            # User portal
│   ├── company_dashboard.html      # Company dashboard
│   ├── verify_otp.html             # OTP verification
│   ├── disqualified.html           # Disqualification page
│   ├── about.html                  # About page
│   └── support.html                # Support page
├── static/
│   ├── css/
│   │   ├── theme.css               # Theme styles
│   │   └── style.css               # Main styles
│   ├── js/
│   │   └── site.js                 # JavaScript utilities
│   ├── portals/
│   │   └── practice.css            # Practice portal styles
│   ├── face_landmarker.task        # MediaPipe model
│   └── style.css                   # Additional styles
├── uploads/                        # Video/audio uploads
├── scripts/
│   └── migrate_mongo_collections.py # Database migration script
├── .env                            # Environment variables (not in git)
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
├── questions.json                  # Interview questions
└── interviews.db                   # SQLite backup (optional)
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | User signup |
| POST | `/login` | User login |
| POST | `/verify_otp` | Verify OTP |
| GET | `/logout` | User logout |

### Practice Portal
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/practice` | Practice portal home |
| GET | `/practice/dashboard` | Practice dashboard |
| POST | `/practice/start` | Start mock interview |
| POST | `/report` | Submit interview answers |
| GET | `/report_final` | View final report |
| GET | `/download_report` | Download PDF report |

### Recruiter Portal
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recruiter` | Recruiter portal home |
| GET | `/recruiter/dashboard` | Recruiter dashboard |
| POST | `/recruiter/create_interview` | Create interview |
| GET | `/recruiter/interviews` | List interviews |
| GET | `/recruiter/reports` | View reports |

### Candidate Interview
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/interview` | Interview access gate |
| POST | `/interview/verify_token` | Verify access token |
| GET | `/interview/start` | Start interview |
| POST | `/report` | Submit answers |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analysis_status/<task_id>` | Check analysis progress |
| POST | `/disqualify` | Disqualify candidate |

---

## 📧 Email System

### Email Types

#### 1. OTP Verification Email
- **Trigger**: User signup
- **Recipients**: Practice users, Recruiters
- **Content**: 6-digit OTP code, 10-minute expiry

#### 2. Welcome Email
- **Trigger**: OTP verification success
- **Recipients**: All verified users
- **Content**: Welcome message, tips for interview

#### 3. Interview Invitation Email
- **Trigger**: Recruiter creates interview
- **Recipients**: Candidate
- **Content**: Interview details, access token, start link

#### 4. Recruiter Confirmation Email
- **Trigger**: Interview created
- **Recipients**: Recruiter
- **Content**: Interview summary, candidate details

#### 5. Report Email
- **Trigger**: Interview completion
- **Recipients**: Candidate + Recruiter (if company interview)
- **Content**: Personality archetype, scores, PDF report attachment

#### 6. Malpractice Alert Email
- **Trigger**: Candidate disqualified
- **Recipients**: Candidate + Recruiter (if company interview)
- **Content**: Disqualification reason, no report generated

#### 7. Support Email
- **Trigger**: User submits support query
- **Recipients**: Admin
- **Content**: User details, query message

### Email Configuration
- **SMTP Server**: Gmail (smtp.gmail.com:587)
- **TLS**: Enabled
- **Max Workers**: 5 (ThreadPoolExecutor)
- **Async**: Non-blocking, returns immediately

---

## 🗄️ Database Schema

### MongoDB Collections

#### users
```json
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "hashed_password",
  "role": "practice_user|recruiter|candidate",
  "company_name": "Acme Corp",
  "created_at": ISODate,
  "verified": true,
  "otp_code": "123456",
  "otp_expiry": ISODate
}
```

#### interviews
```json
{
  "_id": ObjectId,
  "recruiter_id": ObjectId,
  "candidate_name": "Jane Smith",
  "candidate_email": "jane@example.com",
  "questions": ["Q1", "Q2", "Q3"],
  "difficulty": "medium",
  "start_time": ISODate,
  "end_time": ISODate,
  "duration_minutes": 30,
  "token": "unique_token",
  "pass_key": "pass_key",
  "status": "pending|in_progress|completed",
  "created_at": ISODate
}
```

#### reports
```json
{
  "_id": ObjectId,
  "interview_id": ObjectId,
  "candidate_id": ObjectId,
  "candidate_name": "Jane Smith",
  "personality_type": "Yellow",
  "overall_score": 85,
  "emotion_analysis": {
    "happy": 45,
    "neutral": 30,
    "sad": 15,
    "angry": 10
  },
  "behavioral_metrics": {
    "focus_score": 80,
    "blink_rate": 0.25,
    "head_movement": 15
  },
  "question_details": [...],
  "pdf_path": "/uploads/report_123.pdf",
  "created_at": ISODate,
  "malpractice_flag": false
}
```

---

## 🔍 Troubleshooting

### Email Not Sending
**Error**: `Working outside of application context`
**Solution**: Ensure `.env` has valid `MAIL_USERNAME` and `MAIL_PASSWORD`. Check Gmail app-specific password is correct.

### MongoDB Connection Failed
**Error**: `MongoDB connection failed`
**Solution**: 
1. Verify `MONGO_URI` in `.env`
2. Check IP whitelist in MongoDB Atlas
3. Ensure database user has correct permissions

### Whisper Model Not Loading
**Error**: `ERROR loading Whisper model`
**Solution**: 
```bash
pip install --upgrade openai-whisper
```

### MediaPipe Face Detection Issues
**Error**: `Face landmarker model not found`
**Solution**: Ensure `face_landmarker.task` exists in `static/` folder

### Groq API Rate Limit
**Error**: `Rate limit exceeded`
**Solution**: Add multiple Groq API keys in `.env`:
```env
GROQ_API_KEY=key1
GROQ_API_KEY_2=key2
GROQ_API_KEY_3=key3
```

### Port Already in Use
**Error**: `Address already in use`
**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

---

## 📝 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## 👨‍💻 Author

**Persona Nexus Development Team**

---

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- MediaPipe for face detection
- DeepFace for emotion recognition
- Groq for LLM inference
- MongoDB for database
- Flask community for excellent framework

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@personanexus.com
- Visit: https://personanexus.com/support

---

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time video streaming optimization
- [ ] Advanced analytics dashboard
- [ ] Interview scheduling calendar
- [ ] Candidate comparison reports
- [ ] Custom question templates
- [ ] Multi-language support
- [ ] API documentation (Swagger)
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

**Last Updated**: May 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
