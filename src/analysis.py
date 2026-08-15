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
