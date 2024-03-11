pipeline {
    agent any
    environment {
       DOCKER_HUB_USERNAME = 'eliudnjenga'
        DOCKER_HUB_PASSWORD = 'Fee8q7zsTut3#2!'
        DOCKER_IMAGE = 'eliudnjenga/rentcom'
    }
   
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
                    docker.withRegistry('https://index.docker.io/v1/',  DOCKER_HUB_USERNAME, DOCKER_HUB_PASSWORD) {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }
    }
}
