pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build('eliudnjenga/rentcom:latest')
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-access') {
                        docker.image('eliudnjenga/rentcom:latest').push()
                    }
                }
            }
        }
    }
}
