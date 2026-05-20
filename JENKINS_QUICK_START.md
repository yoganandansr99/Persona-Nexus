# Jenkins Quick Start - 5 Minutes Setup

## 1. Install Jenkins (Choose One)

### Windows
- Download from https://www.jenkins.io/download/
- Run installer
- Open http://localhost:8080
- Copy password from `C:\Program Files\Jenkins\secrets\initialAdminPassword`

### Docker
```bash
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins jenkins/jenkins:lts

# Get password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 2. Install Plugins (5 minutes)

Go to **Manage Jenkins** → **Manage Plugins** → **Available**

Search and install:
```
Pipeline
Blue Ocean
Git
GitHub
Docker
Docker Pipeline
Email Extension
AnsiColor
```

Click **Install without restart** → **Restart Jenkins when installation is complete**

---

## 3. Add GitHub Credentials

1. **Manage Jenkins** → **Manage Credentials** → **System** → **Global credentials**
2. **Add Credentials**
3. Type: **Username with password**
4. Username: `your-github-username`
5. Password: `your-github-token` (from GitHub Settings → Developer settings → Personal access tokens)
6. ID: `github-credentials`
7. **Create**

---

## 4. Create Pipeline Job

1. **New Item**
2. Name: `persona-nexus-pipeline`
3. Type: **Pipeline**
4. **OK**

### Configure:
- **GitHub project**: `https://github.com/YOUR_USERNAME/AI_minor`
- **Pipeline** → **Pipeline script from SCM**
- **SCM**: Git
- **Repository URL**: `https://github.com/YOUR_USERNAME/AI_minor.git`
- **Branch**: `*/main`
- **Script path**: `Jenkinsfile`
- **Save**

---

## 5. Create Jenkinsfile

Create file `Jenkinsfile` in repository root:

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "persona-nexus:${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run --rm ${DOCKER_IMAGE} python -m pytest tests/ -v'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
    
    post {
        always {
            sh 'docker system prune -f'
        }
    }
}
```

---

## 6. Run Pipeline

1. Go to pipeline job
2. Click **Build Now**
3. Monitor in **Console Output**

---

## 7. GitHub Webhook (Auto-trigger)

1. GitHub repo → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `http://your-jenkins-url/github-webhook/`
3. **Content type**: `application/json`
4. **Events**: Push events
5. **Add webhook**

Now pipeline runs automatically on every push!

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Docker not found | `sudo usermod -aG docker jenkins` |
| Permission denied | `sudo chmod 666 /var/run/docker.sock` |
| Jenkinsfile not found | Ensure it's in repo root, check branch name |
| Build timeout | Add `timeout(time: 1, unit: 'HOURS')` to Jenkinsfile |
| Out of disk | `docker system prune -a --volumes` |

---

## Useful Commands

```bash
# View logs
docker logs -f jenkins

# Restart
docker restart jenkins

# Access container
docker exec -it jenkins bash

# Backup
docker cp jenkins:/var/jenkins_home ./jenkins-backup
```

---

## Next Steps

1. ✅ Jenkins running
2. ✅ Plugins installed
3. ✅ Credentials added
4. ✅ Pipeline created
5. ✅ Jenkinsfile committed
6. ✅ Webhook configured
7. 🚀 Push code → Pipeline runs automatically!

