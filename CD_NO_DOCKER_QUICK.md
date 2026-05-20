# CD Without Docker - Quick Setup (5 Minutes)

## Problem
You don't use Docker, so the Docker CD Jenkinsfile won't work.

## Solution
Use direct Flask deployment without Docker.

---

## What's New in CD (No Docker)

### 3 New Stages Added:

1. **Deploy to Development**
   - Stops old Flask process
   - Starts new Flask application
   - Runs on port 5000

2. **Health Check**
   - Tests `/health` endpoint
   - Verifies app is running
   - Fails if app is down

3. **Smoke Tests**
   - Tests basic endpoints
   - Verifies functionality
   - Catches deployment issues

---

## Step 1: Replace Jenkinsfile (2 minutes)

```bash
# Backup current
copy Jenkinsfile Jenkinsfile.backup

# Use new CD Jenkinsfile
copy Jenkinsfile-CD-No-Docker Jenkinsfile

# Commit and push
git add Jenkinsfile
git commit -m "Add CD stages: Direct Flask deployment"
git push origin main
```

---

## Step 2: Test (2 minutes)

1. Go to Jenkins: `http://localhost:8080/job/Persona-Nexus-Pipeline`
2. Click **Build Now**
3. Monitor console output
4. Should see new stages:
   - ✅ Deploy to Development
   - ✅ Health Check
   - ✅ Smoke Tests

---

## Step 3: Verify Application (1 minute)

```bash
# Check if Flask is running
curl http://localhost:5000/health

# Should return:
# {"status":"ok"}
```

---

## Pipeline Flow

```
Code Push
    ↓
[CI] Build & Test
    ↓
[CD] Deploy Flask App
    ↓
[CD] Health Check
    ↓
[CD] Smoke Tests
    ↓
✅ Complete
```

---

## What Happens on Each Build

### On Main Branch
1. **CI Stages** - Build and test code
2. **CD Stages** - Deploy application
   - Stop old Flask process
   - Start new Flask application
   - Verify health
   - Run smoke tests

### On Other Branches
- Only CI stages run
- No deployment

---

## Prerequisites

- [ ] Python 3.11+ installed
- [ ] curl installed
- [ ] Health endpoint exists (`/health`)
- [ ] run.py exists in ai_minor/

---

## Expected Console Output

```
[Pipeline] stage
[Pipeline] { (Deploy to Development)
[Pipeline] echo
🚀 Deploying to development environment...
[Pipeline] bat
Stopping Flask application...
Starting Flask application...
✅ Application deployed to development

[Pipeline] stage
[Pipeline] { (Health Check)
[Pipeline] echo
🏥 Running health check...
[Pipeline] bat
{"status":"ok"}
✅ Health check passed

[Pipeline] stage
[Pipeline] { (Smoke Tests)
[Pipeline] echo
🧪 Running smoke tests...
[Pipeline] bat
Testing health endpoint...
{"status":"ok"}
Testing home page...
✅ Smoke tests passed

[Pipeline] echo
✅ PIPELINE COMPLETED SUCCESSFULLY
Finished: SUCCESS
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 5000 in use | Kill process: `taskkill /pid <PID> /f` |
| Health check fails | Check app is running: `curl http://localhost:5000/health` |
| App doesn't start | Check logs in Jenkins console |
| Smoke tests fail | Check endpoints are accessible |

---

## Checklist

- [ ] Jenkinsfile replaced
- [ ] Committed and pushed
- [ ] Build runs successfully
- [ ] Deploy stage completes
- [ ] Health check passes
- [ ] Smoke tests pass
- [ ] Application is running

---

## Result

After setup:
- ✅ Every push to main triggers build
- ✅ All CI checks run
- ✅ Flask app deploys automatically
- ✅ Health check verifies deployment
- ✅ Smoke tests verify functionality

**Your CI/CD pipeline is complete!** 🚀

---

## Files Provided

1. **Jenkinsfile-CD-No-Docker** - Complete Jenkinsfile with CD
2. **CD_NO_DOCKER_GUIDE.md** - Detailed guide
3. **CD_NO_DOCKER_QUICK.md** - This file

