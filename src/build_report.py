import sys
import os
import pandas as pd
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from data_prep import clean_data
from report_context import build_all_packets
from verified_generation import generate_verified_section
from prompts.history_of_actions import FIXED_OUTPUT as HISTORY_FIXED_OUTPUT

DATA_PATH = Path(__file__).parent.parent / "data" / "Bisoprolol_icsr_sample_1068rows.xlsx"

df = pd.read_excel(DATA_PATH)
cleaned = clean_data(df)
packets = build_all_packets(cleaned)

results = {}

for section_key, packet in packets.items():
    print(f"generating: {section_key}...")

    if section_key == "history_of_actions":
        # no llm call here at all, no data was given for this section so
        # its jst fixed honest text, never invented
        results[section_key] = {
            "section": section_key,
            "text": HISTORY_FIXED_OUTPUT,
            "passed_on_first_try": True,
            "final_verified": True,
            "flagged_on_attempt_1": None,
        }
        continue

    if section_key == "case_index_listing":
        # this ones a raw table straight off the df, not llm generated
        # text, so nothing to verify here either, its literally the data
        results[section_key] = {
            "section": section_key,
            "text": packet,
            "passed_on_first_try": True,
            "final_verified": True,
            "flagged_on_attempt_1": None,
        }
        continue

    results[section_key] = generate_verified_section(section_key, packet)

# printing everything at the end so its easy to read top to bottom
print("\n" + "=" * 60)
for section_key, result in results.items():
    print(f"\n### {section_key} ###\n")
    if section_key == "case_index_listing":
        print(result["text"].head())
    else:
        print(result["text"])

# quick summary at the very end, so i dont hav to scroll to find
# wich sections still need a human look
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY:\n")
for section_key, result in results.items():
    status = "✅ verified" if result["final_verified"] else "⚠ NEEDS REVIEW"
    print(f"{section_key}: {status}")