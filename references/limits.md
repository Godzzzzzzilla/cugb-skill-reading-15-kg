# Limits

| condition | behaviour |
|---|---|
| entity mentioned once, never defined | not a node |
| acronym never defined anywhere | only matched if it repeats as a capitalised term |
| relation spanning two sentences | not joined; each sentence stands alone |
| same acronym for two different things | merged under the first definition; check `definitions[]` |
| CJK-only entities | not detected without an acronym or repetition |
