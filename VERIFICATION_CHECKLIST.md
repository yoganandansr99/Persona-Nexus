# Build Fix Verification Checklist

## Pre-Build Verification (Local Testing)

### 1. Check File Modifications
- [ ] `ai_minor/app/__init__.py` - Whisper import wrapped in try-except
- [ ] `Jenkinsfile` - 3 stages fixed (Build Verification, Create Waitress, Deploy)
- [ ] `requirements.txt` - Whisper version updated to >=20231117

**How to verify:**
```bash
# Check __init__.py
git diff ai_minor/app/__init__.py

# Check Jenkinsfile
git diff Jenkinsfile

# Check requirements.txt
git diff requirements.txt
```

### 2. Verify Python Environment Locally
```bash
# Navigate to project
cd d:\AI_minor

# Create venv
python -m venv test_venv

# Activate
test_venv\Scripts\activate.bat

# Install requirements
pip install -r requirements.txt

# Test Flask import
python -c "import sys; sys.path.insert(0, 'ai_minor'); from app import app; print('✓ Flask app imports successfully')"

# Clean up
deactivate
rmdir /s /q test_venv
```

Expected output: `✓ Flask app imports successfully`

---

## Jenkins Build Verification

### Stage 1: Checkout Source
- [ ] Build starts successfully
- [ ] Source code checked out from GitHub
- [ ] Git commit info captured

**Expected output:**
```
CHECKING OUT SOURCE CODE
========================================
```

### Stage 2: Setup Python Environment
- [ ] Virtual environment created
- [ ] Python upgraded
- [ ] All packages installed
- [ ] Waitress installed

**Expected output:**
```
SETTING UP PYTHON ENVIRONMENT
========================================
PYTHON ENVIRONMENT READY
========================================
```

**If fails:** Check if FFmpeg is installed (required for whisper)

### Stage 3: Code Quality Check
- [ ] All Python files compile successfully
- [ ] No syntax errors

**Expected output:**
```
RUNNING CODE QUALITY CHECK
========================================
CODE QUALITY CHECK COMPLETED
========================================
```

### Stage 4: Run Tests
- [ ] Tests run (or skip if no tests folder)

**Expected output:**
```
RUNNING TESTS
========================================
TEST STAGE COMPLETED
========================================
```

### Stage 5: Build Verification
- [ ] Flask app imports successfully
- [ ] No "ModuleNotFoundError: No module named 'whisper'" error

**Expected output:**
```
VERIFYING APPLICATION BUILD
========================================
Flask App Imported Successfully
BUILD VERIFICATION SUCCESSFUL
========================================
```

**If fails:** Check `ai_minor/app/__init__.py` has whisper try-except

### Stage 6: Create Waitress Server File
- [ ] File created at `ai_minor\waitress_server.py`
- [ ] File content displayed correctly

**Expected output:**
```
CREATING WAITRESS SERVER
========================================
from waitress import serve
from app import app

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
WAITRESS SERVER FILE CREATED
========================================
```

**If fails:** Check Jenkinsfile uses `%APP_DIR%\waitress_server.py`

### Stage 7: Stop Old Application
- [ ] Old process killed (if running)
- [ ] Port 5000 freed

**Expected output:**
```
STOPPING OLD APPLICATION
========================================
OLD APPLICATION STOPPED
========================================
```

### Stage 8: Deploy Application
- [ ] Application starts successfully
- [ ] Waits 10 seconds for startup

**Expected output:**
```
DEPLOYING APPLICATION
========================================
APPLICATION DEPLOYED SUCCESSFULLY
========================================
```

**If fails:** Check waitress_server.py was created in previous stage

### Stage 9: Health Check
- [ ] Health endpoint responds
- [ ] HTTP 200 status

**Expected output:**
```
RUNNING HEALTH CHECK
========================================
APPLICATION IS RUNNING SUCCESSFULLY
========================================
```

**If fails:** Check `/health` endpoint exists in `app/routes.py`

### Stage 10: Generate Build Report
- [ ] Report generated with build info

**Expected output:**
```
GENERATING BUILD REPORT
========================================
PERSONA NEXUS BUILD REPORT
========================================
Build Number  : [number]
Build URL     : [url]
Git Commit    : [hash]
Commit Author : [name]
Commit Msg    : [message]
Deployment    : SUCCESS
Port          : 5000
Timestamp     : [date] [time]
========================================
```

