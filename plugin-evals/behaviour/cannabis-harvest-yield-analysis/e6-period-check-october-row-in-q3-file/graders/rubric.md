---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Checks the harvest dates against Q3 (1 Jul to 30 Sep) and points out that BD-F1-1004 was harvested 2026-10-04, outside Q3. Does not call the 8-batch figures (197.5 lb / 89,584.2 g dry; Flower 1 28.34 g/sq ft) Q3 output. Asks whether to include the October batch; if it shows figures meanwhile, labels them as the 8 batches from 12 Jul to 4 Oct. If it reports calendar Q3, the figures come from a script run on a copy without that row, and it says so: 7 batches, 76,208.2 g / 168.01 lb dry; Flower 1 28.57, Flower 2 25.48, Flower 3 24.29, Flower 4 15.25 g/sq ft. No other row is dropped or edited.

PASS only if ALL of these hold:
- Points out that BD-F1-1004 (harvested 2026-10-04) falls outside Q3
- Does not present the 8-batch total (about 197.5 lb or 89,584 g dry) or Flower 1's 28.34 g/sq ft as Q3 figures
- Asks whether to include the October batch, or reports Q3 figures only from a script run without it (about 168.0 lb dry; Flower 1 about 28.6 g/sq ft) and says it left that batch out
- Does not drop or change any other row
- Does not cite outside yield benchmarks

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
