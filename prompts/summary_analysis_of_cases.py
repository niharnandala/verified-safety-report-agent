INSTRUCTION = """
## TASK
Write the Summary Analysis of Cases section.

## PACKET FIELDS
<packet>
case_volume: total/serious/alert counts and percentages
demographics: total_cases_by_age_group, total_cases_by_sex, total_cases_by_country
outcome_counts: all_outcome_counts, serious_outcome_counts, alert_outcome_counts
seriousness_breakdown: death, life_threatening, hospitalization, disabling,
    congenital_anomaly, other counts (these overlap, one case can meet several)
reporter_type: case counts by wo reported (physician/pharmacist/consumer/etc)
</packet>

## FOCUS
Report case volume, the age/sex/country distribution, wich specific
seriousness criteria occurred n how often (note these are not mutually
exclusive), the outcome distribution, n the reporter type breakdown.
Numbers stated plainly, no narrative framing beyond linking them into
sentences.
"""