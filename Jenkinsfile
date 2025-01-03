pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "panelpal:latest" // Name of the Docker image
    }
    stages {
        stage('Checkout') {
            steps {
                // Clone the repository
                git url: 'https://github.com/PatrickWeller/PanelPal.git', 
                branch: "${env.BRANCH_NAME}"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image using the Dockerfile
                    sh """
                        docker build -t ${DOCKER_IMAGE} .
                    """
                }
            }
        }
        stage('Run Tests') {
            steps {
                script {
                    // Run tests inside the container
                    sh """
                        docker run --rm ${DOCKER_IMAGE} pytest
                    """
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline completed.'
        }
        success {
            echo 'Tests passed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}