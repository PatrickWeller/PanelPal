pipeline {
    agent any // This specifies that the pipeline can run on any available agent.

    environment {
        CONDA_PATH = '/usr/share/miniconda'  // Path to Miniconda
        CONDA_ENV = 'PanelPal'  // Name of the Conda environment
    }

    stages {
    //     stage('Checkout Code') {
    //         steps {
    //             // Checkout the repository code
    //             git 'https://github.com/PatrickWeller/PanelPal.git'
    //         }
    //     }

        stage('Checkout Code') {
            steps {
                git branch: 'issue109', 
                    url: 'https://github.com/PatrickWeller/PanelPal.git'
            }
        }

        stage('Set up Conda and Create Environment') {
            steps {
                // Install Miniconda and create the Conda environment
                sh """
                    #!/usr/bin/env bash
                    # Install Miniconda
                    curl -sSLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
                    bash miniconda.sh -b -u -p ${CONDA_PATH}
                    # Add conda to PATH and then activate it
                    export PATH=/usr/share/miniconda/bin:$PATH
                    bash -c 'source /usr/share/miniconda/bin/activate'

                    # Create or update the Conda environment
                    conda env create --file env/environment.yaml || conda env update -f env/environment.yaml --prune
                """
            }
        }

        stage('Install PanelPal') {
            steps {
                // Install the PanelPal package in editable mode
                sh """
                #!/usr/bin/env bash
                conda run -n PanelPal python pip install --upgrade pip
                conda run -n PanelPal python pip install .
                """
            }
        }

        stage('Run Automated Tests') {
            steps {
                // Activate the Conda environment and run tests
                sh """
                    #!/usr/bin/env bash
                    conda run -n PanelPal python pytest test/
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