#!/bin/bash
# Activate the Conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate PanelPal

# Execute the command passed to the container
exec "$@"