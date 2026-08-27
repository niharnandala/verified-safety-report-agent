import re
import pandas as pd
import numpy as np

DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})(?:\s\d{2}:\d{2}:\d{2})?")

# fixed pader/regulatory phrases tht happen to contain digits, not numbers
# derived frm the dataset. stripping the exact phrase, not the number
# itself, so "15" elsewhere in the text (if it ever shows up unrelated
# to this phrase) still gets checked normally, not blanket ignored
SAFE_PHRASE_PATTERNS = [
    re.compile(r"15-day"),
]


def strip_safe_phrases(text):
    for pattern in SAFE_PHRASE_PATTERNS:
        text = pattern.sub("", text)
    return text


def extract_dates(text):
    return set(DATE_PATTERN.findall(text))


def strip_dates(text):
    return DATE_PATTERN.sub("", text)


def extract_numbers(text):
    text_without_dates = strip_dates(text)
    text_clean = strip_safe_phrases(text_without_dates)
    # thousands separators: "1,024" was splitting into 1 and 024->24, n those
    # fragments (23, 24) got falsely flagged. drop the comma between digits so
    # "1,024" reads as one number 1024, matching how its stored in the packet.
    text_clean = re.sub(r"(?<=\d),(?=\d)", "", text_clean)
    # match whole numbers only, no leading sign. a range like "18-64" used to
    # read the hyphen as a minus n produce -64, matching whole numbers instead
    # splits it cleanly into 18 n 64. no genuine negative counts exist here.
    matches = re.findall(r"\d+(?:\.\d+)?", text_clean)
    return {float(m) for m in matches}


def flatten_numbers(obj):
    numbers = set()
    if isinstance(obj, dict):
        for v in obj.values():
            numbers |= flatten_numbers(v)
    elif isinstance(obj, pd.Series):
        # age group labels like "18-64" live in the index, not the values,
        # missed these entirely before, checking both now
        numbers |= flatten_numbers(list(obj.index))
        for v in obj.values:
            numbers |= flatten_numbers(v)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            numbers |= flatten_numbers(v)
    elif isinstance(obj, str):
        # category labels like "75+" or "18-64" have real digits baked in,
        # gemini will naturally quote them verbatim, so pulling embeded
        # numbers out of packet strings too now, not jst treating any
        # string as automatically number free
        numbers |= extract_numbers(obj)
    elif isinstance(obj, (int, float, np.integer, np.floating)) and not isinstance(obj, bool):
        numbers.add(float(obj))
    return numbers


def flatten_dates(obj):
    dates = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(k, "strftime"):
                dates.add(k.strftime("%Y-%m-%d"))
            elif isinstance(k, str):
                match = DATE_PATTERN.search(k)
                if match:
                    dates.add(match.group(1))
            dates |= flatten_dates(v)
    elif isinstance(obj, pd.Series):
        dates |= flatten_dates(list(obj.index))
        for v in obj.values:
            dates |= flatten_dates(v)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            dates |= flatten_dates(v)
    elif hasattr(obj, "strftime"):
        dates.add(obj.strftime("%Y-%m-%d"))
    elif isinstance(obj, str):
        # a string value can hold a real date too now, like "2024-12-27",
        # since i started formatting dates as clean strings instead of
        # raw timestamp objects. same idea as wht flatten_numbers already
        # does for embeded numbers in strings, jst for dates now
        match = DATE_PATTERN.search(obj)
        if match:
            dates.add(match.group(1))
    return dates


def verify_section(generated_text, section_packet):
    # a blank answer used to pass as "clean" here: no numbers in it means
    # nothing to flag. but blank = a missing section, not a good one. flag it.
    if not generated_text or not generated_text.strip():
        return {
            "not_found_numbers": [],
            "not_found_dates": [],
            "empty_output": True,
        }

    # models sometimes write dates/ranges with unicode dashes (‑ – —) instead
    # of a plain "-", which slips past the date matcher: "2025‑06‑22" isnt seen
    # as a date, so its digits (2025, 6, 22) leak thru n get falsely flagged.
    # flatten them all to a plain "-" first.
    generated_text = re.sub(r"[\u2010-\u2015]", "-", generated_text)

    text_numbers = extract_numbers(generated_text)
    packet_numbers = flatten_numbers(section_packet)
    not_found_numbers = [n for n in text_numbers if n not in packet_numbers]

    text_dates = extract_dates(generated_text)
    packet_dates = flatten_dates(section_packet)
    not_found_dates = [d for d in text_dates if d not in packet_dates]

    return {
        "not_found_numbers": not_found_numbers,
        "not_found_dates": not_found_dates
    }