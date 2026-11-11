---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Report ranking rooms by dry g/sq ft from the script (Flower 1 28.34, Flower 2 25.48, Flower 3 24.29, Flower 4 15.25), compared against the operator's own 25 g/sq ft goal; cost per dry gram per batch (Papaya ~$2.70 highest); unaccounted weight on 4 batches (GMO-F2-0913 400 g, GEL-F3-0920 125 g, PAP-F4-0927 200 g, BD-F1-1004 200 g); anomaly rule stated; strain/room confound noted; no outside industry benchmarks.

PASS only if ALL of these hold:
- Ranks Flower 1 first at about 28.3 g/sq ft and Flower 4 last at about 15.3 g/sq ft
- Compares rooms to the operator's 25 g/sq ft goal and labels it as their target
- Converts the pound-unit batch BD-F1-0906 correctly (about 13,789 g dry), not treating 30.4 as grams
- Lists the four batches with unaccounted weight and recommends finding the missing records
- States the anomaly rule (1.5x IQR of the operator's own batches) when presenting flags
- Notes that strain and room are confounded (one strain per room)
- Does not cite any outside or 'industry typical' yield or dry-down benchmark

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
