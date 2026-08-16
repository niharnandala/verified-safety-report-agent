import pandas as pd
from config import (
    CASE_ID_COL, SERIOUS_COL, ALERT_COL, REACTION_COL, OUTCOME_COL,
    SEX_COL, COUNTRY_COL, AGE_GROUP_COL, DATE_COL,
    DEATH_COL, LIFE_THREATENING_COL, HOSPITALIZATION_COL,
    DISABLING_COL, CONGENITAL_ANOMALY_COL, OTHER_SERIOUS_COL,
    REPORTER_QUALIFICATION_COL,
)


def case_volume(df):
    # frst thing i checked here, serious isnt 0/1 like i assumed, its actual
    # text "serious"/"not serious", printed it before writing this so i didnt
    # build the whole fn on a wrong guess
    total_cases = df[CASE_ID_COL].nunique()
    serious_cases = df[df[SERIOUS_COL] == "serious"][CASE_ID_COL].nunique()
    non_serious_cases = total_cases - serious_cases

    # alert n serious happen to match in this dataset (1023/1 in the crosstab
    # i ran) but tht overlap is jst a coincidence of this one dataset, not
    # guaranteed on a diff one, so pulling alert straight off
    # fulfillexpeditecriteria, not reusing serious's numbers as a shortcut
    alert_cases = df[df[ALERT_COL] == "yes"][CASE_ID_COL].nunique()
    non_alert_cases = total_cases - alert_cases
    alert_pct = round((alert_cases / total_cases) * 100, 2)

    return {
        "total_cases": total_cases,
        "serious_cases": serious_cases,
        "non_serious_cases": non_serious_cases,
        "alert_cases": alert_cases,
        "non_alert_cases": non_alert_cases,
        "alert_pct": alert_pct,
    }


def demographics(df):
    # sex n country had missing values, filling em as "unknown" rather then
    # dropping the rows, still wanna count tht case somewhere
    df = df.copy()
    df[SEX_COL] = df[SEX_COL].fillna("unknown")
    df[COUNTRY_COL] = df[COUNTRY_COL].fillna("unknown")

    # occurcountry had a mix of full names n bare codes like "SA" which i
    # almost mapped to south africa by habit, its actually saudi arabia
    # officially. left the raw codes as is n documented it as a known
    # limitation instead of guessing my way past it
    total_cases_by_sex = df.groupby(SEX_COL)[CASE_ID_COL].nunique()
    total_cases_by_country = df.groupby(COUNTRY_COL)[CASE_ID_COL].nunique()
    total_cases_by_age_group = df.groupby(AGE_GROUP_COL)[CASE_ID_COL].nunique()

    return {
        "total_cases_by_sex": total_cases_by_sex,
        "total_cases_by_country": total_cases_by_country,
        "total_cases_by_age_group": total_cases_by_age_group,
    }


def _explode_col(df, col):
    # pulling this bit out since reaction n outcome both need the exact
    # same split/strip/dedupe/explode pattern, no point writing it twice
    temp = df[[CASE_ID_COL, col]].copy()
    temp[col] = temp[col].fillna("").apply(
        lambda x: sorted(set(part.strip() for part in x.split(",") if part.strip()))
    )
    return temp.explode(col)


def reaction_counts(df):
    # went back n forth on case wise vs reaction wise counting here. case
    # wise felt simpler but throws away real info when a case has multiple
    # reactions, n it didnt match how the challenge counted things either,
    # so went reaction wise, one case wth 3 reactions adds to all 3
    exploded = _explode_col(df, REACTION_COL)
    exploded = exploded[exploded[REACTION_COL] != ""]

    all_reaction_counts = exploded[REACTION_COL].value_counts()

    serious_ids = df[df[SERIOUS_COL] == "serious"][CASE_ID_COL]
    serious_reaction_counts = exploded[
        exploded[CASE_ID_COL].isin(serious_ids)
    ][REACTION_COL].value_counts()

    alert_ids = df[df[ALERT_COL] == "yes"][CASE_ID_COL]
    alert_reaction_counts = exploded[
        exploded[CASE_ID_COL].isin(alert_ids)
    ][REACTION_COL].value_counts()

    # merging age group n sex back in off the original df so i can group
    # reactions by them wtout exploding the whole thing again from scratch
    merged = exploded.merge(
        df[[CASE_ID_COL, AGE_GROUP_COL, SEX_COL]].drop_duplicates(CASE_ID_COL),
        on=CASE_ID_COL, how="left"
    )
    reaction_counts_by_age_group = merged.groupby(AGE_GROUP_COL)[REACTION_COL].value_counts()
    reaction_counts_by_sex = merged.groupby(SEX_COL)[REACTION_COL].value_counts()

    return {
        "all_reaction_counts": all_reaction_counts,
        "serious_reaction_counts": serious_reaction_counts,
        "alert_reaction_counts": alert_reaction_counts,
        "reaction_counts_by_age_group": reaction_counts_by_age_group,
        "reaction_counts_by_sex": reaction_counts_by_sex,
    }


def top_reactions(counts, total_cases, min_pct=1, max_n=15):
    # coulda jst done top 10 n called it a day but tht felt arbitrary, so
    # tied the cutoff to actual case volume instead, plus a cap so it
    # never blows up on a bigger dataset either
    threshold = total_cases * (min_pct / 100)
    filtered = counts[counts >= threshold]
    return filtered.head(max_n)


