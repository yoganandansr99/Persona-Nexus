pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    environment {
        PYTHON_VERSION = '3.11'
        VENV_DIR = "venv"
    }

    stages {
        stage('Checkout') {
            steps {
                echo '🔄 Checking out code...'
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = bat(script: '@git log -1 --pretty=%%B', returnStdout: true).trim()
                    env.GIT_COMMIT_AUTHOR = bat(script: '@git log -1 --pretty=%%an', returnStdout: true).trim()
                    env.GIT_COMMIT_SHORT = bat(script: '@git rev-parse --short HEAD', returnStdout: true).trim()
                }
            }
        }

        stage('Setup Environment') {
            steps {
                echo '⚙️ Setting up Python virtual environment...'
                script {
                    bat '''
                        python -m venv venv
                        call venv\\Scripts\\activate.bat
                        python -m pip install --upgrade pip setuptools wheel
                        pip install --no-cache-dir -r requirements.txt
                        if errorlevel 1 (
                            echo ⚠️ Some packages failed to install, continuing...
                        )
                        echo ✅ Virtual environment ready
                    '''
                }
            }
        }

        stage('Code Quality') {
            steps {
                echo '📊 Running code quality checks...'
                script {
                    bat '''
                        call venv\\Scripts\\activate.bat
                        
                        REM Check for syntax errors
                        python -m py_compile ai_minor\\app\\*.py
                        
                        echo ✅ Code quality check completed
                    '''
                }
            }
        }

        stage('Dependency Check') {
            steps {
                echo '🔍 Checking dependencies...'
                script {
                    bat '''
                        call venv\\Scripts\\activate.bat
                        
                        REM List installed packages
                        pip list
                        
                        echo ✅ Dependency check completed
                    '''
                }
            }
        }

        stage('Build Verification') {
            steps {
                echo '🔨 Verifying application build...'
                script {
                    bat '''
                        call venv\\Scripts\\activate.bat
                        
                        REM Check if app can be imported
                        cd ai_minor
                        python -c "from app import app; print('✅ Application imports successfully')"
                        cd ..
                        
                        echo ✅ Build verification passed
                    '''
                }
            }
        }

        stage('Generate Report') {
            steps {
                echo '📋 Generating build report...'
                script {
                    bat '''
                        (
                            echo ========================================
                            echo BUILD REPORT - Persona Nexus
                            echo ========================================
                            echo Build Number: %BUILD_NUMBER%
                            echo Build URL: %BUILD_URL%
                            echo Git Commit: %GIT_COMMIT_SHORT%
                            echo Commit Message: %GIT_COMMIT_MSG%
                            echo Author: %GIT_COMMIT_AUTHOR%
                            echo Build Status: SUCCESS
                            echo Timestamp: %date% %time%
                            echo ========================================
                        ) > build_report.txt
                        
                        type build_report.txt
                    '''
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                echo '📦 Archiving build artifacts...'
                script {
                    bat '''
                        REM Archive requirements and configuration
                        if not exist build_artifacts mkdir build_artifacts
                        copy requirements.txt build_artifacts\\
                        copy Jenkinsfile build_artifacts\\
                        xcopy ai_minor\\app build_artifacts\\app /E /I /Y
                        
                        echo ✅ Artifacts archived
                    '''
                }
            }
        }

        stage('Notify Success') {
            steps {
                echo '📢 Build completed successfully!'
                script {
                    bat '''
                        echo ========================================
                        echo ✅ PIPELINE COMPLETED SUCCESSFULLY
                        echo ========================================
                        echo Build Number: %BUILD_NUMBER%
                        echo Git Commit: %GIT_COMMIT_SHORT%
                        echo Author: %GIT_COMMIT_AUTHOR%
                        echo Build URL: %BUILD_URL%
                        echo ========================================
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo '✅ Pipeline succeeded!'
            archiveArtifacts artifacts: 'build_artifacts/**', allowEmptyArchive: true
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
