# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables (override with .env or secrets manager in production)
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]