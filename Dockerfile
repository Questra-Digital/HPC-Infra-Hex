# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Create the ~/.local/bin directory if it doesn't exist
RUN mkdir -p ~/.local/bin

# Move the kubectl binary to ~/.local/bin
RUN mv /usr/local/bin/kubectl ~/.local/bin/

# Add ~/.local/bin to the PATH
ENV PATH="${PATH}:/root/.local/bin"

# Add the command to update PATH in ~/.bashrc
RUN echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
# Install Helm
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh
    
    
# Add the Helm repository for JupyterHub
RUN helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/

# Update the Helm repositories
RUN helm repo update
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose port 80
EXPOSE 80

# Define environment variable
ENV NAME World

# Specify the command to run on container start
ENTRYPOINT ["python", "app.py"]

