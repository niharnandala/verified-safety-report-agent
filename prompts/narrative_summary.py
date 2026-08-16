INSTRUCTION = """
## TASK
Write the Narrative Summary and Analysis section.

## PACKET FIELDS
<packet>
case_volume: total/serious/alert counts and percentages
top_age_group, top_sex, top_country: most represented category in each
top_reaction, top_serious_reaction: most common reaction overall / among serious cases
top_outcome: most common outcome overall
trend_hikes: any week/month flagged as an unusual spike (may be empty)
</packet>

## FOCUS
Cover, in this order: total case volume + serious/alert split, the most
represented age group/sex/country, the most common reaction overall AND
among serious cases specifically, the most common outcome, then any
trend_hikes finding stated with its exact period and count. If trend_hikes
is empty, state tht no unusual spike was identified.

## EXAMPLE SHAPE (not real numbers, jst the pattern to follow)
"During the reporting period, [N] cases were received, of which [N] ([%])
were serious and [N] ([%]) met 15-day alert criteria. Cases were most
concentrated in the [age group] age group, among [sex] patients, and in
[country]. [Reaction] was the most frequently reported reaction overall
and among serious cases. The most common outcome was [outcome]. Case
volume rose to [N] during the week of [date], above the normal range."
"""