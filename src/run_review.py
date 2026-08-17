import uuid
import pandas as pd
from langgraph.types import Command
from review_graph import graph, _packets_cache


def print_verification_status(section_key, result):
    # skip sections tht never went thru verification (fixed template n raw table dont have this key at all)
    passed_first = result.get("passed_on_first_try")
    if passed_first is None:
        return

    if passed_first:
        print("verification: clean on first try")
        return

    # got flagged on attempt 1, show wht exactly so i can go check it myself
    flagged = result.get("flagged_on_attempt_1") or {}
    print("verification: flagged on attempt 1, needed a retry")
    if flagged.get("not_found_numbers"):
        print(f"  numbers not matched: {flagged['not_found_numbers']}")
    if flagged.get("not_found_dates"):
        print(f"  dates not matched: {flagged['not_found_dates']}")

    if result.get("final_verified"):
        # clean retry doesnt mean it fixed it right, coud jst be deleted insted
        print("  retry looks clean, but double check, might've jst deleted it insted of fixin it")
    else:
        print(f"  still flagged after retry: {result.get('flagged_on_attempt_1')}")


def ask_decision_for_section(section_key, result):
    print(f"\n=== {section_key} ===\n")

    if section_key == "case_index_listing":
        table = pd.DataFrame(result["text"])
        print(table.head())
        return {"action": "approve"}

    packet = _packets_cache.get(section_key)
    print("---- source data (what the model was given) ----")
    print(packet)
    print("---- generated text ----")
    print(result["text"])

    # show verification every time now, not jst when it still fails after retry
    print_verification_status(section_key, result)

    while True:
        choice = input("\napprove (a) / edit (e) / regenerate (r)? ").strip().lower()
        if choice == "a":
            return {"action": "approve"}
        elif choice == "e":
            new_text = input("paste the corrected text:\n")
            return {"action": "edit", "edited_text": new_text}
        elif choice == "r":
            note = input("wht shd change? ")
            return {"action": "regenerate", "instructions": note}
        print("type a, e, or r")


config = {"configurable": {"thread_id": str(uuid.uuid4())}}

state = graph.invoke({}, config)

while "__interrupt__" in state:
    payload = state["__interrupt__"][0].value
    decisions = {
        section_key: ask_decision_for_section(section_key, result)
        for section_key, result in payload.items()
    }
    state = graph.invoke(Command(resume=decisions), config)

print(f"\nreview complete. final report saved to {state['report_path']}")