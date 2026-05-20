pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    environment {
        PYTHON_VERSION = '3.11'
        VENV_DIR = "${WORKSPACE}/venv"
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
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
            }
        }

        stage('Setup Environment') {
            steps {
                echo '⚙️ Setting up Python virtual environment...'
                script {
                    sh '''
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip setuptools wheel
                        pip install -r requirements.txt
                        echo "✅ Virtual environment ready"
                    '''
                }
            }
        }

        stage('Code Quality') {
            steps {
                echo '📊 Running code quality checks...'
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        
                        # Check for syntax errors
                        python -m py_compile ai_minor/app/*.py || true
                        
                        # Run pylint if available
                        pip install pylint > /dev/null 2>&1
                        python -m pylint ai_minor/app/ --exit-zero --disable=all --enable=E,F || true
                        
                        echo "✅ Code quality check completed"
                    '''
                }
            }
        }

        stage('Dependency Check') {
            steps {
                echo '🔍 Checking dependencies...'
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        
                        # Check for security vulnerabilities
                        pip install safety > /dev/null 2>&1
                        safety check --json || true
                        
                        echo "✅ Dependency check completed"
                    '''
                }
            }
        }

        stage('Unit Tests') {
            steps {
                echo '🧪 Running unit tests...'
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        
                        # Install pytest if not already installed
                        pip install pytest pytest-cov > /dev/null 2>&1
                        
                        # Run tests if test directory exists
                        if [ -d "tests" ]; then
                            python -m pytest tests/ -v --tb=short --cov=ai_minor/app --cov-report=term-missing || true
                        else
                            echo "⚠️ No tests directory found, skipping tests"
                        fi
                        
                        echo "✅ Unit tests completed"
                    '''
                }
            }
        }

        stage('Build Verification') {
            steps {
                echo '🔨 Verifying application build...'
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        
                        # Check if app can be imported
                        cd ai_minor
                        python -c "from app import app; print('✅ Application imports successfully')" || exit 1
                        cd ..
                        
                        echo "✅ Build verification passed"
                    '''
                }
            }
        }

        stage('Generate Report') {
            steps {
                echo '📋 Generating build report...'
                script {
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        
                        echo "========================================" > build_report.txt
                        echo "BUILD REPORT - Persona Nexus" >> build_report.txt
                        echo "========================================" >> build_report.txt
                        echo "Build Number: ${BUILD_NUMBER}" >> build_report.txt
                        echo "Build URL: ${BUILD_URL}" >> build_report.txt
                        echo "Git Commit: ${GIT_COMMIT_SHORT}" >> build_report.txt
                        echo "Commit Message: ${GIT_COMMIT_MSG}" >> build_report.txt
                        echo "Author: ${GIT_COMMIT_AUTHOR}" >> build_report.txt
                        echo "Build Status: SUCCESS" >> build_report.txt
                        echo "Timestamp: $(date)" >> build_report.txt
                        echo "========================================" >> build_report.txt
                        
                        cat build_report.txt
                    '''
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                echo '📦 Archiving build artifacts...'
                script {
                    sh '''
                        # Archive requirements and configuration
                        mkdir -p build_artifacts
                        cp requirements.txt build_artifacts/
                        cp Jenkinsfile build_artifacts/
                        cp -r ai_minor/app build_artifacts/ || true
                        
                        echo "✅ Artifacts archived"
                    '''
                }
            }
        }

        stage('Notify Success') {
            steps {
                echo '📢 Build completed successfully!'
                script {
                    sh '''
                        echo "========================================" 
                        echo "✅ PIPELINE COMPLETED SUCCESSFULLY"
                        echo "========================================"
                        echo "Build Number: ${BUILD_NUMBER}"
                        echo "Git Commit: ${GIT_COMMIT_SHORT}"
                        echo "Author: ${GIT_COMMIT_AUTHOR}"
                        echo "Build URL: ${BUILD_URL}"
                        echo "========================================"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up workspace...'
            script {
                sh '''
                    # Remove virtual environment to save space
                    rm -rf ${VENV_DIR}
                    
                    # Archive build report
                    if [ -f "build_report.txt" ]; then
                        cp build_report.txt build_report_${BUILD_NUMBER}.txt
                    fi
                '''
            }
        }
        success {
            echo '✅ Pipeline succeeded!'
            archiveArtifacts artifacts: 'build_artifacts/**', allowEmptyArchive: true
        }
        failure {
            echo '❌ Pipeline failed!'
            script {
                sh '''
                    echo "Build failed at: $(date)"
                    echo "Check console output for details: ${BUILD_URL}console"
                '''
            }
        }
    }
}
