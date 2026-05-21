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
        stage('Checkout Code') {
            steps {
                echo '========== CHECKOUT =========='
                checkout scm
            }
        }

        stage('Stop Old Server') {
            steps {
                echo '========== STOP OLD APP =========='
                catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                    bat '''
                        FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :5000') DO (
                            taskkill /PID %%P /F 2>nul || echo Process not found
                        )
                        echo ✓ Old app stopped
                    '''
                }
            }
        }

        stage('Start New Server') {
            steps {
                echo '========== START APP =========='
                bat '''
                    cd /d ai_minor
                    start "" /B python run.py
                    cd /d ..
                    echo ✓ App started
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '========== HEALTH CHECK =========='
                bat '''
                    ping -n 6 127.0.0.1 >nul
                    curl http://127.0.0.1:5000
                '''
            }
        }
    }

    post {
        success {
            echo '===================================='
            echo 'CI/CD SUCCESSFUL'
            echo 'Public URL:'
            echo 'https://hasty-hydrogen-wind.ngrok-free.dev/'
            echo '===================================='
        }
        failure {
            echo 'Build or deployment failed'
        }
        always {
            cleanWs()
        }
    }
}