pipeline {
    agent any
     environment {
        DOCKERHUB_CREDENTIALS = 'docker-hub-access'
    }

     
    triggers {
        pollSCM('* * * * *') // Poll every minute
    }
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
                    docker.withRegistry('https://index.docker.io/v1/', DOCKERHUB_CREDENTIALS) {
                        docker.image('eliudnjenga/rentcom:latest').push()
                    }
                }
            }
        }
    }
}
