#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "fastdvdnet"))

import argparse
from denoiser import load_model
from video_enhancer import process_video


def main():
    parser = argparse.ArgumentParser(description="Enhance videos using FastDVDnet")
    parser.add_argument("input", help="Input video file")
    parser.add_argument("output", help="Output video file")
    parser.add_argument("--model", help="Path to pretrained model weights")
    parser.add_argument("--noise", type=int, default=25, help="Noise sigma (0-255, default: 25)")
    parser.add_argument("--device", choices=['cuda', 'mps', 'cpu'], help="Device to use")
    parser.add_argument("--temp-dir", default="temp", help="Temporary directory for frames")

    args = parser.parse_args()

    model, device = load_model(model_path=args.model, device=args.device)

    process_video(
        model=model,
        device=device,
        input_video=args.input,
        output_video=args.output,
        noise_sigma=args.noise,
        temp_dir=args.temp_dir
    )


if __name__ == "__main__":
    main()
