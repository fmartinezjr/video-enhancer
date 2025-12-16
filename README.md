# Video Enhancer

Deep learning video denoising using [FastDVDnet](https://github.com/m-tassano/fastdvdnet).

## Features

Removes noise using FastDVDnet

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -e ".[dev]" #for dev
```

## Usage

### Basic usage

```bash
python -m src.video_processor_local input/my_video.mp4 output/enhanced_video.mp4 --model fastdvdnet/model.pth
```

### Adjust noise level

```bash
python -m src.video_processor_local input/my_video.mp4 output/enhanced_video.mp4 --model fastdvdnet/model.pth --noise 30
```

Higher noise values (0-255) apply more aggressive denoising. Default is 25.

### Force CPU mode

```bash
python -m src.video_processor_local input/my_video.mp4 output/enhanced_video.mp4 --device cpu
```

### All options

```bash
python -m src.video_processor_local --help
```

## How It Works

1. Extract frames from video
2. Process 5-frame sequences through FastDVDnet
3. Save denoised frames
4. Reassemble into video

## Performance

- **With GPU (M1/M2/M3 or NVIDIA):** ~5-15 minutes per minute of video
- **CPU only:** Much slower (hours for longer videos)

## Local Dev Checks

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type check
mypy src/
```

## Run on AWS Infra

```bash
aws s3 cp video.mp4 s3://$BUCKET/input/
```