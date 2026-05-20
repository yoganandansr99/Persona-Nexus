pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE_NAME = 'persona-nexus'
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        GITHUB_TOKEN = credentials('github-token')
    }

    stages {
        stage('Checkout') {
            steps {
                echo '🔄 Checking out code...'
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                    env.GIT_COMMIT_AUTHOR = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
                }
            }
        }

        stage('Build') {
            steps {
                echo '🔨 Building Docker image...'
                script {
                    sh '''
                        docker build \
                            -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} \
                            -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest \
                            -f Dockerfile \
                            .
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                script {
                    sh '''
                        docker run --rm \
                            -v $(pwd)/ai_minor:/app \
                            ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} \
                            python -m pytest tests/ -v --cov=app --cov-report=xml || true
                    '''
                }
            }
        }

        stage('Code Quality') {
            steps {
                echo '📊 Running code quality checks...'
                script {
                    sh '''
                        docker run --rm \
                            -v $(pwd)/ai_minor:/app \
                            ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} \
                            python -m pylint app/ --exit-zero || true
                    '''
                }
            }
        }

        stage('Security Scan') {
            steps {
                echo '🔒 Running security scan...'
                script {
                    sh '''
                        docker run --rm \
                            -v $(pwd):/app \
                            aquasec/trivy:latest image \
                            --severity HIGH,CRITICAL \
                            ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} || true
                    '''
                }
            }
        }

        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo '📤 Pushing image to Docker registry...'
                script {
                    sh '''
                        echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying to staging environment...'
                script {
                    sh '''
                        docker-compose -f docker-compose.yml \
                            -f docker-compose.staging.yml \
                            up -d
                    '''
                }
            }
        }

        stage('Integration Tests') {
            when {
                branch 'main'
            }
            steps {
                echo '🧪 Running integration tests...'
                script {
                    sh '''
                        sleep 10
                        curl -f http://localhost:5000/health || exit 1
                        echo "✅ Health check passed"
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
                tag pattern: "v\\d+\\.\\d+\\.\\d+", comparator: "REGEXP"
            }
            steps {
                echo '🚀 Deploying to production...'
                script {
                    sh '''
                        docker-compose -f docker-compose.yml \
                            -f docker-compose.prod.yml \
                            up -d
                    '''
                }
            }
        }

        stage('Notify') {
            steps {
                echo '📢 Sending notifications...'
                script {
                    sh '''
                        echo "Build Status: ${BUILD_STATUS}"
                        echo "Build Number: ${BUILD_NUMBER}"
                        echo "Git Commit: ${GIT_COMMIT_MSG}"
                        echo "Author: ${GIT_COMMIT_AUTHOR}"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up...'
            cleanWs()
        }
        success {
            echo '✅ Pipeline succeeded!'
            script {
                sh '''
                    echo "Build successful: ${BUILD_URL}"
                '''
            }
        }
        failure {
            echo '❌ Pipeline failed!'
            script {
                sh '''
                    echo "Build failed: ${BUILD_URL}"
                '''
            }
        }
    }
}
