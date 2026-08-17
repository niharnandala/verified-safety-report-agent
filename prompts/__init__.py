from .system_prompt import SYSTEM_PROMPT
from . import (
    reporting_period, narrative_summary, summary_analysis_of_cases,
    reaction_ae_analysis, serious_cases_15day, trends_observations,
    history_of_actions, case_index_listing
)

SECTION_INSTRUCTIONS = {
    "reporting_period": reporting_period.INSTRUCTION,
    "narrative_summary": narrative_summary.INSTRUCTION,
    "summary_analysis_of_cases": summary_analysis_of_cases.INSTRUCTION,
    "reaction_ae_analysis": reaction_ae_analysis.INSTRUCTION,
    "serious_cases_15day": serious_cases_15day.INSTRUCTION,
    "trends_observations": trends_observations.INSTRUCTION,
    "history_of_actions": history_of_actions.INSTRUCTION,
    "case_index_listing": case_index_listing.INSTRUCTION
}

# added this one so review_graph.py doesnt hav to hardcode section names
# ("history_of_actions", "case_index_listing") to figure out wich sections
# skip the llm n wht to show insted. not every section module actually
# defines FIXED_OUTPUT (only history_of_actions.py does rn), so usin
# getattr wth a None fallback insted of jst .FIXED_OUTPUT wich woud crash
# on the other 7
FIXED_OUTPUTS = {
    "reporting_period": getattr(reporting_period, "FIXED_OUTPUT", None),
    "narrative_summary": getattr(narrative_summary, "FIXED_OUTPUT", None),
    "summary_analysis_of_cases": getattr(summary_analysis_of_cases, "FIXED_OUTPUT", None),
    "reaction_ae_analysis": getattr(reaction_ae_analysis, "FIXED_OUTPUT", None),
    "serious_cases_15day": getattr(serious_cases_15day, "FIXED_OUTPUT", None),
    "trends_observations": getattr(trends_observations, "FIXED_OUTPUT", None),
    "history_of_actions": getattr(history_of_actions, "FIXED_OUTPUT", None),
    "case_index_listing": getattr(case_index_listing, "FIXED_OUTPUT", None),
}