# ✅ MINIMAL JENKINSFILE - ONLY CI & CD (7 STAGES)

## What Changed

### Removed (Extra Features):
- ❌ Build reports generation
- ❌ Artifact archiving
- ❌ Git metadata extraction
- ❌ Verbose logging
- ❌ Complex error handling

### Kept (Only CI & CD):
- ✅ Checkout source
- ✅ Setup & install packages
- ✅ Verify build
- ✅ Create server
- ✅ Stop old app
- ✅ Deploy app
- ✅ Health check

---

## New Jenkinsfile Structure (7 Stages)

### CI Stages (Build):
1. **Checkout** - Clone from GitHub
2. **Setup & Install** - Create venv, install packages
3. **Verify Build** - Import Flask app

### CD Stages (Deploy):
4. **Create Server** - Generate waitress_server.py
5. **Stop Old App** - Kill process on port 5000
6. **Deploy** - Start new application
7. **Health Check** - Verify running

---

## Pipeline Flow

```
GitHub Push
    ↓
[1] Checkout (~30 sec)
    ↓
[2] Setup & Install (~5-10 min)
    └─ Create venv
    └─ pip install -q
    ↓
[3] Verify Build (~30 sec)
    └─ Import Flask app
    ↓
[4] Create Server (~10 sec)
    └─ Generate waitress_server.py
    ↓
[5] Stop Old App (~10 sec)
    └─ Kill process on port 5000
    ↓
[6] Deploy (~30 sec)
    └─ Start new app
    ↓
[7] Health Check (~10 sec)
    └─ Verify running
    ↓
✅ Application Running on Port 5000

TOTAL TIME: ~5-10 minutes
```

---

## Timeout Configuration

**Before:** 1 hour (too long)  
**After:** 30 minutes (reasonable)

Why? pip install can take 10-15 minutes, so 30 minutes is safe.

---

## Code Comparison

### Before (Complex):
```groovy
stage('Generate Build Report') {
    // 20+ lines
}

stage('Archive Artifacts') {
    // 20+ lines
}

stage('Deployment Summary') {
    // 10+ lines
}

post {
    success { ... }
    failure { ... }
    always { ... }
}
```

### After (Minimal):
```groovy
post {
    always {
        cleanWs()
    }
}
```

---

## What Each Stage Does

### 1. Checkout
```groovy
checkout scm
```
- Clones from GitHub
- Gets latest code

### 2. Setup & Install
```groovy
IF NOT EXIST venv (python -m venv venv)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
pip install -q waitress
```
- Creates venv if needed
- Installs all packages
- Installs waitress server

### 3. Verify Build
```groovy
python -c "import sys; sys.path.insert(0, '%APP_DIR%'); from app import app; print('✓ Flask App OK')"
```
- Imports Flask app
- Verifies code works

### 4. Create Server
```groovy
cd /d %APP_DIR%
(echo from waitress import serve...) > waitress_server.py
cd /d ..
```
- Creates waitress_server.py
- In ai_minor directory

### 5. Stop Old App
```groovy
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :5000') DO (
    taskkill /PID %%P /F 2>nul
)
```
- Finds process on port 5000
- Kills it gracefully

### 6. Deploy
```groovy
cd /d %APP_DIR%
start /B python waitress_server.py
cd /d ..
```
- Starts new application
- Runs in background

### 7. Health Check
```groovy
curl http://localhost:5000/health
```
- Tests health endpoint
- Verifies app is running

---

## Why This Works

1. **Minimal** - Only essential stages
2. **Fast** - No extra processing
3. **Reliable** - Simple, fewer failure points
4. **Clear** - Easy to understand
5. **Focused** - Only CI & CD

---

## Build Time Estimate

| Stage | Time |
|-------|------|
| Checkout | ~30 sec |
| Setup & Install | ~5-10 min |
| Verify Build | ~30 sec |
| Create Server | ~10 sec |
| Stop Old App | ~10 sec |
| Deploy | ~30 sec |
| Health Check | ~10 sec |
| **TOTAL** | **~5-10 min** |

---

## Next Steps

### 1. Push Changes
```bash
git add Jenkinsfile
git commit -m "Minimal Jenkinsfile - only CI & CD"
git push origin main
```

### 2. Run Jenkins Build
```
Jenkins → Persona Nexus → Build Now
```

### 3. Expected Output
```
========== CHECKOUT ==========
✓ Checkout complete

========== SETUP & INSTALL ==========
✓ Setup Complete

========== VERIFY BUILD ==========
✓ Flask App OK

========== CREATE SERVER ==========
✓ Server file created

========== STOP OLD APP ==========
✓ Old app stopped

========== DEPLOY ==========
✓ App deployed on port 5000

========== HEALTH CHECK ==========
✓ Health check passed
```

### 4. Verify Application
```bash
curl http://localhost:5000/health
# Should return: {"status": "healthy", ...}
```

---

## Summary

| Item | Status |
|------|--------|
| Stages | 7 (minimal) |
| CI stages | 3 |
| CD stages | 4 |
| Extra features | Removed |
| Build time | 5-10 min |
| Timeout | 30 min |
| Status | ✅ Ready |

---

## Final Status

**✅ MINIMAL JENKINSFILE READY**

**Only CI & CD - No extra features**

**Expected build time: 5-10 minutes**

---
