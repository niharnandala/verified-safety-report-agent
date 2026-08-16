import pandas as pd
from analysis import (
    case_volume, demographics, reaction_counts, outcome_counts,
    top_reactions, trend_analysis, seriousness_breakdown, reporter_type
)
from config import (
    CASE_ID_COL, SERIOUS_COL, ALERT_COL, REACTION_COL,
    OUTCOME_COL, SEX_COL, COUNTRY_COL, AGE_GROUP_COL, DATE_COL
)


def reporting_period(df):
    # jst needs the date range, straight off the raw df, nothing else
    return {
        "start_date": df[DATE_COL].min(),
        "end_date": df[DATE_COL].max()
    }


def narrative_summary(cases, demograph, reaction, outcomes, trend):
    # condensed headline numbers pulled frm every other section, not raw
    # access to everything, jst the top level facts on purpose
    return {
        "case_volume": cases,
        "top_age_group": demograph["total_cases_by_age_group"].idxmax(),
        "top_sex": demograph["total_cases_by_sex"].idxmax(),
        "top_country": demograph["total_cases_by_country"].idxmax(),
        "top_reaction": reaction["all_reaction_counts"].idxmax(),
        "top_serious_reaction": reaction["serious_reaction_counts"].idxmax(),
        "top_outcome": outcomes["all_outcome_counts"].idxmax(),
        "trend_hikes": trend["hikes"].to_dict()
    }


def summary_analysis_of_cases(cases, demograph, outcomes, seriousness, reporter):
    # case volume, demographics, outcomes, seriousness sub flags, n reporter type,
    # everything section 3 actually asks for
    return {
        "case_volume": cases,
        "demographics": demograph,
        "outcome_counts": outcomes,
        "seriousness_breakdown": seriousness,
        "reporter_type": reporter
    }


def reaction_ae_analysis(reaction, cases):
    # only reaction data, nothing bout demographics or outcomes here
    return {
        "top_reactions_all": top_reactions(reaction["all_reaction_counts"], cases["total_cases"]),
        "top_reactions_serious": top_reactions(reaction["serious_reaction_counts"], cases["total_cases"]),
        "reaction_counts_by_age_group": reaction["reaction_counts_by_age_group"],
        "reaction_counts_by_sex": reaction["reaction_counts_by_sex"]
    }


def serious_cases_15day(cases, reaction, outcomes):
    # alert cases specifically, counted straight off fulfillexpeditecriteria
    # inside case_volume, not borrowed frm serious
    return {
        "alert_cases": cases["alert_cases"],
        "non_alert_cases": cases["non_alert_cases"],
        "alert_pct": cases["alert_pct"],
        "alert_reactions": reaction["alert_reaction_counts"],
        "alert_outcomes": outcomes["alert_outcome_counts"]
    }


def history_of_actions():
    # no data given for this at all, dont invent anything,
    # this fn never touches the dataframe
    return {
        "actions": None,
        "note": "no history of actions data was supplied for this exercise"
    }


def case_index_listing(df):
    # raw case listing, no analysis fn involved, straight columns
    # pulled n renamed frm the cleaned df
    return df[[
        CASE_ID_COL, REACTION_COL, SERIOUS_COL, DATE_COL, COUNTRY_COL, OUTCOME_COL
    ]].rename(columns={
        CASE_ID_COL: "case_id",
        REACTION_COL: "reaction",
        SERIOUS_COL: "seriousness",
        DATE_COL: "reporting_date",
        COUNTRY_COL: "country",
        OUTCOME_COL: "outcome"
    })


def build_all_packets(df):
    # calling each core analysis fn jst once here, then passing the
    # results into wichever section fns actually need them
    cases = case_volume(df)
    demograph = demographics(df)
    reaction = reaction_counts(df)
    outcomes = outcome_counts(df)
    trend = trend_analysis(df)
    seriousness = seriousness_breakdown(df)
    reporter = reporter_type(df)

    return {
        "reporting_period": reporting_period(df),
        "narrative_summary": narrative_summary(cases, demograph, reaction, outcomes, trend),
        "summary_analysis_of_cases": summary_analysis_of_cases(cases, demograph, outcomes, seriousness, reporter),
        "reaction_ae_analysis": reaction_ae_analysis(reaction, cases),
        "serious_cases_15day": serious_cases_15day(cases, reaction, outcomes),
        "trends_observations": trend,
        "history_of_actions": history_of_actions(),
        "case_index_listing": case_index_listing(df)
    }