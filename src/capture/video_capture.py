from pathlib import Path
from typing import Iterator, Tuple
import cv2
from PIL import Image

def iter_video_frames(video_path:str | Path,
                      sample_fps: float = 1.0,
                      max_frames: int | None = None
                      ) -> Iterator[Tuple[int,Image.Image]]:
    
    """
    Yields (frame_idx, PIL.Image) samples from the video at ~ sample_fps
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video:{video_path}")
    
    real_fps = cap.get(cv2.CAP_PROP_FPS)
    step = max(int(round(real_fps/sample_fps)),1)
    idx = 0
    out_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % step ==0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield out_idx,Image.fromarray(frame_rgb)
            out_idx +=1
            if max_frames is not None and out_idx >= max_frames:
                break
        idx += 1
    
    cap.release()
        
            