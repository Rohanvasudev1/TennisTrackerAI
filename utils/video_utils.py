import cv2
from pathlib import Path
def read_video(vid_path):
    cap = cv2.VideoCapture(str(vid_path))

    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {vid_path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    if not frames:
        raise ValueError(f"No frames read from {vid_path} (file may be empty or corrupt)")

    return frames

def save_video(output_video_frames, output_video_path):
    if not output_video_frames:
        raise ValueError("No frames supplied to save_video()")

    # Make sure the output directory exists
    out_path = Path(output_video_path).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    h, w = output_video_frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(str(out_path), fourcc, 24, (w, h))

    if not out.isOpened():
        raise IOError(f"Could not open VideoWriter for {out_path}")

    for frame in output_video_frames:
        if frame.shape[:2] != (h, w):
            raise ValueError("All frames must have the same resolution")
        out.write(frame)

    out.release()
