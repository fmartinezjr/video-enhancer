#!/usr/bin/env python3
"""
Video enhancement using FastDVDnet for AWS Batch.
Downloads from S3, processes, uploads to S3, sends SNS notifications.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "fastdvdnet"))

import argparse
from .denoiser import load_model
from .video_enhancer import process_video
from .s3_utils import download_from_s3, upload_to_s3, send_notification


def main():
    parser = argparse.ArgumentParser(
        description="Enhance videos using FastDVDnet (AWS Batch)"
    )
    parser.add_argument("input", help="Input S3 URI (s3://bucket/key)")
    parser.add_argument("output", help="Output S3 URI (s3://bucket/key)")
    parser.add_argument("--model", help="Path to pretrained model weights")
    parser.add_argument(
        "--noise", type=int, default=25, help="Noise sigma (0-255, default: 25)"
    )
    parser.add_argument(
        "--device", choices=["cuda", "mps", "cpu"], help="Device to use"
    )

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        input_local = tmpdir_path / "input.mp4"
        output_local = tmpdir_path / "output.mp4"
        work_dir = tmpdir_path / "work"
        work_dir.mkdir()

        try:
            download_from_s3(args.input, str(input_local))

            model, device = load_model(model_path=args.model, device=args.device)

            process_video(
                model=model,
                device=device,
                input_video=str(input_local),
                output_video=str(output_local),
                noise_sigma=args.noise,
                temp_dir=str(work_dir),
            )

            upload_to_s3(str(output_local), args.output)

            message = f"""Video processing completed successfully!

Input:  {args.input}
Output: {args.output}
Noise sigma: {args.noise}
"""
            send_notification(message, subject="Video Enhancement Complete ✓")

        except Exception as e:
            error_message = f"""Video processing FAILED!

Input:  {args.input}
Output: {args.output}

Error: {str(e)}
"""
            send_notification(error_message, subject="Video Enhancement Failed ✗")
            raise


if __name__ == "__main__":
    main()
