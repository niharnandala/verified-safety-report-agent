import os
import json
import sys
import time
from dotenv import load_dotenv
from groq import Groq

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from prompts import SYSTEM_PROMPT, SECTION_INSTRUCTIONS

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL_NAME = "llama-3.3-70b-versatile"


def call_groq_with_retry(fn, *args, max_attempts=3, wait_seconds=5, **kwargs):
    # same idea as the gemini version, jst for wen groqs servers are busy
    # or i hit a transient rate limit, not a real problem with my prompt
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts:
                raise
            print(f"groq request failed ({e.__class__.__name__}), retrying in {wait_seconds}s (attempt {attempt}/{max_attempts})")
            time.sleep(wait_seconds)


def generate_section(section_key, packet, correction=None):
    packet_json = json.dumps(packet, indent=2, default=str)

    instruction = SECTION_INSTRUCTIONS[section_key]
    full_prompt = f"{instruction}\n\n<packet>\n{packet_json}\n</packet>"

    if correction:
        full_prompt += f"\n\n<correction>\n{correction}\n</correction>"

    # groq doesnt have a seperate "system_instruction" slot like gemini did,
    # its jst a normal messages list wth the system prompt as the frst entry
    response = call_groq_with_retry(
        client.chat.completions.create,
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt},
        ],
        temperature=0.15,
        max_tokens=500,
    )
    return response.choices[0].message.content