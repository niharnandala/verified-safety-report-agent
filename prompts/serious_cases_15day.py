INSTRUCTION = """
## TASK
Write the Serious Cases / 15-Day Alerts section.

## PACKET FIELDS
<packet>
alert_cases, non_alert_cases, alert_pct: counts/% meeting 15-day alert criteria
alert_reactions: most common reactions among alert cases specifically
alert_outcomes: most common outcomes among alert cases specifically
</packet>

## FOCUS
State the alert case count n percentage, then the most common reactions n
outcomes within tht alert group specifically (not the whole dataset). End
wth one fixed line: "Expectedness (labelled/unlabelled status) could not be
assessed, as no product label was supplied for this exercise."
"""