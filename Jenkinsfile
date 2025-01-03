pipeline {
    agent {
        // Docker image with Conda pre-installed
        docker {
            image 'continuumio/miniconda3'
            args '-v /tmp:/tmp'
        }
    }

    environment {
        CONDA_ENV = 'PanelPal'  // Name of the Conda environment
        REPO_URL = "https://github.com/PatrickWeller/PanelPal.git"
        GIT_BRANCH = "issue109"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: "${GIT_BRANCH}", 
                    url: "${REPO_URL}"
            }
        }

        stage('Setup Conda Environment') {
            steps {
                script {
                    // Create and activate the Conda environment from environment.yaml
                    sh """
                        conda env create -f environment.yaml -n ${CONDA_ENV_NAME} || conda env update -f environment.yaml -n ${CONDA_ENV_NAME}
                    """
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image for PanelPal
                    sh """
                        docker build -t panelpal .
                    """
                }
            }
        }
        stage('Activate Conda Environment and Install Dependencies') {
            steps {
                script {
                    // Activate Conda environment and install the package
                    sh """
                        . /opt/conda/etc/profile.d/conda.sh
                        conda activate ${CONDA_ENV_NAME}
                        pip install .
                    """
                }
            }
        }
        stage('Run Tests') {
            steps {
                script {
                    // Run Pytest in the activated environment
                    sh """
                        . /opt/conda/etc/profile.d/conda.sh
                        conda activate ${CONDA_ENV_NAME}
                        pytest
                    """
                }
            }
        }
    }
    post {
        always {
            echo 'Cleaning up...'
            script {
                // Deactivate and remove the environment
                sh """
                    . /opt/conda/etc/profile.d/conda.sh
                    conda deactivate || true
                    conda env remove -n ${CONDA_ENV_NAME} || true
                """
            }
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}