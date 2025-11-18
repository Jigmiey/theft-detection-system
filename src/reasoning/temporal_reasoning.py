"""
temporal_reasoning.py
---------------------
Combines multiple frame-level descriptions into one temporal
analysis using Groq's text-reasoning models.
"""

import os
import json
import requests
from dotenv import load_dotenv
import re

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"  # text-only reasoning model

TEMPORAL_PROMPT = """
You are a retail security analyst reviewing a short CCTV clip.

Below are frame-by-frame scene descriptions in chronological order.
Analyze the **temporal sequence** and detect suspicious transitions
(e.g., concealment, rapid movement toward exits, interacting oddly with bags).
Especially the sequence of actions of the particular person over time.
and report if the person is commiting potential theft or not.

Return a JSON with:
{
  "timeline_summary": str,
  "suspect_actions": [str],
  "risk_assessment": "normal | low | medium | high",
  "alert": bool
}
Be concise, analytical, and reason about behavior over time.
"""

def analyze_temporal_behavior(frame_summaries):
    """
    frame_summaries: list of dicts like [{"frame":0,"description":json_string}, ...]
    """
    if not GROQ_API_KEY:
        raise EnvironmentError("GROQ_API_KEY missing from .env")

    # join frames into one timeline text
    joined = "\n".join(
        [f"Frame {f['frame']}: {f['description']}" for f in frame_summaries]
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You reason over time-series CCTV descriptions."}]},
            {"role": "user", "content": [{"type": "text", "text": TEMPORAL_PROMPT + "\n" + joined}]},
        ],
        "max_tokens": 600,
        "temperature": 0.3,
    }

    response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload)
    if response.status_code != 200:
        print(" Reasoning error:", response.text)
        response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()

    # Extract JSON inside ```json ... ```
    json_match = re.search(r"```json(.*?)```", content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # fallback: try to parse any JSON substring
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        json_str = json_match.group(0).strip() if json_match else "{}"

    try:
        parsed = json.loads(json_str)
        return parsed
    except json.JSONDecodeError:
        print(" Could not parse JSON output. Returning raw text.")
        return {"raw_output": content}