def outcome_counts(df):
    # frst thought was to pair reaction[i] wth outcome[i] by position since
    # both r comma sep the same way. wrote a check script comparing list
    # lengths per row tho n found 6 out of 1068 rows where they dont even
    # match up. so didnt trust the pairing, counting outcomes independent
    # instead, not tied to a specific reaction
    exploded = _explode_col(df, OUTCOME_COL)
    exploded = exploded[exploded[OUTCOME_COL] != ""]

    all_outcome_counts = exploded[OUTCOME_COL].value_counts()

    serious_ids = df[df[SERIOUS_COL] == "serious"][CASE_ID_COL]
    serious_outcome_counts = exploded[
        exploded[CASE_ID_COL].isin(serious_ids)
    ][OUTCOME_COL].value_counts()

    alert_ids = df[df[ALERT_COL] == "yes"][CASE_ID_COL]
    alert_outcome_counts = exploded[
        exploded[CASE_ID_COL].isin(alert_ids)
    ][OUTCOME_COL].value_counts()

    return {
        "all_outcome_counts": all_outcome_counts,
        "serious_outcome_counts": serious_outcome_counts,
        "alert_outcome_counts": alert_outcome_counts,
    }


def seriousness_breakdown(df):
    # these 6 flags r independent yes/no, not mutually exclusive, a case
    # can be both hospitalization n disabling at once, so counting each
    # one on its own, not picking jst one per case
    return {
        "death": df[df[DEATH_COL] == "yes"][CASE_ID_COL].nunique(),
        "life_threatening": df[df[LIFE_THREATENING_COL] == "yes"][CASE_ID_COL].nunique(),
        "hospitalization": df[df[HOSPITALIZATION_COL] == "yes"][CASE_ID_COL].nunique(),
        "disabling": df[df[DISABLING_COL] == "yes"][CASE_ID_COL].nunique(),
        "congenital_anomaly": df[df[CONGENITAL_ANOMALY_COL] == "yes"][CASE_ID_COL].nunique(),
        "other": df[df[OTHER_SERIOUS_COL] == "yes"][CASE_ID_COL].nunique(),
    }


def reporter_type(df):
    # jst a straight groupby, nothing fancy needed here
    return df.groupby(REPORTER_QUALIFICATION_COL)[CASE_ID_COL].nunique()


def trim_partial_edges(counts, df, date_col, freq_days):
    # frst n last bucket usually dont cover a full period, like if data
    # starts mid week tht frst week isnt a real full week, itd unfairly
    # look low n mess with the median. dropping incomplete edges before
    # any stats get computed on this
    if len(counts) < 3:
        return counts

    min_date = df[date_col].min()
    max_date = df[date_col].max()

    trimmed = counts.copy()
    if trimmed.index[0] < min_date:
        trimmed = trimmed.iloc[1:]
    if trimmed.index[-1] + pd.Timedelta(days=freq_days) > max_date + pd.Timedelta(days=1):
        trimmed = trimmed.iloc[:-1]

    return trimmed


def robust_hikes(counts):
    # tried mean +/- 2 std frst since tht felt like the obvious textbook
    # move, tested it on a tiny made up example (10,12,11,13,50) before
    # trusting it on real data n it failed, the one outlier dragged both
    # the mean n the std up so much it hid itself. median n mad cant get
    # bullied by one extreme value the same way so switched to tht
    median = counts.median()
    mad = (counts - median).abs().median()
    scaled_mad = mad * 1.4826  # derived frm the normal curve, not jst copied it
    # Φ⁻¹(0.75)≈0.6745 → flip it → 1/0.6745 ≈ 1.4826

    upper_limit = median + (2 * scaled_mad)
    lower_limit = median - (2 * scaled_mad)
    # 2x specifically cuz 2Φ(2)-1≈0.9545, ~95% of a normal curve sits
    # within 2 std devs, past tht is the rare tail worth flagging

    hikes = counts[counts > upper_limit]
    dips = counts[counts < lower_limit]

    return {
        "median": median,
        "mad": round(scaled_mad, 2),
        "upper_limit": round(upper_limit, 2),
        "lower_limit": round(lower_limit, 2),
        "hikes": hikes,
        "dips": dips,
    }


def trend_analysis(df, date_col=DATE_COL, sparse_threshold=5):
    cases_df = df.drop_duplicates(CASE_ID_COL)[[CASE_ID_COL, date_col]].copy()
    cases_df[date_col] = pd.to_datetime(cases_df[date_col])

    print("rows going into weekly grouping:", len(cases_df))          # ← add
    print("date range:", cases_df[date_col].min(), "to", cases_df[date_col].max())  # ← add

    weekly_counts = cases_df.groupby(
        pd.Grouper(key=date_col, freq="W")
    )[CASE_ID_COL].nunique()


    weekly_trimmed = trim_partial_edges(weekly_counts, cases_df, date_col, freq_days=7)

    # checking median here not mean, caught this after i'd already fixed
    # the main hike detection, same masking problem shows up one level up
    # too, one freak week can inflate an average n hide genuinely thin
    # data frm ever getting caught
    if weekly_trimmed.median() < sparse_threshold:
        monthly_counts = cases_df.groupby(
            pd.Grouper(key=date_col, freq="ME")
        )[CASE_ID_COL].nunique()
        monthly_trimmed = trim_partial_edges(monthly_counts, cases_df, date_col, freq_days=30)
        return robust_hikes(monthly_trimmed)

    return robust_hikes(weekly_trimmed)

