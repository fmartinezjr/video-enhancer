from pathlib import Path
import cv2
from tqdm import tqdm


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
