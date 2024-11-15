FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the processing script and model files into the container
COPY processing_container_code.py coco.names ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt frozen_inference_graph.pb /app/
WORKDIR /app

# Set the entrypoint to run the processing script
CMD ["python", "processing_container_code.py"]
