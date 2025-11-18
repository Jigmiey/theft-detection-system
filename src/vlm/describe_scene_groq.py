"""
describe_scene_groq.py
----------------------
Vision-Language Model (VLM) module for describing CCTV frames via Groq's
latest multimodal Llama models (e.g., Llama-4 Maverick 17B Vision).

Requirements:
    - pip install requests python-dotenv pillow
Environment:
    - GROQ_API_KEY=<your_api_key> in .env
"""

import os
import io
import base64
import requests
from PIL import Image
from dotenv import load_dotenv

# -----------------------------------------------------------
# Load environment
# -----------------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# ✅ Use Groq's latest multimodal model (verify in your console)
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct"

# -----------------------------------------------------------
# Prompt template
# -----------------------------------------------------------
SECURITY_PROMPT =SECURITY_PROMPT = """
You are a professional retail security analyst reviewing CCTV footage.

Your task has two parts:

1️⃣ **Observation Phase**
- Describe what you SEE in the frame: how many people, their relative positions, clothing colors, actions, and objects.

2️⃣ **Behavioral Analysis Phase**
- Identify whether any person's behavior might indicate potential theft, concealment, or abnormal actions.
- Focus on actions like: picking up items quickly, hiding items, avoiding staff, standing unusually close to exit, glancing around nervously, or interacting oddly with bags/pockets.
- Label each person’s behavior as: "normal", "possibly suspicious", or "potential theft".

Return output as JSON with:
{
  "people_count": int,
  "persons": [
    {
      "position": str,
      "clothing": str,
      "action": str,
      "behavior_label": "normal | possibly suspicious | potential theft"
    }
  ],
  "notable_objects": [str],
  "scene_summary": str,
  "risk_assessment": "normal | low | medium | high"
}
Be analytical and concise. Avoid repeating identical people unless visually distinct.
"""

TEMPERATURE = 0.4
MAX_TOKENS = 600

# -----------------------------------------------------------
# Helper: Convert PIL image → base64 string
# -----------------------------------------------------------
def pil_to_base64_png(img: Image.Image) -> str:
    """
    Converts a PIL Image to a base64-encoded PNG string.
    Used for inline image upload via Groq API.
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# -----------------------------------------------------------
# Core function
# -----------------------------------------------------------
def describe_frame_groq(img: Image.Image, prompt: str = SECURITY_PROMPT) -> str:
    """
    Sends an image + text prompt to Groq Vision-Language model.
    Returns the model's textual description or JSON.
    """

    if not GROQ_API_KEY:
        raise EnvironmentError("GROQ_API_KEY not found in .env file.")

    # Encode image as Base64 and wrap as Data URI
    image_b64 = pil_to_base64_png(img)
    image_data_uri = f"data:image/png;base64,{image_b64}"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You analyze CCTV footage for retail theft detection."}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_uri}},
                ],
            },
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }

    # Send request
    response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload)

    # Handle non-200 responses gracefully
    if response.status_code != 200:
        print("❌ Response error:", response.text)
        response.raise_for_status()

    data = response.json()

    # Extract model output
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[Error parsing Groq response: {e}]"

# -----------------------------------------------------------
# Debug/Test block (optional)
# -----------------------------------------------------------
if __name__ == "__main__":
    # Example test with one frame
    test_image_path = "data/samples/frame1.png"
    if os.path.exists(test_image_path):
        img = Image.open(test_image_path)
        print("🧠 Analyzing frame via Groq model...")
        result = describe_frame_groq(img)
        print(result)
    else:
        print("⚠️ Test image not found at:", test_image_path)


