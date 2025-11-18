from src.capture.video_capture import iter_video_frames
#from src.vlm.describe_scene import describe_frame
from src.vlm.describe_scene_groq import describe_frame_groq
from src.reasoning.temporal_reasoning import analyze_temporal_behavior
from src.alert.send_alert import send_email_alert
import json
from pathlib import Path
import time

if __name__ == "__main__":
    video = "data/samples/vid2.mp4"
    
    output_text_path =Path("outputs/frame_summaries_vid2.txt")
    output_text_path.parent.mkdir(parents=True,exist_ok=True)
    
    frame_summaries = []
    
    with output_text_path.open("w",encoding="utf-8") as f_out:
        f_out.write("===FRAME SUMMARIES ===\n\n")
    
        for i,img in iter_video_frames(video,sample_fps=1.0,max_frames=100):
            print(f"Processing frame : {i}")
            desc = describe_frame_groq(img)
            
            frame_summaries.append({"frame":i,"description":desc})
            f_out.write(f"---Frame {i}---\n")
            try:
                parsed = json.loads(desc)
                json.dump(parsed, f_out, indent =2)
            except Exception:
                f_out.write(desc)
            f_out.write("\n\n")
            time.sleep(2.5)
            #print(f"\nFrame {i}: {desc}")
    
    timeline_result = analyze_temporal_behavior(frame_summaries)
    print("\n Temporal Reasoning Output:\n", timeline_result)
    if timeline_result.get("alert"):
        subject = f"[ALERT] Theft Risk: {timeline_result.get('risk_assessment', 'Unknown').upper()}"
        message = (
            f"Incident summary:\n{timeline_result.get('timeline_summary')}\n\n"
            f"Actions: {timeline_result.get('suspect_actions')}"
        )
        send_email_alert(subject, message)
        print("Triggered alert send for this clip")
    else:
        print(" No alert triggered for this clip.")
    