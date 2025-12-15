FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ /app/src/
COPY fastdvdnet/ /app/fastdvdnet/

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-u", "-m", "src.video_processor"]
