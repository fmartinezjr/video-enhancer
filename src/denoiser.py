import os
import numpy as np
import torch
import cv2
import sys
from pathlib import Path

# Add fastdvdnet to path
fastdvdnet_path = Path(__file__).parent.parent / "fastdvdnet"
sys.path.insert(0, str(fastdvdnet_path))

from models import FastDVDnet  # type: ignore
from utils import remove_dataparallel_wrapper  # type: ignore


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
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
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
    input_tensor = input_tensor.view(
        1, -1, input_tensor.shape[2], input_tensor.shape[3]
    )
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
