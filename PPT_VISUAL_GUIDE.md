# 🎨 PERSONA NEXUS - PPT VISUAL GUIDE & DIAGRAMS

## ARCHITECTURE DIAGRAMS

### System Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                     PERSONA NEXUS PLATFORM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Practice   │  │  Recruiter   │  │  Candidate   │           │
│  │   Portal     │  │   Portal     │  │  Interview   │           │
│  │  /practice   │  │  /recruiter  │  │ /interview   │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                    │
│         └─────────────────┼─────────────────┘                    │
│                           │                                      │
│                    ┌──────▼──────┐                               │
│                    │  Flask App  │                               │
│                    │  (Python)   │                               │
│                    └──────┬──────┘                               │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│    ┌────▼────┐    ┌──────▼──────┐   ┌─────▼─────┐              │
│    │ MongoDB │    │ Email System │   │ AI Engine │              │
│    │ (Atlas) │    │ (Gmail SMTP) │   │ (Groq)    │              │
│    └─────────┘    └─────────────┘   └───────────┘              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Three Portal Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONA NEXUS PORTALS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PRACTICE PORTAL              RECRUITER PORTAL                   │
│  ┌──────────────────┐        ┌──────────────────┐               │
│  │ Students/Users   │        │ Companies/HR     │               │
│  ├──────────────────┤        ├──────────────────┤               │
│  │ • Signup/Login   │        │ • Signup/Login   │               │
│  │ • Mock Interview │        │ • Create Intv    │               │
│  │ • Get Report     │        │ • Send Invite    │               │
│  │ • Track Progress │        │ • Monitor Cand   │               │
│  │ • View History   │        │ • View Reports   │               │
│  └──────────────────┘        └──────────────────┘               │
│                                                                   │
│              CANDIDATE INTERVIEW PORTAL                          │
│              ┌──────────────────────────┐                        │
│              │ Candidates               │                        │
│              ├──────────────────────────┤                        │
│              │ • Receive Email Link     │                        │
│              │ • Enter Token            │                        │
│              │ • Complete Interview     │                        │
│              │ • Get Report             │                        │
│              └──────────────────────────┘                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### AI Analysis Engine
```
┌─────────────────────────────────────────────────────────────────┐
│                    AI ANALYSIS ENGINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUT: Video Interview                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Webcam Feed (Video)                                    │   │
│  │ • Microphone Feed (Audio)                                │   │
│  │ • Candidate Responses (Text)                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ANALYSIS MODULES                                         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  1. PERSONALITY DETECTION (Groq LLM)                    │   │
│  │     └─ Yellow, Blue, Green, Red Archetypes             │   │
│  │                                                          │   │
│  │  2. EMOTION RECOGNITION (DeepFace)                      │   │
│  │     └─ Happy, Sad, Angry, Neutral, Surprised, etc.     │   │
│  │                                                          │   │
│  │  3. SPEECH ANALYSIS (Whisper + VADER)                   │   │
│  │     └─ Tone, Pitch, Energy, Sentiment, Clarity         │   │
│  │                                                          │   │
│  │  4. BEHAVIORAL METRICS (MediaPipe)                      │   │
│  │     └─ Focus Score, Blink Rate, Head Movement          │   │
│  │                                                          │   │
│  │  5. ANSWER RELEVANCE (Groq LLM)                         │   │
│  │     └─ Relevance Scoring, Quality Assessment           │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  OUTPUT: Comprehensive Report                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Personality Type                                       │   │
│  │ • Overall Score (0-100)                                  │   │
│  │ • Emotion Analysis (%)                                   │   │
│  │ • Behavioral Metrics                                     │   │
│  │ • Question-by-Question Breakdown                         │   │
│  │ • PDF Report (Downloadable)                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack Layers
```
┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ FRONTEND LAYER                                          │    │
│  │ • Jinja2 Templates                                      │    │
│  │ • HTML5 + CSS3 + Bootstrap                              │    │
│  │ • JavaScript (AJAX, WebRTC)                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ APPLICATION LAYER                                       │    │
│  │ • Flask 3.1+ (Python 3.11+)                             │    │
│  │ • Blueprints (Modular Architecture)                     │    │
│  │ • ThreadPoolExecutor (Async Tasks)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ AI/ML LAYER                                             │    │
│  │ • Whisper (Speech Recognition)                          │    │
│  │ • MediaPipe (Face Detection)                            │    │
│  │ • DeepFace (Emotion Recognition)                        │    │
│  │ • VADER (Sentiment Analysis)                            │    │
│  │ • Groq LLM (Answer Evaluation)                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ DATA LAYER                                              │    │
│  │ • MongoDB Atlas (Cloud Database)                        │    │
│  │ • Collections: users, interviews, reports              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ INFRASTRUCTURE LAYER                                    │    │
│  │ • Waitress WSGI Server                                  │    │
│  │ • Python venv (Isolation)                               │    │
│  │ • Gmail SMTP (Email)                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Jenkins CI/CD Pipeline
```
┌─────────────────────────────────────────────────────────────────┐
│                  JENKINS CI/CD PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  GitHub Push Event                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ CI STAGES (Build & Test)                                │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ 1. Checkout Source                                      │    │
│  │    └─ Clone from GitHub                                 │    │
│  │                                                          │    │
│  │ 2. Setup Python Environment                             │    │
│  │    └─ Create venv, install packages                     │    │
│  │                                                          │    │
│  │ 3. Code Quality Check                                   │    │
│  │    └─ Compile Python files                              │    │
│  │                                                          │    │
│  │ 4. Run Tests                                            │    │
│  │    └─ Execute pytest                                    │    │
│  │                                                          │    │
│  │ 5. Build Verification                                   │    │
│  │    └─ Import Flask app                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ CD STAGES (Deploy)                                      │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ 6. Create Waitress Server                               │    │
│  │    └─ Generate server file                              │    │
│  │                                                          │    │
│  │ 7. Stop Old Application                                 │    │
│  │    └─ Kill previous process                             │    │
│  │                                                          │    │
│  │ 8. Deploy Application                                   │    │
│  │    └─ Start new server                                  │    │
│  │                                                          │    │
│  │ 9. Health Check                                         │    │
│  │    └─ Verify running                                    │    │
│  │                                                          │    │
│  │ 10. Generate Build Report                               │    │
│  │     └─ Create report                                    │    │
│  │                                                          │    │
│  │ 11. Archive Artifacts                                   │    │
│  │     └─ Save build files                                 │    │
│  │                                                          │    │
│  │ 12. Deployment Summary                                  │    │
│  │     └─ Print summary                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│         │                                                        │
│         ▼                                                        │
│  ✅ Application Running on Port 5000                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### DevOps Tools Ecosystem
```
┌─────────────────────────────────────────────────────────────────┐
│                   DEVOPS TOOLS ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │     GIT      │      │    GITHUB    │      │   JENKINS    │   │
│  │              │      │              │      │              │   │
│  │ • Version    │      │ • Repository │      │ • CI/CD      │   │
│  │   Control    │      │ • Webhook    │      │ • Pipeline   │   │
│  │ • Branching  │      │ • Collab     │      │ • Automation │   │
│  └──────────────┘      └──────────────┘      └──────────────┘   │
│         │                     │                     │            │
│         └─────────────────────┼─────────────────────┘            │
│                               │                                  │
│                    ┌──────────▼──────────┐                       │
│                    │   BUILD PROCESS     │                       │
│                    ├─────────────────────┤                       │
│                    │ • Python venv       │                       │
│                    │ • pip install       │                       │
│                    │ • Code Quality      │                       │
│                    │ • Testing           │                       │
│                    └──────────────────────┘                       │
│                               │                                  │
│         ┌─────────────────────┼─────────────────────┐            │
│         │                     │                     │            │
│    ┌────▼────┐         ┌─────▼──────┐      ┌──────▼────┐       │
│    │ WAITRESS │         │  MONGODB   │      │   EMAIL   │       │
│    │  SERVER  │         │   ATLAS    │      │   GMAIL   │       │
│    │          │         │            │      │           │       │
│    │ • WSGI   │         │ • Database │      │ • SMTP    │       │
│    │ • Port   │         │ • Cloud    │      │ • Async   │       │
│    │ • Process│         │ • Backup   │      │ • Notify  │       │
│    └──────────┘         └────────────┘      └───────────┘       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA FLOW DIAGRAM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  USER INTERACTION                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. User visits /practice or /recruiter                  │   │
│  │ 2. Signup/Login with email                              │   │
│  │ 3. Receive OTP via email                                │   │
│  │ 4. Verify OTP                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  INTERVIEW PROCESS                                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Start interview                                       │   │
│  │ 2. Enable webcam/microphone                              │   │
│  │ 3. Answer questions                                      │   │
│  │ 4. Real-time analysis (focus, emotion)                   │   │
│  │ 5. Submit answers                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  AI ANALYSIS                                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Process video/audio                                   │   │
│  │ 2. Extract features (emotion, behavior)                  │   │
│  │ 3. Analyze speech (tone, sentiment)                      │   │
│  │ 4. Evaluate answers (relevance)                          │   │
│  │ 5. Generate personality profile                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  REPORT GENERATION                                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Create PDF report                                     │   │
│  │ 2. Store in MongoDB                                      │   │
│  │ 3. Send email notification                               │   │
│  │ 4. Display on dashboard                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  USER RECEIVES REPORT                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Personality Type                                       │   │
│  │ • Overall Score                                          │   │
│  │ • Emotion Analysis                                       │   │
│  │ • Behavioral Metrics                                     │   │
│  │ • Recommendations                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## COMPARISON CHARTS

