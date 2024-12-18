# Base image with slim Python
FROM continuumio/miniconda3:4.12.0

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH=/opt/conda/envs/PanelPal/bin:$PATH \
    CONDA_DEFAULT_ENV=PanelPal

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Create the Conda environment
RUN conda env create -f environment.yaml && \
    conda clean -a

# Create an entrypoint script
RUN echo '#!/bin/bash\n\
source /opt/conda/etc/profile.d/conda.sh\n\
conda activate PanelPal\n\
export PATH=/opt/conda/envs/PanelPal/bin:$PATH\n\
exec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Install the package in the specified environment
RUN /opt/conda/envs/PanelPal/bin/pip install --no-cache-dir -e .

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]