### Stage 11: Archive Artifacts
- [ ] Artifacts archived successfully

**Expected output:**
```
ARCHIVING ARTIFACTS
========================================
ARTIFACTS ARCHIVED
========================================
```

### Stage 12: Deployment Summary
- [ ] Pipeline completes successfully

**Expected output:**
```
CI/CD PIPELINE COMPLETED SUCCESSFULLY
========================================
Application URL: http://localhost:5000
Build Number: [number]
Git Commit: [hash]
Author: [name]
========================================
```

---

## Post-Build Verification

### 1. Application Running
```bash
# Check if Flask app is running
curl http://localhost:5000/health

# Expected response: 200 OK with health status
```

### 2. Verify Waitress Server File
```bash
# Check file exists
type ai_minor\waitress_server.py

# Expected: File content displayed
```

### 3. Check Build Artifacts
- [ ] `build_artifacts/` folder created
- [ ] Contains: `build_report.txt`, `Jenkinsfile`, `requirements.txt`, `app/` folder

### 4. Verify No Errors in Console
- [ ] No "ModuleNotFoundError" messages
- [ ] No "The system cannot find the file specified" messages
- [ ] No path-related errors

---

## Troubleshooting Guide

### Issue: "ModuleNotFoundError: No module named 'whisper'"
**Status:** ❌ FAILED - Whisper import not wrapped
**Solution:** 
1. Verify `ai_minor/app/__init__.py` has try-except around whisper import
2. Check git diff shows the change
3. Commit and push changes
4. Re-run build

### Issue: "The system cannot find the file specified" for waitress_server.py
**Status:** ❌ FAILED - File creation path incorrect
**Solution:**
1. Verify Jenkinsfile uses `%APP_DIR%\waitress_server.py` (not relative path)
2. Check "Create Waitress Server File" stage output
3. Verify file exists: `type ai_minor\waitress_server.py`
4. If not, check Jenkinsfile syntax

### Issue: "Port 5000 already in use"
**Status:** ⚠️ WARNING - Old process still running
**Solution:**
1. Manually kill process: `taskkill /F /IM python.exe`
2. Or change port in Jenkinsfile (not recommended)
3. Re-run build

### Issue: "Health check failed"
**Status:** ❌ FAILED - Application not responding
**Solution:**
1. Check if Flask app started: `netstat -ano | findstr :5000`
2. Check `/health` endpoint exists in `app/routes.py`
3. Check application logs for errors
4. Verify waitress_server.py is correct

### Issue: "BUILD VERIFICATION SUCCESSFUL" but app doesn't start
**Status:** ⚠️ WARNING - Import works but runtime error
**Solution:**
1. Check application logs for runtime errors
2. Verify all dependencies installed
3. Check database connection
4. Check environment variables in `.env`

---

## Success Criteria

✅ **Build is successful when:**
1. All 12 stages complete without errors
2. No "ModuleNotFoundError" messages
3. No path-related errors
4. Application deploys successfully
5. Health check passes
6. Artifacts archived

✅ **Application is running when:**
1. `curl http://localhost:5000/health` returns 200 OK
2. `ai_minor\waitress_server.py` exists and is readable
3. No Python errors in console
4. Port 5000 is listening

---

## Quick Test Commands

```bash
# Test 1: Check Flask import
python -c "import sys; sys.path.insert(0, 'ai_minor'); from app import app; print('✓ OK')"

# Test 2: Check waitress_server.py exists
type ai_minor\waitress_server.py

# Test 3: Check health endpoint
curl http://localhost:5000/health

# Test 4: Check port 5000 listening
netstat -ano | findstr :5000

# Test 5: Check requirements installed
pip list | findstr -E "Flask|waitress|groq|whisper"
```

---

## Next Steps After Successful Build

1. ✅ Verify all stages pass
2. ✅ Confirm application is running
3. ✅ Test health endpoint
4. ✅ Review build artifacts
5. ✅ Check application logs
6. ✅ Test application features
7. ✅ Commit changes to GitHub
8. ✅ Setup GitHub webhook for auto-trigger (if not done)

---

**Last Updated:** May 20, 2026
**Status:** Ready for testing
**Next Action:** Run Jenkins build and verify all stages
