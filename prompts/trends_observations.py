INSTRUCTION = """
## TASK
Write the Trends and Important Observations section.

## PACKET FIELDS
<packet>
median, mad, upper_limit, lower_limit: the normal range for this dataset's
    case volume per period
hikes: periods flagged above the normal range (may be empty)
dips: periods flagged below the normal range (may be empty)
granularity: "weekly" or "monthly", wich period size was used
</packet>

## FOCUS
For each entry in hikes, state its period n count against upper_limit, eg:
"the week of [date] recorded [count] cases, above the normal range of
[lower_limit] to [upper_limit]." Do the same for dips against lower_limit.
If hikes is empty, say so. If dips is empty, say so. Never suggest a cause
or call it a signal, jst state wht was flagged n wht the normal range was.
"""