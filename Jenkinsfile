pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "panelpal:latest" // Name of the Docker image
    }
    stages {
        stage('Checkout') {
            steps {
                // Clone the repository and checkout Jenkinsfile branch
                git url: 'https://github.com/PatrickWeller/PanelPal.git', 
                branch: "${env.BRANCH_NAME}"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image using the Dockerfile
                    sh """
                        docker build -q -t ${DOCKER_IMAGE} .
                    """
                }
            }
        }
        stage('Run Tests') {
            steps {
                script {
                    // Run tests inside the container
                    sh """
                        docker run --rm ${DOCKER_IMAGE} pytest --cov=PanelPal test/
                    """
                }
            }
        }
    }
    post {
        always {
            // Clean up Docker images and containers if needed
            echo 'Cleaning up...'
            sh """
                docker system prune -f

                # Remove the image, suppress errors if not found
                docker rmi ${DOCKER_IMAGE} || true 
            """
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