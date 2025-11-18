from src.capture.video_capture import iter_video_frames
from PIL import Image
from pathlib import Path
if __name__ == "__main__":
    video = "data/samples/vid2.mp4"
    output_dir = Path("data/Frames/vid2")
    output_dir.mkdir(parents=True,exist_ok=True)
    for i,img in iter_video_frames(video,sample_fps=1.0,max_frames=1000):
        print(f"frame no: {i}")
        file_path = output_dir/f"frame{i}.png"
        img.save(file_path)
    print("Frames are extracted and saved successfully!")