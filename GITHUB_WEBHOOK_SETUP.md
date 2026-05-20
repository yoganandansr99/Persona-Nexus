# GitHub Webhook Setup - Auto-Trigger Jenkins Builds

## Problem
Pushing code to GitHub doesn't automatically trigger Jenkins builds.

## Solution
Configure GitHub webhook to notify Jenkins on every push.

---

## Step 1: Get Jenkins Webhook URL

### On Windows Jenkins
1. Go to Jenkins home: `http://localhost:8080`
2. Your webhook URL will be:
   ```
   http://YOUR_IP:8080/github-webhook/
   ```

### Find Your IP Address
```bash
# Windows
ipconfig

# Look for IPv4 Address (e.g., 192.168.1.100)
```

### Example Webhook URLs
- **Local:** `http://localhost:8080/github-webhook/`
- **Network:** `http://192.168.1.100:8080/github-webhook/`
- **Public:** `http://your-domain.com:8080/github-webhook/`

---

## Step 2: Configure GitHub Webhook

### 2.1 Go to GitHub Repository Settings
1. Open your repository: `https://github.com/yoganandansr99/Persona-Nexus`
2. Click **Settings** (top right)
3. Click **Webhooks** (left sidebar)
4. Click **Add webhook**

### 2.2 Fill in Webhook Details

**Payload URL:**
```
http://YOUR_IP:8080/github-webhook/
```

**Content type:**
```
application/json
```

**Events to trigger on:**
- Select: **Just the push event**
- Or: **Let me select individual events** → Check **Pushes**

**Active:**
- ✅ Check the box

### 2.3 Click **Add webhook**

---

## Step 3: Verify Webhook in Jenkins

### 3.1 Configure Jenkins Job
1. Go to Jenkins job: `http://localhost:8080/job/Persona-Nexus-Pipeline`
2. Click **Configure**
3. Scroll to **Build Triggers**
4. Check: **GitHub hook trigger for GITScm polling**
5. Click **Save**

### 3.2 Check Webhook Deliveries
1. Go to GitHub repo → Settings → Webhooks
2. Click on your webhook
3. Scroll to **Recent Deliveries**
4. Should see green checkmarks (✅)
5. If red (❌), click to see error details

---

## Step 4: Test the Webhook

### Test 1: Manual Push
```bash
# Make a change
echo "# Test webhook" >> README.md

# Commit and push
git add README.md
git commit -m "Test webhook trigger"
git push origin main
```

### Test 2: Check Jenkins
1. Go to Jenkins job
2. Should see new build automatically started
3. Check **Build History** for new build

### Test 3: Check Webhook Log
1. GitHub repo → Settings → Webhooks
2. Click your webhook
3. Click **Recent Deliveries**
4. Should see recent push event with ✅

---

## Common Issues & Fixes

### Issue 1: Webhook Shows Red ❌

**Error:** `Connection refused` or `Connection timeout`

**Cause:** Jenkins is not accessible from GitHub

**Fix:**
- If Jenkins is on localhost, use ngrok to expose it:
  ```bash
  ngrok http 8080
  # Use the ngrok URL in webhook
  ```
- Or use a public IP/domain

### Issue 2: Webhook Shows Green ✅ But Build Doesn't Start

**Cause:** Jenkins job not configured for webhook

**Fix:**
1. Go to Jenkins job → Configure
2. Check **GitHub hook trigger for GITScm polling**
3. Save and try again

### Issue 3: "Payload URL is not a valid URL"

**Cause:** Invalid URL format

**Fix:**
- Ensure URL ends with `/`
- Use correct IP address
- Check port number (usually 8080)

### Issue 4: "We couldn't deliver this payload"

**Cause:** Jenkins is offline or unreachable

**Fix:**
- Ensure Jenkins is running
- Check firewall settings
- Verify IP address is correct
- Check port is open

---

## Alternative: Manual Polling (If Webhook Doesn't Work)

### Configure Jenkins to Poll GitHub

