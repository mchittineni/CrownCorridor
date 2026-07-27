# Use official lightweight Python image
FROM python:3.11-slim

LABEL maintainer="Manideep Chittineni"
LABEL description="IaCSecBench — An Infrastructure-as-Code Security Benchmark Framework"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY experiments/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application source code
COPY . /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Entrypoint executes reproducible benchmark experiments
ENTRYPOINT ["python3", "-m", "security_framework.engine.engine"]
CMD ["infrastructure/"]
