pipeline {
    agent any

    stages {

        stage('Clone Code') {
            steps {
                git 'https://github.com/binlas/task-tracker.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t task-tracker-app .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker stop task-tracker || true'
                sh 'docker rm task-tracker || true'
            }
        }

        stage('Run Container') {
            steps {
                sh 'docker run -d -p 5000:5000 -p 8501:8501 --name task-tracker task-tracker-app'
            }
        }
    }
}