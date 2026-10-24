# Python 3.11 slim base image
FROM python:3.11-slim

# Stream logs immediately to Render dashboard and set default Render port
ENV PYTHONUNBUFFERED=1 \
    PORT=10000

# Install system dependencies:
# - ffmpeg: audio/video merging and extraction
# - curl: container health verification
# - nodejs: solves YouTube JS signature challenge in yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p temp_downloads

# Expose Render standard port
EXPOSE 10000

# Start Uvicorn server: exec replaces shell PID 1 so SIGTERM from Render shuts down cleanly
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
