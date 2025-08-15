# Use a stable Python 3.11 slim image as the base
FROM python:3.11-slim

# Set environment variables for the container
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
# Cloud Run will automatically provide this PORT variable.
# We set a default of 8080 for local testing.
ENV PORT 8080

# Create and set the working directory
WORKDIR $APP_HOME

# Copy and install Python dependencies in a separate layer to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Command to run the application by invoking gunicorn as a Python module.
# This is the most reliable method as it doesn't depend on the system's PATH.
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "app:app"]
