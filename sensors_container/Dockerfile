# Use a base image suitable for Raspberry Pi with Python and GPIO support
FROM balenalib/raspberrypi3-python:3.9-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    build-essential \
    cmake \
    wget \
    patch \
    libatlas-base-dev \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Download and install the latest version of pip directly
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && rm get-pip.py

# Upgrade setuptools and wheel (important for building packages)
RUN pip3 install --upgrade setuptools wheel

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --use-deprecated=legacy-resolver

# Copy the sensor script into the container
COPY sensors_container_code.py /app/
WORKDIR /app

# Set the entrypoint to run the sensor script
CMD ["python3", "sensors_container_code.py"]
