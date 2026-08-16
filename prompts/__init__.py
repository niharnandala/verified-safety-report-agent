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