from groq_client import generate_section
from verify_section import verify_section


def build_correction_message(not_found_numbers, not_found_dates):
    # phrasing this as a question to double check, not a flat statement tht
    # its wrong. if i say "this is wrong" as a fact n it was actually right
    # (jst a false positive frm my checker), gemini will obediently delete
    # a real number to make the complaint go away, n tht'd be worse then
    # jst leaving it alone
    lines = []
    if not_found_numbers:
        lines.append(
            f"these numbers couldnt be automatically matched against the source "
            f"data below: {not_found_numbers}. double check each one against the "
            f"packet, if it genuinely isnt there, correct or remove it, if it "
            f"actually is there n jst wasnt matched, you can keep it as is."
        )
    if not_found_dates:
        lines.append(
            f"these dates couldnt be automatically matched against the source "
            f"data below: {not_found_dates}. same thing, double check n only "
            f"change wht actually doesnt belong."
        )
    return " ".join(lines)


def generate_verified_section(section_key, packet):
    # attempt 1, straight generation no correction yet
    text = generate_section(section_key, packet)
    result = verify_section(text, packet)

    passed_first_try = not result["not_found_numbers"] and not result["not_found_dates"]

    if passed_first_try:
        return {
            "section": section_key,
            "text": text,
            "attempt_1_text": text,
            "passed_on_first_try": True,
            "final_verified": True,
            "flagged_on_attempt_1": None,
        }

    # jst one retry, not lettin this loop forever, if it fails twice
    # tht goes to human review flagged, not silently retried n retried
    flagged_attempt_1 = {
        "not_found_numbers": result["not_found_numbers"],
        "not_found_dates": result["not_found_dates"],
    }
    correction = build_correction_message(
        result["not_found_numbers"], result["not_found_dates"]
    )

    text_retry = generate_section(section_key, packet, correction=correction)
    result_retry = verify_section(text_retry, packet)

    final_verified = not result_retry["not_found_numbers"] and not result_retry["not_found_dates"]

    # even if attempt 2 passed clean, still carryin flagged_attempt_1 forward
    # so human review can see this one needed a correction round, a clean
    # pass on retry doesnt necessarily mean it was a real hallucination tht
    # got fixed, it coud also mean somethin true got deleted to dodge the
    # flag, only a human lookin at the actual source data can tell those apart
    return {
        "section": section_key,
        "text": text_retry,
        "passed_on_first_try": False,
        "final_verified": final_verified,
        "flagged_on_attempt_1": flagged_attempt_1,
    }