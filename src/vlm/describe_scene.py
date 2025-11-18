from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import torch

#One-time modelload (it will be cache locally)
MODEL_NAME = "Qwen/Qwen2-VL-2B-Instruct"
print(f" Loading model {MODEL_NAME}(this may take some time)...")

processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForVision2Seq.from_pretrained(
    MODEL_NAME,
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map ="auto"
)

SECURITY_PROMPT = """
You are a security analyst reviewing CCTV footage from a retail clothing store.

Your goal:
1. Identify how many people are visible in the frame.
2. Describe each person's position (front, back, left, right), approximate clothing color, and action.
3. Identify key visible objects or interactions (e.g., picking up clothes, bending, checking shelves).

Be factual, concise, and avoid assumptions.
"""

def describe_frame(img: Image.Image, 
                   prompt: str = SECURITY_PROMPT
                   ) -> str:
    """
    Takes a PIL image, uses an open-source Vision-Language Model(Qwen2-VL-2B-Instruct),
    and returns a short textual description.
    """   
    inputs = processor(text=prompt,
                   images=img,
                   return_tensors = "pt"
                   ).to(model.device)
    
    output_ids = model.generate(**inputs, max_new_tokens=64)
    description = processor.batch_decode(output_ids,skip_special_tokens = True)[0]
    return description.strip()
    

