import pandas as pd
from analysis import case_volume, demographics, reaction_counts, outcome_counts, top_reactions, trend_analysis

def reporting_period(df):
    return {
        "start_date":df["receive_date"].min(),
        "end_date":df["receive_date"].max()
    }

def narrative_summary(cases,demograph,reaction,outcomes,trend):
    return {
        "case_volume":cases,

    }


def build_all_packets(df):
    # calling each core analysis fn jst once here, then passing the
    # results into wichever section fns actually need them
    cases = case_volume(df)
    demograph = demographics(df)
    reaction = reaction_counts(df)
    outcomes = outcome_counts(df)
    trend = trend_analysis(df)

    return {
        "reporting_period": reporting_period(df),
        "narrative_summary": narrative_summary(cases, demograph, reaction, outcomes, trend),
        "summary_analysis_of_cases": summary_analysis_of_cases(cases, demograph, outcomes),
        "reaction_ae_analysis": reaction_ae_analysis(reaction, cases),
        "serious_cases_15day": serious_cases_15day(cases, reaction, outcomes),
        "trends_observations": trend,
        "history_of_actions": history_of_actions(),
        "case_index_listing": case_index_listing(df)
    }