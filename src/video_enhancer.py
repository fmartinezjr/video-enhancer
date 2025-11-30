import os
import shutil
from pathlib import Path
import cv2
import numpy as np
import torch
from tqdm import tqdm

from fastdvdnet.models import FastDVDnet
from fastdvdnet.utils import remove_dataparallel_wrapper


def load_model(model_path=None, device=None):
    """
    Load FastDVDnet model.

    Args:
        model_path: Path to pretrained model weights
        device: Device to run on ('cuda', 'mps', or 'cpu')

    Returns:
        Tuple of (model, device)
    """
    if device is None:
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
        else:
            device = torch.device('cpu')
    else:
        device = torch.device(device)

    print(f"Using device: {device}")

    model = FastDVDnet(num_input_frames=5)

    if model_path and os.path.exists(model_path):
        state_dict = torch.load(model_path, map_location=device)
        state_dict = remove_dataparallel_wrapper(state_dict)
        model.load_state_dict(state_dict)
        print(f"Loaded model from: {model_path}")
    else:
        print("No pretrained model loaded.")

    model.to(device)
    model.eval()

    return model, device


def extract_frames(video_path, output_dir):
    """Extract frames from video using OpenCV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Extracting {total_frames} frames from {video_path.name}...")

    frame_idx = 0
    with tqdm(total=total_frames, desc="Extracting frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_path = output_dir / f"frame_{frame_idx:05d}.png"
            cv2.imwrite(str(frame_path), frame)
            frame_idx += 1
            pbar.update(1)

    cap.release()
    return fps, frame_idx


def load_frames(frame_dir, start_idx, num_frames=5):
    """Load a sequence of frames."""
    frames = []
    frame_dir = Path(frame_dir)

    for i in range(start_idx, start_idx + num_frames):
        frame_path = frame_dir / f"frame_{i:05d}.png"
        if not frame_path.exists():
            return None

        frame = cv2.imread(str(frame_path))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)

    return frames


def denoise_frames(model, device, frames, noise_sigma=25):
    """
    Denoise a sequence of frames using FastDVDnet.

    Args:
        model: FastDVDnet model
        device: Torch device
        frames: List of 5 frames (numpy arrays)
        noise_sigma: Noise level (0-255), default 25

    Returns:
        Denoised middle frame
    """
    frame_tensors = []
    for frame in frames:
        frame_t = torch.from_numpy(frame.transpose(2, 0, 1)).float() / 255.0
        frame_tensors.append(frame_t)

    input_tensor = torch.stack(frame_tensors, dim=0)
    input_tensor = input_tensor.view(1, -1, input_tensor.shape[2], input_tensor.shape[3])
    input_tensor = input_tensor.to(device)

    noise_map = torch.FloatTensor([noise_sigma / 255.0])
    noise_map = noise_map.view(1, 1, 1, 1)
    noise_map = noise_map.expand(1, 1, input_tensor.shape[2], input_tensor.shape[3])
    noise_map = noise_map.to(device)

    with torch.no_grad():
        output = model(input_tensor, noise_map)

    output_frame = output.squeeze(0).cpu().numpy()
    output_frame = np.transpose(output_frame, (1, 2, 0))
    output_frame = np.clip(output_frame * 255.0, 0, 255).astype(np.uint8)
    output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

    return output_frame


def reassemble_video(frames_dir, output_path, fps):
    """Reassemble frames into video using OpenCV."""
    frames_dir = Path(frames_dir)
    frame_files = sorted(frames_dir.glob("frame_*.png"))

    if not frame_files:
        raise ValueError(f"No frames found in {frames_dir}")

    first_frame = cv2.imread(str(frame_files[0]))
    height, width = first_frame.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    for frame_file in tqdm(frame_files, desc="Writing video"):
        frame = cv2.imread(str(frame_file))
        out.write(frame)

    out.release()


def process_video(model, device, input_video, output_video, noise_sigma=25, temp_dir="temp"):
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

    try:
        fps, total_frames = extract_frames(input_path, frames_dir)

        enhanced_dir.mkdir(parents=True, exist_ok=True)

        print(f"Processing {total_frames} frames...")
        with tqdm(total=total_frames, desc="Denoising frames") as pbar:
            for i in range(total_frames):

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
                    enhanced_frame = denoise_frames(model, device, frame_sequence, noise_sigma)

                    output_frame_path = enhanced_dir / f"frame_{i:05d}.png"
                    cv2.imwrite(str(output_frame_path), enhanced_frame)

                pbar.update(1)

        print(f"Reassembling video...")
        reassemble_video(enhanced_dir, output_path, fps)

        print(f"✓ Enhanced video saved to: {output_path}")

    finally:
        if temp_path.exists():
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_path)
