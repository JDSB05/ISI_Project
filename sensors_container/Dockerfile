FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and the wait script
COPY sensors_container_code.py .
COPY wait-for-it.sh .

# Give execution permission to the script
RUN chmod +x wait-for-it.sh

# Set default environment variables
ENV MQTT_BROKER=mqtt
ENV MQTT_PORT=1883
ENV CAR_ID=carro1

# Set the entry command with host and port separated
CMD ["./wait-for-it.sh", "mqtt", "--", "python", "sensors_container_code.py"]