### Traditional vs AI-Powered Interviews
```
TRADITIONAL INTERVIEWS          VS          AI-POWERED (PERSONA NEXUS)
─────────────────────────────────────────────────────────────────
❌ Subjective evaluation         ✅ Objective AI analysis
❌ Time-consuming                ✅ Instant reports
❌ Limited insights              ✅ Comprehensive analysis
❌ Inconsistent criteria         ✅ Standardized metrics
❌ Manual report writing         ✅ Automated PDF generation
❌ No real-time monitoring       ✅ Real-time focus detection
❌ Difficult to detect cheating  ✅ Automatic malpractice detection
❌ Scalability issues            ✅ Highly scalable
```

### Portal Comparison
```
┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Feature         │ Practice Portal  │ Recruiter Portal │ Candidate Portal │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Users           │ Students         │ Companies/HR     │ Candidates       │
│ Purpose         │ Practice         │ Screening        │ Interview        │
│ Interviews      │ Unlimited        │ Limited          │ Single           │
│ Reports         │ Instant          │ Instant          │ Instant          │
│ Monitoring      │ Self             │ Real-time        │ Real-time        │
│ Malpractice     │ Detected         │ Detected         │ Detected         │
│ Cost            │ Free/Paid        │ Paid             │ Free             │
└─────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

---

## KEY METRICS & STATISTICS

### Project Size
```
Code Files:        35+ Python files
Templates:         20+ HTML templates
Stylesheets:       3 CSS files
Scripts:           1 JavaScript file
Documentation:     20+ markdown files
Total Size:        ~500 KB code + 87.7 KB docs
```

### Dependencies
```
Python Packages:   35+ packages
Framework:         Flask 3.1+
Database:          MongoDB 4.17+
AI/ML Libraries:   5 major libraries
Email:             Flask-Mail + Gmail
```

### Pipeline
```
Jenkins Stages:    12 stages
CI Stages:         5 stages
CD Stages:         4 stages
Post Actions:      3 actions
Automation:        100%
```

---

## TIMELINE & MILESTONES

```
May 2026
├─ Week 1: Project Setup & Architecture
│  └─ ✅ Flask app, MongoDB, AI integration
├─ Week 2: Portal Development
│  └─ ✅ Practice, Recruiter, Candidate portals
├─ Week 3: AI Engine & Analysis
│  └─ ✅ Personality, emotion, speech analysis
├─ Week 4: Email System & Security
│  └─ ✅ OTP, notifications, authentication
├─ Week 5: Testing & Bug Fixes
│  └─ ✅ Email context fix, dependency resolution
├─ Week 6: DevOps & CI/CD
│  └─ ✅ Jenkins pipeline, Jenkinsfile, automation
├─ Week 7: Documentation
│  └─ ✅ 20+ markdown files, API docs, guides
└─ Week 8: Production Ready
   └─ ✅ Version 1.0.0 released
```

---

## QUICK REFERENCE CARDS

### For Developers
```
Setup:
  git clone <repo>
  cd ai_minor
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  
Configure:
  Create .env with required variables
  
Run:
  python run.py
  
Access:
  http://localhost:5000
```

### For DevOps
```
Build:
  Jenkins → Build Now
  
Monitor:
  Jenkins Console Output
  
Deploy:
  Automatic via CI/CD pipeline
  
Health Check:
  curl http://localhost:5000/health
```

### For Users
```
Practice:
  /practice → Signup → Interview → Report
  
Recruiter:
  /recruiter → Create Interview → Send Link → Monitor
  
Candidate:
  Email Link → Enter Token → Interview → Report
```

---

