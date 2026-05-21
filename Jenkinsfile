pipeline {
    agent any

    options {
        timeout(time: 10, unit: 'MINUTES')
        timestamps()
    }

    environment {
        APP_PORT = "5000"
        APP_DIR = "ai_minor"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '========== CHECKOUT =========='
                checkout scm
                echo '✓ Code checked out'
            }
        }

        stage('Create Server') {
            steps {
                echo '========== CREATE SERVER =========='
                bat '''
                    cd /d %APP_DIR%
                    (
                        echo from waitress import serve
                        echo from app import app
                        echo if __name__ == "__main__":
                        echo     serve(app, host="0.0.0.0", port=5000)
                    ) > waitress_server.py
                    cd /d ..
                    echo ✓ Server file created
                '''
            }
        }

        stage('Stop Old App') {
            steps {
                echo '========== STOP OLD APP =========='
                bat '''
                    FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :5000') DO (
                        taskkill /PID %%P /F 2>nul
                    )
                    echo ✓ Old app stopped
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo '========== DEPLOY =========='
                bat '''
                    cd /d %APP_DIR%
                    start /B python waitress_server.py
                    cd /d ..
                    timeout /t 5
                    echo ✓ App deployed on port 5000
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '========== HEALTH CHECK =========='
                bat '''
                    timeout /t 3
                    curl http://localhost:5000/health
                    echo ✓ Health check passed
                '''
            }
        }
    }

    post {
        always {
            echo '========== CLEANUP =========='
            cleanWs()
        }
    }
}