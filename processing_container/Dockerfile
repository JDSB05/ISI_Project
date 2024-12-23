FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Set environment variables
ENV MQTT_BROKER=mqtt
ENV MQTT_PORT=1883

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code, templates, static files, and the wait script
COPY processing_container_code.py wait-for-it.sh ./
COPY templates/ ./templates/
COPY static/ ./static/

# Give execution permission to the script
RUN chmod +x wait-for-it.sh

# Set the entry command
CMD ["./wait-for-it.sh", "mqtt", "--", "python", "processing_container_code.py"]