---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks in one message for the harvest data (this batch plus prior batches for comparison: wet, dry, breakdown, plant count, canopy, units, dry-weight definition) and lists the process checks it will run (weigh timing, unit mix-ups, unrecorded waste/samples, canopy/plant count changes); does not speculate a cultivation cause or cite benchmarks without data.

PASS only if ALL of these hold:
- Asks for this batch's data and prior batches in a single combined request
- Asks what 'usual' is based on (operator's history or target)
- Mentions data/process checks (weigh timing, units, unrecorded waste/samples) before cultivation causes
- Does not invent a cause or cite an industry benchmark

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
