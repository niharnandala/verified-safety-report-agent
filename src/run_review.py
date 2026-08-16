import uuid
import pandas as pd
from langgraph.types import Command
from review_graph import graph, _packets_cache


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

    if not result.get("final_verified", True):
        print(f"\n⚠ heads up, this section needed a correction n still has flagged items: {result.get('flagged_on_attempt_1')}")

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