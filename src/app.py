import uuid
import streamlit as st
from langgraph.types import Command
from review_graph import graph

st.title("PADER Report — Human Review")

if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    st.session_state.state = graph.invoke({}, st.session_state.config)
    st.session_state.decisions = {}

state = st.session_state.state

if "__interrupt__" in state:
    payload = state["__interrupt__"][0].value
    st.write("Review each section below, then submit all decisions at once.")

    for section_key, result in payload.items():
        st.subheader(section_key)

        if section_key == "case_index_listing":
            st.dataframe(result["text"].head())
            st.session_state.decisions[section_key] = {"action": "approve"}
            continue

        if not result.get("final_verified", True):
            st.warning(f"needed a correction earlier, flagged: {result.get('flagged_on_attempt_1')}")

        action = st.radio(
            "decision", ["approve", "edit", "regenerate"],
            key=f"action_{section_key}", horizontal=True,
        )

        if action == "approve":
            st.text_area("text", result["text"], disabled=True, key=f"view_{section_key}")
            st.session_state.decisions[section_key] = {"action": "approve"}

        elif action == "edit":
            edited = st.text_area("edit directly", result["text"], key=f"edit_{section_key}")
            st.session_state.decisions[section_key] = {"action": "edit", "edited_text": edited}

        elif action == "regenerate":
            st.text_area("current text", result["text"], disabled=True, key=f"cur_{section_key}")
            note = st.text_input("wht shd change?", key=f"note_{section_key}")
            st.session_state.decisions[section_key] = {"action": "regenerate", "instructions": note}

        st.divider()

    if st.button("Submit all decisions"):
        st.session_state.state = graph.invoke(
            Command(resume=st.session_state.decisions), st.session_state.config
        )
        st.session_state.decisions = {}
        st.rerun()

else:
    st.success("Report finalized")
    with open(state["report_path"]) as f:
        st.markdown(f.read())