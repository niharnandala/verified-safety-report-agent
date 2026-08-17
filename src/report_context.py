import pandas as pd
from analysis import (
    case_volume, demographics, reaction_counts, outcome_counts,
    top_reactions, trend_analysis, seriousness_breakdown, reporter_type
)
from config import (
    CASE_ID_COL, SERIOUS_COL, REACTION_COL,
    OUTCOME_COL, COUNTRY_COL, DATE_COL
)


def reporting_period(df, **analysis):
    return {
        "start_date": df[DATE_COL].min().strftime("%Y-%m-%d"),
        "end_date": df[DATE_COL].max().strftime("%Y-%m-%d")
    }


def narrative_summary(df, **analysis):
    # used to jst be positional args (cases, demograph, reaction, outcomes, trend),
    # switched to pulling em out of the analysis dict by name so the names
    # here actually match wht i typed in SECTION_REGISTRY's "needs" list below,
    # no more guessing wich positional slot is wich
    cases = analysis["case_volume"]
    demograph = analysis["demographics"]
    reaction = analysis["reaction_counts"]
    outcomes = analysis["outcome_counts"]
    trend = analysis["trend_analysis"]

    return {
        "case_volume": cases,
        "top_age_group": demograph["total_cases_by_age_group"].idxmax(),
        "top_sex": demograph["total_cases_by_sex"].idxmax(),
        "top_country": demograph["total_cases_by_country"].idxmax(),
        "top_reaction": reaction["all_reaction_counts"].idxmax(),
        "top_serious_reaction": reaction["serious_reaction_counts"].idxmax(),
        "top_outcome": outcomes["all_outcome_counts"].idxmax(),
        "trend_hikes": {k.strftime("%Y-%m-%d"): v for k, v in trend["hikes"].to_dict().items()}
    }


def summary_analysis_of_cases(df, **analysis):
    cases = analysis["case_volume"]
    demograph = analysis["demographics"]
    outcomes = analysis["outcome_counts"]
    seriousness = analysis["seriousness_breakdown"]
    reporter = analysis["reporter_type"]

    return {
        "case_volume": cases,
        "demographics": demograph,
        "outcome_counts": outcomes,
        "seriousness_breakdown": seriousness,
        "reporter_type": reporter
    }


def reaction_ae_analysis(df, **analysis):
    reaction = analysis["reaction_counts"]
    cases = analysis["case_volume"]

    return {
        "top_reactions_all": top_reactions(reaction["all_reaction_counts"], cases["total_cases"]),
        "top_reactions_serious": top_reactions(reaction["serious_reaction_counts"], cases["total_cases"]),
        "reaction_counts_by_age_group": reaction["reaction_counts_by_age_group"],
        "reaction_counts_by_sex": reaction["reaction_counts_by_sex"]
    }


def serious_cases_15day(df, **analysis):
    cases = analysis["case_volume"]
    reaction = analysis["reaction_counts"]
    outcomes = analysis["outcome_counts"]

    return {
        "alert_cases": cases["alert_cases"],
        "non_alert_cases": cases["non_alert_cases"],
        "alert_pct": cases["alert_pct"],
        "alert_reactions": reaction["alert_reaction_counts"],
        "alert_outcomes": outcomes["alert_outcome_counts"]
    }


def history_of_actions():
    # no data given for this at all, dont invent anything,
    # this fn never touches the dataframe, left it wtout df/**analysis
    # on purpose since it genuinely doesnt need either, the registry
    # below wraps it in a lil lambda so it still fits the same calling shape
    return {
        "actions": None,
        "note": "no history of actions data was supplied for this exercise"
    }


def case_index_listing(df, **analysis):
    # raw case listing, no analysis fn involved, straight columns
    # pulled n renamed frm the cleaned df. **analysis jst sits here unused,
    # this section declares 0 needs so its always empty anyway
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


# this is the actual fix. used to be tht "wht does section X need" only
# lived implicitly, buried in wich variable got passed into wich fn call
# inside build_all_packets. now its jst data, sittin right here, u can
# read it top to bottom wtout tracing any function calls to figure out
# wht feeds wht. adding a new report type later means addin new entries
# here, not rewritin the assembly logic itself
SECTION_REGISTRY = {
    "reporting_period": {
        "needs": [],
        "build": reporting_period,
    },
    "narrative_summary": {
        "needs": ["case_volume", "demographics", "reaction_counts", "outcome_counts", "trend_analysis"],
        "build": narrative_summary,
    },
    "summary_analysis_of_cases": {
        "needs": ["case_volume", "demographics", "outcome_counts", "seriousness_breakdown", "reporter_type"],
        "build": summary_analysis_of_cases,
    },
    "reaction_ae_analysis": {
        "needs": ["reaction_counts", "case_volume"],
        "build": reaction_ae_analysis,
    },
    "serious_cases_15day": {
        "needs": ["case_volume", "reaction_counts", "outcome_counts"],
        "build": serious_cases_15day,
    },
    "trends_observations": {
        # no dedicated build fn fr this one, trend_analysis's own output
        # IS the packet as is, jst pass it thru
        "needs": ["trend_analysis"],
        "build": lambda df, **analysis: analysis["trend_analysis"],
    },
    "history_of_actions": {
        # needs nothing, but history_of_actions() also doesnt accept
        # (df, **analysis) like everything else does, so wrapped it
        # in a tiny lambda jst to keep the calling convention identical
        # fr every single section, no special casing needed at the call site
        "needs": [],
        "build": lambda df, **analysis: history_of_actions(),
    },
    "case_index_listing": {
        "needs": [],
        "build": case_index_listing,
    },
}


def build_all_packets(df):
    # compute every analysis once, up front, regardless of wich sections
    # actually end up using it. this dict is the single source of truth
    # every section pulls its "needs" out of
    all_analysis = {
        "case_volume": case_volume(df),
        "demographics": demographics(df),
        "reaction_counts": reaction_counts(df),
        "outcome_counts": outcome_counts(df),
        "trend_analysis": trend_analysis(df),
        "seriousness_breakdown": seriousness_breakdown(df),
        "reporter_type": reporter_type(df),
    }

    packets = {}
    for section_key, spec in SECTION_REGISTRY.items():
        # only hand this section the specific pieces it declared it needs
        # in "needs", not the whole all_analysis dict, tht defeats the
        # entire point of declaring needs in the first place
        needed = {name: all_analysis[name] for name in spec["needs"]}
        packets[section_key] = spec["build"](df, **needed)

    return packets


"""
section                       | needs (declared, not hardcoded anymore)
------------------------------|------------------------------------------------------------
reporting_period              | (none, reads dates straight off df)

narrative_summary             | case_volume, demographics, reaction_counts,
                               | outcome_counts, trend_analysis

summary_analysis_of_cases     | case_volume, demographics, outcome_counts,
                               | seriousness_breakdown, reporter_type

reaction_ae_analysis          | reaction_counts, case_volume

serious_cases_15day           | case_volume, reaction_counts, outcome_counts

trends_observations           | trend_analysis (passed straight thru, no reshaping)

history_of_actions            | (none, fixed statement, no analysis fn called)

case_index_listing            | (none, raw table straight off df)
"""