import pandas as pd
def case_volume(df):
    # df is already cleaned n deduped before this fn even runs,
    # so no need to redo the version filtering here, jst trust it
    total_cases = df["safetyreportid"].nunique()

    # serious col actually holds text "serious"/"not serious", not 1/0
    serious_cases = (df["serious"] == "serious").sum()
    non_serious_cases = (df["serious"] == "not serious").sum()

    # these two shd always add up to total_cases, gud sanity check
    serious_pct = round((serious_cases / total_cases) * 100, 1)

    return {
        "total_cases": total_cases,
        "serious_cases": serious_cases,
        "non_serious_cases": non_serious_cases,
        "serious_pct": serious_pct
    }


def demographics(df):
            
        sex = df["patient_patientsex"].fillna("unknown")
        country = df["occurcountry"].fillna("unknown")

        total_cases_by_age_group = df.groupby("age_group")["safetyreportid"].nunique()
        total_cases_by_sex = df.groupby(sex)["safetyreportid"].nunique()
        total_cases_by_country=df.groupby(country)["safetyreportid"].nunique()

        return {
            "total_cases_by_age_group":total_cases_by_age_group,
            "total_cases_by_sex":total_cases_by_sex,
            "total_cases_by_country":total_cases_by_country
        }



def reaction_counts(df):
      # reaction col has multiple reactions jammed into one string, sep by commas
      # so first split each cell into a list of reactions
      reactions=df["patient_reaction_reactionmeddrapt"].fillna("unknown").str.split(",")

      # strip extra spaces around each one, otherwise "fever" and " fever" count as 2 diff things
      reactions=reactions.apply(lambda lst:[r.strip() for r in lst])

      # if same case listed the same reaction twice, only count it once for tht case
      reactions=reactions.apply(lambda lst:list(set(lst)))

      # now explode so each reaction gets its own row, still tied back to its case
      exploded=df.assign(reaction=reactions).explode("reaction")

      # plain count across everyone, this is the most common reactions answer
      all_reaction_counts=exploded["reaction"].value_counts()

      # explode already happened above, jst filter down to serious cases n count again
      serious_only=exploded[exploded["serious"]=="serious"]
      serious_reaction_counts=serious_only["reaction"].value_counts()


      return {
            "all_reaction_counts":all_reaction_counts,
            "serious_reaction_counts":serious_reaction_counts
      }

def top_reactions(counts,total_cases,min_pct=1,max_n=15):
      # min_pct means only keep reactions tht show up in atleast tht % of total cases
      # so this isnt some random top N, its tied to actual case volume
      min_count=(min_pct/100)*total_cases

      # keep only reactions tht clear the threshold
      filtered = counts[counts >=min_count]

      # still cap it so the list never blows up even if alot pass the threshold
      filtered=filtered.head(max_n)
      return filtered


def outcome_counts(df):
      # outcome col also has multiple values jammed into one string, sep by commas
      # same shape problem as the reaction col, so same fix
      outcomes=df["patient_reaction_reactionoutcome"].fillna("unknown").str.split(",")

      # strip extra spaces around each one
      outcomes=outcomes.apply(lambda lst:[o.strip() for o in lst])

      # if same case listed the same outcome twice, only count it once for tht case
      outcomes=outcomes.apply(lambda lst:list(set(lst)))

      # now explode so each outcome gets its own row, still tied back to its case
      # not tied to a specific reaction tho, we checked n tht link isnt reliable for 6 rows
      exploded=df.assign(outcome=outcomes).explode("outcome")

      # plain count across everyone
      all_outcome_counts=exploded["outcome"].value_counts()

      # same explode already happened above, jst filter down to serious cases n count again
      serious_only=exploded[exploded["serious"]=="serious"]
      serious_outcome_counts=serious_only["outcome"].value_counts()


      return {
            "all_outcome_counts":all_outcome_counts,
            "serious_outcome_counts":serious_outcome_counts
      }


def robust_hikes(counts):
    # median instead of average, jst sorts the numbers n takes the middle one
    # one freak week cant drag this around the way it drags an average
    median = counts.median()

    # for each week, how far off is it from the median
    # then take the median of those distances, tht gives a "typical wobble"
    # tht also cant get dragged by one extreme week
    abs_devs = (counts - median).abs()
    mad = abs_devs.median()

    # raw mad tends to run smaller than normal std dev on typical data
    # this scaling number jst adjusts it so the threshold behaves similarly
    # to wht we'd expect from a std dev based band, ppl commonly use this exact number
    scaled_mad = mad * 1.4826

    upper_limit = median + 2 * scaled_mad
    lower_limit = median - 2 * scaled_mad

    hikes = counts[counts > upper_limit]
    dips = counts[counts < lower_limit]

    return {
        "median": median,
        "mad": scaled_mad,
        "upper_limit": upper_limit,
        "lower_limit": lower_limit,
        "hikes": hikes,
        "dips": dips
    }




def trim_partial_edges(counts, df, date_col, freq_days):
    # first n last bucket can be partial, meaning they dont cover a full period
    # tht makes them look lower than they really are, not a real dip
    # so jst drop them before we calc mean/sd, dont let them skew things
    counts = counts.copy()

    min_date = df[date_col].min()
    max_date = df[date_col].max()

    first_label = counts.index[0]
    last_label = counts.index[-1]

    first_bucket_days = (first_label - min_date).days + 1
    last_bucket_start = last_label - pd.Timedelta(days=freq_days - 1)
    last_bucket_days = (max_date - last_bucket_start).days + 1

    if first_bucket_days < freq_days:
        counts = counts.drop(first_label)

    if last_bucket_days < freq_days:
        counts = counts.drop(last_label)

    return counts


def trend_analysis(df, date_col="receivedate", sparse_threshold=5):
    # this is the main fn, works on any file, no hardcoded numbers frm today
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], format="%Y%m%d")

    # one row per case so we dont double count cases with multiple reactions
    one_row_per_case = df.drop_duplicates(subset="safetyreportid")

    # always try weekly first, gives us the finer resolution we actually want
    weekly_counts = one_row_per_case.groupby(
        pd.Grouper(key=date_col, freq="W")
    )["safetyreportid"].nunique()

    weekly_trimmed = trim_partial_edges(weekly_counts, one_row_per_case, date_col, 7)

    # gaurdline, if weekly avg is too low, weekly buckets r too sparse to trust
    # a file wo way fewer total cases could show 1 or 2 a week, tht'll look
    # like fake spikes tht arent real, so fall bck to monthly instead
    if weekly_trimmed.median() < sparse_threshold:
        monthly_counts = one_row_per_case.groupby(
            pd.Grouper(key=date_col, freq="M")
        )["safetyreportid"].nunique()

        monthly_trimmed = trim_partial_edges(monthly_counts, one_row_per_case, date_col, 28)

        result = robust_hikes(monthly_trimmed)
        result["granularity"] = "monthly"
        result["counts"] = monthly_trimmed
        return result

    result = robust_hikes(weekly_trimmed)
    result["granularity"] = "weekly"
    result["counts"] = weekly_trimmed
    return result