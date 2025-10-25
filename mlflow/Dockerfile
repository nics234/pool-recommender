# mlflow/Dockerfile — lightweight, reliable MLflow image

FROM python:3.11-slim

# Set working directory
WORKDIR /mlflow

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc git curl && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install MLflow + dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir "mlflow>=2.10,<2.15" psycopg2-binary boto3

# Expose default MLflow port
EXPOSE 5000

# Run MLflow tracking server
CMD ["mlflow", "server", \
     "--backend-store-uri", "sqlite:///mlflow.db", \
     "--default-artifact-root", "./mlruns", \
     "--host", "0.0.0.0", \
     "--port", "5000"]
