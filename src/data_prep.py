import pandas as pd
def normalize_age(age, unit):
    # get age onto the same scale, years, before anything else touches it
    # if the unit is missing or tht weird "800" code, dont guess, jst unknown
    if pd.isna(age) or unit == "800":
        return None

    if unit == "year":
        return age
    elif unit == "month":
        return age / 12
    elif unit == "week":
        return age / 52
    elif unit == "day":
        return age / 365
    else:
        return None  # any other unrecognized unit, unknown too


def bucket_age(age_years):
    # takes an age tht's already in years, sorts it into a clinically
    # meaningful group, not jst flat 10yr splits
    if pd.isna(age_years):
        return "unknown"
    elif age_years < 18:
        return "under 18"
    elif age_years < 65:
        return "18-64"
    elif age_years < 75:
        return "65-74"
    else:
        return "75+"



def clean_data(df):
        max_version=df.groupby("safetyreportid")["safetyreportversion"].transform("max")
        df_latest=df[df["safetyreportversion"]==max_version].copy()
        df_latest["age_years"] = df_latest.apply(
            lambda row: normalize_age(row["patient_patientonsetage"], row["patient_patientonsetageunit"]),
            axis=1
        )
        df_latest["age_group"] = df_latest["age_years"].apply(bucket_age)
        return df_latest


