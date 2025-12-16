# This Dockerfile is optimized for AWS Batch with GPU support.
# For mac, run natively with Python to use MPS acceleration.
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ /app/src/
COPY fastdvdnet/ /app/fastdvdnet/

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-u", "-m", "src.video_processor_batch"]
