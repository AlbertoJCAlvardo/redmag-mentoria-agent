# Use a stable Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables for the container
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
# Cloud Run will automatically provide this PORT variable.
# We set a default of 8080 for local testing.
ENV PORT=8080

# Create and set the working directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies in a separate layer to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port
EXPOSE $PORT

# Health check using Python instead of curl
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/health')" || exit 1

# Command to run the application using uvicorn directly (more reliable for FastAPI)
CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 120
