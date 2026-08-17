import uuid
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver

from data_prep import clean_data
from report_context import build_all_packets
from verified_generation import generate_verified_section
from groq_client import generate_section
from verify_section import verify_section
from prompts import SECTION_INSTRUCTIONS, FIXED_OUTPUTS
import pandas as pd
from pathlib import Path


class ReviewState(TypedDict):
    results: Dict[str, Any]
    pending_regenerate: Dict[str, str]
    report_path: str

_packets_cache = {}


def generate_report(state):
    DATA_PATH = Path(__file__).parent.parent / "data" / "Bisoprolol_icsr_sample_1068rows.xlsx"
    df = pd.read_excel(DATA_PATH)
    cleaned = clean_data(df)
    packets = build_all_packets(cleaned)

    _packets_cache.clear()
    _packets_cache.update(packets)

    results = {}
    for section_key, packet in packets.items():
        # used to check "if section_key == 'history_of_actions'" n
        # "if section_key == 'case_index_listing'" by name here, wich meant
        # addin a new no-llm section later meant editin this fn too. now it
        # jst checks wehter tht section even HAS an instruction to send to
        # the model, tht answer already lives in prompts/, not hardcoded here
        if SECTION_INSTRUCTIONS[section_key] is None:
            fixed = FIXED_OUTPUTS[section_key]

            if fixed is not None:
                # fixed statement section (rn jst history_of_actions), no
                # data to format, jst use the fixed text as is
                results[section_key] = {
                    "section": section_key, "text": fixed,
                    "final_verified": True,
                }
            else:
                # no instruction AND no fixed text means this section is
                # literally jst raw data (rn jst case_index_listing), format
                # any date columns to plain strings so they dont sneak
                # raw Timestamp objects into graph state, then dump as records
                formatted = packet.copy()
                for col in formatted.columns:
                    if pd.api.types.is_datetime64_any_dtype(formatted[col]):
                        formatted[col] = formatted[col].dt.strftime("%Y-%m-%d")
                results[section_key] = {
                    "section": section_key,
                    "text": formatted.to_dict("records"),
                    "final_verified": True,
                }
            continue

        results[section_key] = generate_verified_section(section_key, packet)

    return {"results": results, "pending_regenerate": {}}


def human_review(state):
    decisions = interrupt(state["results"])

    results = dict(state["results"])
    pending_regenerate = {}

    for section_key, decision in decisions.items():
        action = decision["action"]
        if action == "approve":
            continue
        elif action == "edit":
            results[section_key]["text"] = decision["edited_text"]
            results[section_key]["final_verified"] = True
        elif action == "regenerate":
            pending_regenerate[section_key] = decision["instructions"]

    return {"results": results, "pending_regenerate": pending_regenerate}


def apply_regenerations(state):
    results = dict(state["results"])
    for section_key, instructions in state["pending_regenerate"].items():
        packet = _packets_cache[section_key]
        correction = f"the human reviewer asked for this specific change: {instructions}"
        text = generate_section(section_key, packet, correction=correction)
        check = verify_section(text, packet)
        clean = not check["not_found_numbers"] and not check["not_found_dates"]

        # used to build this dict wth diff keys then wht generate_verified_section
        # produces (no passed_on_first_try at all), wich meant run_review.py's
        # print_verification_status silently skipped regenerated sections, no
        # warning even if the regenerate itself introduced a new hallucination.
        # matchin the same shape here so the reviewer actually sees the status
        # after a manual regenerate too, not jst on the first automatic pass
        results[section_key] = {
            "section": section_key,
            "text": text,
            "passed_on_first_try": clean,
            "final_verified": clean,
            "flagged_on_attempt_1": None if clean else check,
        }
    return {"results": results, "pending_regenerate": {}}


def route_after_review(state):
    return "apply_regenerations" if state["pending_regenerate"] else "finalize_report"


def finalize_report(state):
    lines = []
    for section_key, result in state["results"].items():
        lines.append(f"## {section_key}\n")
        # used to check "if section_key == 'case_index_listing'" here too,
        # same problem as the one in generate_report, swapped it fr checkin
        # wht SHAPE the text actually is insted of wht its called. a list
        # of records means its raw table data (only case_index_listing
        # produces this rn, but nothin here assumes tht by name anymore),
        # anythin else is jst plain text, dump it as is
        if isinstance(result["text"], list):
            table = pd.DataFrame(result["text"])
            lines.append(table.to_markdown(index=False))
        else:
            lines.append(result["text"])
        lines.append("")
    final_text = "\n".join(lines)

    out_path = Path(__file__).parent.parent / "report_output.md"
    out_path.write_text(final_text, encoding="utf-8")

    return {"report_path": str(out_path)}


builder = StateGraph(ReviewState)
builder.add_node("generate_report", generate_report)
builder.add_node("human_review", human_review)
builder.add_node("apply_regenerations", apply_regenerations)
builder.add_node("finalize_report", finalize_report)

builder.set_entry_point("generate_report")
builder.add_edge("generate_report", "human_review")
builder.add_conditional_edges("human_review", route_after_review, {
    "apply_regenerations": "apply_regenerations",
    "finalize_report": "finalize_report",
})
builder.add_edge("apply_regenerations", "human_review")
builder.add_edge("finalize_report", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)