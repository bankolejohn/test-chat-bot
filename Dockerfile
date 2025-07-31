FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for development
RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (including development tools)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    pytest \
    pytest-flask \
    pytest-cov \
    black \
    flake8 \
    ipython

# Copy application code
COPY . .

# Create necessary directories and files
RUN mkdir -p /app/logs /app/backups /app/data && \
    touch /app/conversations.json && \
    touch /app/training_data.json

# Set development environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for development
EXPOSE 5000

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run Flask development server with auto-reload
CMD ["python", "app.py"]