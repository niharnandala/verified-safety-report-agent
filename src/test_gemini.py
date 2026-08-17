import pandas as pd
from data_prep import clean_data
from report_context import build_all_packets
from verified_generation import generate_verified_section
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "Bisoprolol_icsr_sample_1068rows.xlsx"

df = pd.read_excel(DATA_PATH)
cleaned = clean_data(df)

packets = build_all_packets(cleaned)

section_key = "serious_cases_15day"
packet = packets[section_key]

result = generate_verified_section(section_key, packet)
print(result)