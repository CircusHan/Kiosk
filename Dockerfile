# Dockerfile for Healthcare Kiosk Application

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    fonts-nanum \
    espeak \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs static/certificates locale

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM=offscreen

# Expose ports
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app.main", "--api-only"]