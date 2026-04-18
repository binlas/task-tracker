pipeline {
    agent any

    stages {

        stage('Clone Code') {
            steps {
                git branch: 'main', url: 'https://github.com/binlas/task-tracker.git'
                 }
}

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t task-tracker-app .'
            }
        }

        stage('Stop Old Container') {
            steps {
                bat 'docker stop task-tracker || true'
                bat 'docker rm task-tracker || true'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d -p 5000:5000 -p 8501:8501 --name task-tracker task-tracker-app'
            }
        }
    }
}