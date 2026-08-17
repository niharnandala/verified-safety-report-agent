<div align="center">

# Version 1 — section dependencies, declared as data

### GenAR AI Engineering Challenge — generalization writeup

![Status](https://img.shields.io/badge/status-implemented%20%26%20tested-brightgreen)

</div>

---

- Picked from the challenge's 7 suggested V1 directions: **section dependencies**
- Why this one: it's the actual real gap I found in my own V0, not one I picked because it
  sounds good

## Contents

- [The problem](#the-problem)
- [Before → after](#before--after)
- [What I built](#what-i-built)
- [Proof it works](#proof-it-works)
- [What's still not fixed](#whats-still-not-fixed)

---

## The problem

- `analysis.py`, `config.py`, `SECTION_INSTRUCTIONS` already didn't care what report type was
  asking, genuinely reusable already
- One place still did: `build_all_packets()`
- It "knew" `narrative_summary` needs `case_volume`, `demographics`, `reaction_counts`,
  `outcome_counts`, `trend_analysis` only because those were the exact variables typed into that
  one function call
- That knowledge lived in code structure, not anywhere you could read it without tracing
  function calls by hand

---

## Before → after

```mermaid
---
config:
  theme: base
  themeVariables:
    background: '#ffffff'
    mainBkg: '#ffffff'
    primaryColor: '#ffffff'
    primaryBorderColor: '#000000'
    primaryTextColor: '#000000'
    secondaryColor: '#ffffff'
    secondaryBorderColor: '#000000'
    secondaryTextColor: '#000000'
    tertiaryColor: '#ffffff'
    tertiaryBorderColor: '#000000'
    lineColor: '#000000'
    textColor: '#000000'
    nodeBorder: '#000000'
    clusterBkg: '#ffffff'
    clusterBorder: '#000000'
    edgeLabelBackground: '#ffffff'
    titleColor: '#000000'
---
flowchart TB
  subgraph Before["Before — hidden in code"]
    A1["case_volume(df), demographics(df), ... computed"]
    B1["narrative_summary(cases, demograph, reaction, outcomes, trend)"]
    C1["summary_analysis_of_cases(cases, demograph, outcomes, seriousness, reporter)"]
    D1["...6 more hand-written calls like this"]
    E1["8 packets"]
  end

  A1 --> B1 & C1 & D1
  B1 --> E1
  C1 --> E1
  D1 --> E1

  classDef heading font-size:24px,font-weight:bold;
  classDef node font-size:18px;
  class Before heading;
  class A1,B1,C1,D1,E1 node;

  style B1 fill:#FFD600
  style A1 fill:#FFD600
  style C1 fill:#FFD600
  style D1 fill:#FFD600
  style E1 fill:#FFD600
  style Before fill:#2962FF
```

```mermaid
---
config:
  theme: base
  themeVariables:
    background: '#ffffff'
    mainBkg: '#ffffff'
    primaryColor: '#ffffff'
    primaryBorderColor: '#000000'
    primaryTextColor: '#000000'
    secondaryColor: '#ffffff'
    secondaryBorderColor: '#000000'
    secondaryTextColor: '#000000'
    tertiaryColor: '#ffffff'
    tertiaryBorderColor: '#000000'
    lineColor: '#000000'
    textColor: '#000000'
    nodeBorder: '#000000'
    clusterBkg: '#ffffff'
    clusterBorder: '#000000'
    edgeLabelBackground: '#ffffff'
    titleColor: '#000000'
---
flowchart TB
  subgraph After["After — declared as data"]
    A2["SECTION_REGISTRY = section: needs list, build fn"]
    H2["case_volume(df), demographics(df), ... computed once"]
    G2["loop: needed = pick each name in needs from raw results"]
    I2["spec.build(df, **needed)"]
    J2["8 packets"]
  end

  A2 --> G2
  H2 --> G2
  G2 --> I2
  I2 --> J2

  style G2 fill:#FFF9C4
  style A2 fill:#FFF9C4
  style H2 fill:#FFF9C4
  style I2 fill:#FFF9C4
  style J2 fill:#FFF9C4
  style After fill:#00C853
```

- Before: reading "what does `narrative_summary` need" means opening `report_context.py` and
  reading its function call
- After: reading "what does `narrative_summary` need" means reading one line in
  `SECTION_REGISTRY`

---

## What I built

The actual code, verbatim from `report_context.py`, not a paraphrase:

```python
SECTION_REGISTRY = {
    "narrative_summary": {
        "needs": ["case_volume", "demographics", "reaction_counts", "outcome_counts", "trend_analysis"],
        "build": narrative_summary,
    },
    # ...one entry like this per section
}

def build_all_packets(df):
    all_analysis = {
        "case_volume": case_volume(df),
        "demographics": demographics(df),
        # ...every analysis computed once, up front
    }
    packets = {}
    for section_key, spec in SECTION_REGISTRY.items():
        needed = {name: all_analysis[name] for name in spec["needs"]}
        packets[section_key] = spec["build"](df, **needed)
    return packets
```

- `SECTION_REGISTRY` dict in `report_context.py`, one entry per section
- Each entry declares `"needs": [...]` (plain list of analysis names) + `"build": ...`
  (which function shapes it)
- `build_all_packets()` is now one generic loop instead of 8 hand-written lines
- Packet-builder functions do the exact same shaping logic as before, just pull inputs by name
  from a dict instead of positional args, so `needs` actually matches what's inside the function
- Bonus, same trip: `review_graph.py` used to hardcode `if section_key == "history_of_actions"`
  to decide "skip the LLM", now it checks whether that section even has an instruction, driven
  by data already in `prompts/`

---

## Proof it works

- Ran `python src/run_review.py` after the refactor, all 8 sections, same numbers as before,
  refactor didn't break anything

<details>
<summary>🐛 The bug this refactor actually caught, by testing it, not by reviewing the diff</summary>

<br>

- Tested the regenerate path for the first time ever doing this, and it caught a real bug:
  `apply_regenerations()` built results in a different shape than normal generation, so a
  regenerated section's verification status was silently never shown
- Fixed by making both paths build the same shape
- That's the actual point of testing something instead of assuming it works, a refactor that
  "obviously doesn't change behavior" still needs the untouched paths exercised, not just the
  ones you were thinking about while writing it

</details>

---

## What's still not fixed

- `review_graph.py`'s LangGraph nodes still assume one report's sections running at a time
- A second real report type running through the same graph would need a report-type identifier
  threaded through it, that part's still genuinely new work
- Cheapest thing left on the table if there's more time: versioning, stamp `report_output.md`
  with which model/dataset/prompt produced it

---

<div align="center">

Full main writeup: [`README.md`](../README.md)

</div>