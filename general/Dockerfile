# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
# 1. Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# 2. Ensure logs are delivered immediately to the terminal
ENV PYTHONUNBUFFERED=1
# 3. Explicitly set the Flask application entry point
ENV FLASK_APP=deploy.py

# Set the working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies without saving pip cache to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
# The .dockerignore file will prevent unwanted files from being copied
COPY . .

# Expose the port Flask is configured to run on
EXPOSE 5000

# Start the application using the deploy.py script
CMD ["python", "deploy.py"]
