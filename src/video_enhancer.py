import shutil
from pathlib import Path
import cv2
from tqdm import tqdm

from .frame_io import extract_frames, load_frames, reassemble_video, extract_audio
from .denoiser import denoise_frames


def process_video(
    model, device, input_video, output_video, noise_sigma=25, temp_dir="temp"
):
    """
    Pipeline: extract → denoise → reassemble.

    Args:
        model: FastDVDnet model
        device: Torch device
        input_video: Path to input video
        output_video: Path to output video
        noise_sigma: Noise level (0-255)
        temp_dir: Temporary directory for frames
    """
    input_path = Path(input_video)
    output_path = Path(output_video)
    temp_path = Path(temp_dir)

    frames_dir = temp_path / "frames"
    enhanced_dir = temp_path / "enhanced"
    audio_path = temp_path / "audio.aac"

    try:
        temp_path.mkdir(parents=True, exist_ok=True)

        print("Extracting audio")
        has_audio = extract_audio(input_path, audio_path)
        if has_audio:
            print("Audio extracted successfully")
        else:
            print("No audio track found in input video")

        fps, total_frames = extract_frames(input_path, frames_dir)

        enhanced_dir.mkdir(parents=True, exist_ok=True)

        print(f"Processing {total_frames} frames...")
        with tqdm(total=total_frames, desc="Denoising frames", mininterval=1.0) as pbar:
            for i in range(total_frames):

                if i > 0 and i % 10 == 0:
                    print(
                        f"Denoised {i}/{total_frames} frames ({i*100//total_frames}%)"
                    )

                if i < 2:
                    start_idx = 0
                elif i >= total_frames - 2:
                    start_idx = max(0, total_frames - 5)
                else:
                    start_idx = i - 2

                frame_sequence = load_frames(frames_dir, start_idx, num_frames=5)

                if frame_sequence is None:
                    src = frames_dir / f"frame_{i:05d}.png"
                    dst = enhanced_dir / f"frame_{i:05d}.png"
                    shutil.copy(src, dst)
                else:
                    enhanced_frame = denoise_frames(
                        model, device, frame_sequence, noise_sigma
                    )

                    output_frame_path = enhanced_dir / f"frame_{i:05d}.png"
                    cv2.imwrite(str(output_frame_path), enhanced_frame)

                pbar.update(1)

        print("Reassembling video...")
        reassemble_video(
            enhanced_dir, output_path, fps, audio_path if has_audio else None
        )

        print(f"✓ Enhanced video saved to: {output_path}")

    finally:
        if temp_path.exists():
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_path)
