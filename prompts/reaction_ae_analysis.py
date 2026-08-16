INSTRUCTION = """
## TASK
Write the Reaction / Adverse Event Analysis section.

## PACKET FIELDS
<packet>
top_reactions_all: most frequent reactions overall, wth counts
top_reactions_serious: most frequent reactions among serious cases, wth counts
reaction_counts_by_age_group: reaction frequency broken down by age group
reaction_counts_by_sex: reaction frequency broken down by sex
</packet>

## FOCUS
List top reactions overall n among serious cases wth counts. Only mention
an age group or sex concentration if one reaction clearly dominates within
tht slice, dont force a pattern if none stands out. End wth one fixed line:
"System Organ Class level analysis was not available for this dataset."
"""