1. Go to Jenkins job → Configure
2. Scroll to **Build Triggers**
3. Check: **Poll SCM**
4. Enter schedule:
   ```
   H/5 * * * *
   ```
   (Checks every 5 minutes)
5. Click **Save**

**Note:** Polling is slower than webhooks but works without network access.

---

## Step-by-Step Setup (Complete)

### For Local Jenkins (Windows)

#### 1. Install ngrok (to expose local Jenkins)
```bash
# Download from https://ngrok.com/download
# Or use chocolatey
choco install ngrok
```

#### 2. Start ngrok
```bash
ngrok http 8080
# You'll see: Forwarding https://abc123.ngrok.io -> http://localhost:8080
```

#### 3. Use ngrok URL in GitHub Webhook
```
https://abc123.ngrok.io/github-webhook/
```

#### 4. Configure Jenkins Job
1. Jenkins → Job → Configure
2. Check **GitHub hook trigger for GITScm polling**
3. Save

#### 5. Test
```bash
git add .
git commit -m "Test"
git push origin main
# Should trigger build automatically
```

---

## For Public Jenkins (Server)

#### 1. Get Server IP/Domain
```bash
# Get IP
hostname -I

# Or use domain: example.com
```

#### 2. Configure GitHub Webhook
```
http://your-server-ip:8080/github-webhook/
```

#### 3. Configure Jenkins Job
1. Jenkins → Job → Configure
2. Check **GitHub hook trigger for GITScm polling**
3. Save

#### 4. Test
```bash
git add .
git commit -m "Test"
git push origin main
# Should trigger build automatically
```

---

## Verify Webhook is Working

### Check 1: GitHub Webhook Log
```
GitHub → Repo → Settings → Webhooks → Your Webhook
Recent Deliveries should show:
  ✅ POST /github-webhook/ 200 OK
```

### Check 2: Jenkins Build History
```
Jenkins → Job → Build History
Should show new builds after each push
```

### Check 3: Jenkins Logs
```
Jenkins → Manage Jenkins → System Log
Should show webhook requests
```

---

## Complete Jenkinsfile with Webhook Trigger

```groovy
pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    triggers {
        githubPush()  // Trigger on GitHub push
    }

    environment {
        PYTHON_VERSION = '3.11'
        VENV_DIR = "venv"
    }

    stages {
        // ... rest of stages
    }
}
```

---

## Troubleshooting Checklist

- [ ] Jenkins is running
- [ ] GitHub webhook URL is correct
- [ ] Webhook is active (green checkmark)
- [ ] Jenkins job has webhook trigger enabled
- [ ] Recent deliveries show ✅
- [ ] Test push triggers build
- [ ] Build history shows new builds

---

## Quick Test Commands

```bash
# Test 1: Make a change
echo "test" >> README.md

# Test 2: Commit and push
git add README.md
git commit -m "Test webhook"
git push origin main

# Test 3: Check Jenkins
# Go to http://localhost:8080/job/Persona-Nexus-Pipeline
# Should see new build in Build History

# Test 4: Check webhook log
# GitHub → Settings → Webhooks → Recent Deliveries
# Should show ✅ for recent push
```

---

## Expected Behavior After Setup

### Before Webhook
```
Push to GitHub → Manual "Build Now" in Jenkins → Build starts
```

### After Webhook
```
Push to GitHub → Automatic build in Jenkins → Build starts immediately
```

---

## Summary

✅ **Webhook Setup Steps:**
1. Get Jenkins webhook URL
2. Add webhook in GitHub
3. Enable webhook trigger in Jenkins job
4. Test with git push
5. Verify in webhook log

✅ **Expected Result:**
- Every push to GitHub triggers Jenkins build
- Build starts automatically
- No manual "Build Now" needed

---

## Resources

- [GitHub Webhooks Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [Jenkins GitHub Plugin](https://plugins.jenkins.io/github/)
- [ngrok Documentation](https://ngrok.com/docs)
- [Jenkins Webhook Trigger](https://www.jenkins.io/doc/book/pipeline/syntax/#triggers)

