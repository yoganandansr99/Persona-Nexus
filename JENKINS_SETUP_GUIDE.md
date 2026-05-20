# Jenkins Setup Guide - Persona Nexus AI Interview Platform

## Table of Contents
1. [Jenkins Installation](#jenkins-installation)
2. [Required Plugins](#required-plugins)
3. [Pipeline Creation](#pipeline-creation)
4. [Docker Integration](#docker-integration)
5. [Troubleshooting](#troubleshooting)

---

## 1. Jenkins Installation

### Option A: Windows Installation

#### Step 1: Download Jenkins
1. Go to https://www.jenkins.io/download/
2. Download **Jenkins for Windows** (LTS version recommended)
3. Run the installer (.msi file)

#### Step 2: Initial Setup
1. Jenkins will start automatically after installation
2. Open browser: `http://localhost:8080`
3. Find initial admin password at: `C:\Program Files\Jenkins\secrets\initialAdminPassword`
4. Copy the password and paste it in the browser
5. Click **Install suggested plugins**
6. Create first admin user
7. Configure Jenkins URL (keep as `http://localhost:8080`)

#### Step 3: Configure Java Path (if needed)
1. Go to **Manage Jenkins** → **Configure System**
2. Set **JAVA_HOME** to your Java installation path
3. Example: `C:\Program Files\Java\jdk-11.0.x`

---

### Option B: Docker Installation (Recommended)

```bash
# Create Jenkins volume
docker volume create jenkins-data

# Run Jenkins in Docker
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins \
  jenkins/jenkins:lts

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 2. Required Plugins

### Step 1: Access Plugin Manager
1. Go to **Manage Jenkins** → **Manage Plugins**
2. Click **Available** tab

### Step 2: Install Required Plugins

Search and install these plugins:

#### Core Plugins
- **Pipeline** (Declarative Pipeline)
- **Blue Ocean** (Better UI for pipelines)
- **Git** (Git integration)
- **GitHub** (GitHub integration)

#### Docker Plugins
- **Docker** (Docker integration)
- **Docker Pipeline** (Docker in pipelines)
- **Docker Commons** (Docker support)

#### Build & Test Plugins
- **JUnit** (Test reporting)
- **Cobertura** (Code coverage)
- **SonarQube Scanner** (Code quality)

#### Notification Plugins
- **Email Extension** (Email notifications)
- **Slack** (Slack notifications)
- **GitHub Status** (GitHub status updates)

#### Utility Plugins
- **AnsiColor** (Colored console output)
- **Timestamper** (Add timestamps to logs)
- **Log Parser** (Parse build logs)

### Step 3: Install Plugins
1. Select all required plugins
2. Click **Install without restart**
3. Check **Restart Jenkins when installation is complete**
4. Wait for Jenkins to restart

### Step 4: Verify Installation
1. Go to **Manage Jenkins** → **Manage Plugins** → **Installed**
2. Verify all plugins are listed

---

## 3. Pipeline Creation

### Step 1: Create New Pipeline Job
1. Click **New Item** on Jenkins home
2. Enter job name: `persona-nexus-pipeline`
3. Select **Pipeline**
4. Click **OK**

### Step 2: Configure Pipeline

#### General Settings
1. Check **GitHub project**
2. Enter project URL: `https://github.com/YOUR_USERNAME/AI_minor`
3. Check **Build Triggers** → **GitHub hook trigger for GITScm polling**

#### Pipeline Definition
1. Select **Pipeline script from SCM**
2. Choose **Git** as SCM
3. Enter repository URL: `https://github.com/YOUR_USERNAME/AI_minor.git`
4. Set branch: `*/main` or `*/master`
5. Script path: `Jenkinsfile`

### Step 3: Save Configuration
1. Click **Save**
2. Jenkins will now look for `Jenkinsfile` in your repository

---

## 4. Docker Integration

### Step 1: Configure Docker in Jenkins

#### For Windows (Docker Desktop)
1. Go to **Manage Jenkins** → **Configure System**
2. Scroll to **Docker**
3. Click **Add Docker Cloud**
4. Set Docker URL: `unix:///var/run/docker.sock` (Linux) or `tcp://localhost:2375` (Windows)
5. Test connection

#### For Linux
1. Add Jenkins user to docker group:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Step 2: Create Jenkinsfile

Create `Jenkinsfile` in your repository root:

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "persona-nexus:${BUILD_NUMBER}"
        DOCKER_REGISTRY = "your-registry"
        GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code..."
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo "Running tests..."
                script {
                    sh '''
                        docker run --rm ${DOCKER_IMAGE} \
                        python -m pytest tests/ -v --tb=short
                    '''
                }
            }
        }
        
        stage('Code Quality') {
            steps {
                echo "Running code quality checks..."
                script {
                    sh '''
                        docker run --rm ${DOCKER_IMAGE} \
                        pylint app/ --exit-zero
                    '''
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo "Pushing image to registry..."
                script {
                    sh '''
                        docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
                    '''
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                echo "Deploying to staging..."
                script {
                    sh '''
                        docker-compose -f docker-compose.staging.yml down
                        docker-compose -f docker-compose.staging.yml up -d
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
            }
            steps {
                echo "Deploying to production..."
                script {
                    sh '''
                        docker-compose -f docker-compose.prod.yml down
                        docker-compose -f docker-compose.prod.yml up -d
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo "Cleaning up..."
            sh 'docker system prune -f'
        }
        success {
            echo "Pipeline succeeded!"
            // Add Slack/Email notification here
        }
        failure {
            echo "Pipeline failed!"
            // Add Slack/Email notification here
        }
    }
}
```

---

## 5. Step-by-Step Pipeline Execution

### First Run
1. Go to your pipeline job
2. Click **Build Now**
3. Monitor build progress in **Console Output**

### Stages Explained

| Stage | Purpose |
|-------|---------|
| **Checkout** | Clone repository from GitHub |
| **Build Docker Image** | Build Docker image with tag |
| **Run Tests** | Execute unit tests inside container |
| **Code Quality** | Run linting and code analysis |
| **Push to Registry** | Push image to Docker Hub/Registry |
| **Deploy to Staging** | Deploy to staging environment |
| **Deploy to Production** | Manual approval + production deployment |

---

## 6. GitHub Integration

### Step 1: Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click **Generate new token**
3. Select scopes: `repo`, `admin:repo_hook`, `admin:org_hook`
4. Copy token

### Step 2: Add GitHub Credentials to Jenkins
1. Go to **Manage Jenkins** → **Manage Credentials**
2. Click **System** → **Global credentials**
3. Click **Add Credentials**
4. Choose **Username with password**
5. Username: your GitHub username
6. Password: paste the token
7. ID: `github-credentials`
8. Click **Create**

### Step 3: Configure GitHub Webhook
1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Payload URL: `http://your-jenkins-url/github-webhook/`
4. Content type: `application/json`
5. Events: Push events
6. Click **Add webhook**

---

## 7. Notifications Setup

### Email Notifications
1. Go to **Manage Jenkins** → **Configure System**
2. Scroll to **E-mail Notification**
3. Configure SMTP server
4. Add to Jenkinsfile:
```groovy
post {
    failure {
        emailext(
            subject: "Build Failed: ${env.JOB_NAME}",
            body: "Build failed. Check console output at ${env.BUILD_URL}",
            to: "your-email@example.com"
        )
    }
}
```

### Slack Notifications
1. Install **Slack** plugin
2. Go to **Manage Jenkins** → **Configure System**
3. Find **Slack** section
4. Add Slack workspace token
5. Add to Jenkinsfile:
```groovy
post {
    failure {
        slackSend(
            color: 'danger',
            message: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
}
```

---

## 8. Troubleshooting

### Issue: Docker command not found
**Solution:**
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Issue: Permission denied while trying to connect to Docker daemon
**Solution:**
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

### Issue: Pipeline script not found
**Solution:**
1. Ensure `Jenkinsfile` is in repository root
2. Check branch name matches pipeline configuration
3. Verify Git credentials are correct

### Issue: Build timeout
**Solution:**
Add timeout to Jenkinsfile:
```groovy
options {
    timeout(time: 1, unit: 'HOURS')
}
```

### Issue: Out of disk space
**Solution:**
```bash
# Clean up old Docker images and containers
docker system prune -a --volumes
```

---

## 9. Best Practices

1. **Use declarative pipelines** - Easier to read and maintain
2. **Separate concerns** - Different stages for different tasks
3. **Use credentials** - Never hardcode secrets
4. **Add timeouts** - Prevent hanging builds
5. **Clean up resources** - Remove old images and containers
6. **Monitor logs** - Use AnsiColor and Timestamper plugins
7. **Test locally first** - Run Jenkinsfile locally before pushing
8. **Use Blue Ocean** - Better visualization of pipeline status

---

## 10. Quick Reference Commands

```bash
# View Jenkins logs
docker logs -f jenkins

# Restart Jenkins
docker restart jenkins

# Access Jenkins container
docker exec -it jenkins bash

# View Jenkins configuration
cat /var/jenkins_home/config.xml

# Backup Jenkins
docker cp jenkins:/var/jenkins_home ./jenkins-backup

# Restore Jenkins
docker cp ./jenkins-backup jenkins:/var/jenkins_home
```

---

## 11. Complete Setup Checklist

- [ ] Jenkins installed and running
- [ ] All required plugins installed
- [ ] Docker configured in Jenkins
- [ ] GitHub credentials added
- [ ] GitHub webhook configured
- [ ] Pipeline job created
- [ ] Jenkinsfile in repository
- [ ] First build successful
- [ ] Notifications configured
- [ ] Staging deployment working
- [ ] Production deployment ready

---

## Support

For more information:
- Jenkins Documentation: https://www.jenkins.io/doc/
- Pipeline Syntax: https://www.jenkins.io/doc/book/pipeline/
- Docker Plugin: https://plugins.jenkins.io/docker-plugin/
- Blue Ocean: https://www.jenkins.io/doc/book/blueocean/

