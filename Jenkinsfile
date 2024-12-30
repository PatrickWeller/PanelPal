pipeline {
    agent any // This specifies that the pipeline can run on any available agent.

    environment {
        CONDA_PATH = '/usr/share/miniconda'  // Path to Miniconda
        CONDA_ENV = 'PanelPal'  // Name of the Conda environment
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Checkout the repository code
                git 'https://github.com/PatrickWeller/PanelPal.git'
            }
        }

        stage('Set up Conda and Create Environment') {
            steps {
                // Install Miniconda and create the Conda environment
                sh """
                    # Install Miniconda
                    curl -sSLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
                    bash miniconda.sh -b -p ${CONDA_PATH}
                    source ${CONDA_PATH}/bin/activate
                    conda init bash

                    # Create or update the Conda environment
                    conda env create --file env/environment.yaml || conda env update -f env/environment.yml --prune
                """
            }
        }

        stage('Install PanelPal') {
            steps {
                // Install the PanelPal package in editable mode
                sh 'pip install .'
            }
        }

        stage('Run Automated Tests') {
            steps {
                // Activate the Conda environment and run tests
                sh """
                    source ${CONDA_PATH}/bin/activate
                    conda activate ${CONDA_ENV}
                    pytest test/
                """
            }
        }
    }

    post {
        success {
            // This block is executed if the pipeline runs successfully.
            echo 'Pipeline succeeded! Your project is built and tested.'
        }
        failure {
            // This block is executed if the pipeline fails.
            echo 'Pipeline failed. Please check the logs for details.'
        }
    }
}