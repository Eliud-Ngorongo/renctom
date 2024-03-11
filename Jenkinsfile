pipeline {
    agent any
    environment {
        DOCKER_HUB_CREDENTIALS = credentials('eliudnjenga')
        DOCKER_IMAGE = 'eliudnjenga/rentcom'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }
        stage('Push') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_HUB_CREDENTIALS) {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }
    }
}
