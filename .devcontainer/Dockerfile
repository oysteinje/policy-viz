FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
# Install Python packages
RUN pip install --no-cache-dir \
    flask \
    requests \
    beautifulsoup4 \
    azure-identity \
    azure-mgmt-subscription \
    azure-mgmt-resource \
    azure-mgmt-managementgroups \
    streamlit
