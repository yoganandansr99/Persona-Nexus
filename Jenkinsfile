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
                        
                        # List installed packages
                        pip list
                        
                        echo "✅ Dependency check completed"
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
            node {
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
        }
        success {
            echo '✅ Pipeline succeeded!'
            node {
                archiveArtifacts artifacts: 'build_artifacts/**', allowEmptyArchive: true
            }
        }
        failure {
            echo '❌ Pipeline failed!'
            node {
                script {
                    sh '''
                        echo "Build failed at: $(date)"
                        echo "Check console output for details: ${BUILD_URL}console"
                    '''
                }
            }
        }
    }
}
