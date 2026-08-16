import os
import json
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time
from google.genai import errors

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from prompts import SYSTEM_PROMPT, SECTION_INSTRUCTIONS

load_dotenv()

def call_gemini_with_retry(fn, *args, max_attempts=3, wait_seconds=5, **kwargs):
    # this one is for wen googles servers themselves are jst busy, totally
    # diff problem frm grounding, jst waitin n askin again shd be enough
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except errors.ServerError:
            if attempt == max_attempts:
                raise
            print(f"gemini servers busy, retrying in {wait_seconds}s (attempt {attempt}/{max_attempts})")
            time.sleep(wait_seconds)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL_NAME = "gemini-3.5-flash"

def generate_section(section_key, packet, correction=None):
    packet_json = json.dumps(packet, indent=2, default=str)

    instruction = SECTION_INSTRUCTIONS[section_key]
    full_prompt = f"{instruction}\n\n<packet>\n{packet_json}\n</packet>"

    if correction:
        full_prompt += f"\n\n<correction>\n{correction}\n</correction>"

    print("FULL PROMPT SENT:\n")
    print(full_prompt)
    print("---")

    response = call_gemini_with_retry(
        client.models.generate_content,
        model=MODEL_NAME,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.15,
            max_output_tokens=500,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text