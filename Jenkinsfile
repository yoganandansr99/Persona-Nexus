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
        APP_PORT = "5000"
        APP_DIR = "ai_minor"
        APP_FILE = "waitress_server.py"
    }

    stages {

        stage('Checkout Source') {
            steps {
                echo '========================================'
                echo 'CHECKING OUT SOURCE CODE'
                echo '========================================'

                checkout scm

                script {

                    env.GIT_COMMIT_MSG = bat(
                        script: '@git log -1 --pretty=%%B',
                        returnStdout: true
                    ).trim()

                    env.GIT_COMMIT_AUTHOR = bat(
                        script: '@git log -1 --pretty=%%an',
                        returnStdout: true
                    ).trim()

                    env.GIT_COMMIT_SHORT = bat(
                        script: '@git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Setup Python Environment') {
            steps {

                echo '========================================'
                echo 'SETTING UP PYTHON ENVIRONMENT'
                echo '========================================'

                bat '''
                    IF EXIST venv (
                        rmdir /s /q venv
                    )

                    python -m venv venv

                    call venv\\Scripts\\activate.bat

                    python -m pip install --upgrade pip setuptools wheel

                    pip install --no-cache-dir -r requirements.txt

                    pip install waitress

                    echo.
                    echo ========================================
                    echo PYTHON ENVIRONMENT READY
                    echo ========================================
                '''
            }
        }

        stage('Code Quality Check') {
            steps {

                echo '========================================'
                echo 'RUNNING CODE QUALITY CHECK'
                echo '========================================'

                bat '''
                    call venv\\Scripts\\activate.bat

                    for /r %APP_DIR% %%f in (*.py) do (
                        python -m py_compile "%%f"
                    )

                    echo.
                    echo ========================================
                    echo CODE QUALITY CHECK COMPLETED
                    echo ========================================
                '''
            }
        }

        stage('Run Tests') {
            steps {

                echo '========================================'
                echo 'RUNNING TESTS'
                echo '========================================'

                bat '''
                    call venv\\Scripts\\activate.bat

                    IF EXIST tests (
                        pytest tests
                    ) ELSE (
                        echo No tests folder found
                    )

                    echo.
                    echo ========================================
                    echo TEST STAGE COMPLETED
                    echo ========================================
                '''
            }
        }

        stage('Build Verification') {
            steps {

                echo '========================================'
                echo 'VERIFYING APPLICATION BUILD'
                echo '========================================'

                bat '''
                    call venv\\Scripts\\activate.bat

                    python -c "import sys; sys.path.insert(0, '%APP_DIR%'); from app import app; print('Flask App Imported Successfully')"

                    echo.
                    echo ========================================
                    echo BUILD VERIFICATION SUCCESSFUL
                    echo ========================================
                '''
            }
        }

        stage('Create Waitress Server File') {
            steps {

                echo '========================================'
                echo 'CREATING WAITRESS SERVER'
                echo '========================================'

                bat '''
                    cd /d %APP_DIR%
                    
                    (
                        echo from waitress import serve
                        echo from app import app
                        echo.
                        echo if __name__ == "__main__":
                        echo     serve(app, host="0.0.0.0", port=5000)
                    ) > waitress_server.py

                    if exist waitress_server.py (
                        echo File created successfully
                        type waitress_server.py
                    ) else (
                        echo ERROR: Failed to create waitress_server.py
                        exit /b 1
                    )

                    cd /d ..

                    echo.
                    echo ========================================
                    echo WAITRESS SERVER FILE CREATED
                    echo ========================================
                '''
            }
        }

        stage('Stop Old Application') {
            steps {

                echo '========================================'
                echo 'STOPPING OLD APPLICATION'
                echo '========================================'

                bat '''
                    FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :5000') DO (
                        taskkill /PID %%P /F
                    )

                    echo.
                    echo ========================================
                    echo OLD APPLICATION STOPPED
                    echo ========================================
                '''
            }
        }

        stage('Deploy Application') {
            steps {

                echo '========================================'
                echo 'DEPLOYING APPLICATION'
                echo '========================================'

                bat '''
                    call venv\\Scripts\\activate.bat

                    cd /d %APP_DIR%
                    
                    if exist waitress_server.py (
                        echo Starting application from: %cd%\\waitress_server.py
                        start /B python waitress_server.py
                    ) else (
                        echo ERROR: waitress_server.py not found in %cd%
                        exit /b 1
                    )

                    cd /d ..

                    timeout /t 10

                    echo.
                    echo ========================================
                    echo APPLICATION DEPLOYED SUCCESSFULLY
                    echo ========================================
                '''
            }
        }

        stage('Health Check') {
            steps {

                echo '========================================'
                echo 'RUNNING HEALTH CHECK'
                echo '========================================'

                bat '''
                    curl http://localhost:%APP_PORT%

                    IF %ERRORLEVEL% NEQ 0 (
                        echo.
                        echo ========================================
                        echo HEALTH CHECK FAILED
                        echo ========================================
                        exit /b 1
                    )

                    echo.
                    echo ========================================
                    echo APPLICATION IS RUNNING SUCCESSFULLY
                    echo ========================================
                '''
            }
        }

        stage('Generate Build Report') {
            steps {

                echo '========================================'
                echo 'GENERATING BUILD REPORT'
                echo '========================================'

                bat '''
                    (
                        echo ========================================
                        echo PERSONA NEXUS BUILD REPORT
                        echo ========================================
                        echo Build Number  : %BUILD_NUMBER%
                        echo Build URL     : %BUILD_URL%
                        echo Git Commit    : %GIT_COMMIT_SHORT%
                        echo Commit Author : %GIT_COMMIT_AUTHOR%
                        echo Commit Msg    : %GIT_COMMIT_MSG%
                        echo Deployment    : SUCCESS
                        echo Port          : %APP_PORT%
                        echo Timestamp     : %date% %time%
                        echo ========================================
                    ) > build_report.txt

                    type build_report.txt
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {

                echo '========================================'
                echo 'ARCHIVING ARTIFACTS'
                echo '========================================'

                bat '''
                    IF NOT EXIST build_artifacts (
                        mkdir build_artifacts
                    )

                    copy build_report.txt build_artifacts\\

                    IF EXIST Jenkinsfile (
                        copy Jenkinsfile build_artifacts\\
                    )

                    IF EXIST requirements.txt (
                        copy requirements.txt build_artifacts\\
                    )

                    xcopy %APP_DIR% build_artifacts\\app /E /I /Y

                    echo.
                    echo ========================================
                    echo ARTIFACTS ARCHIVED
                    echo ========================================
                '''
            }
        }

        stage('Deployment Summary') {
            steps {

                echo '========================================'
                echo 'CI/CD PIPELINE COMPLETED SUCCESSFULLY'
                echo '========================================'

                echo "Application URL: http://localhost:5000"
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Git Commit: ${GIT_COMMIT_SHORT}"
                echo "Author: ${GIT_COMMIT_AUTHOR}"

                echo '========================================'
            }
        }
    }

    post {

        success {

            echo '========================================'
            echo 'PIPELINE SUCCEEDED'
            echo '========================================'

            archiveArtifacts(
                artifacts: 'build_artifacts/**',
                allowEmptyArchive: true
            )
        }

        failure {

            echo '========================================'
            echo 'PIPELINE FAILED'
            echo '========================================'
        }

        always {

            echo '========================================'
            echo 'CLEANING WORKSPACE'
            echo '========================================'

            cleanWs()
        }
    }
}