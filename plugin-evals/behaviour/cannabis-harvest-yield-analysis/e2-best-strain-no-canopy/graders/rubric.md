---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Notices no unit column and asks for the weight unit before running (values like 118/26 could be lb or kg); notes canopy and lights are missing so only per-plant comparison is possible; caveats tiny sample (3 batches, too few for anomaly fences) and that strain is confounded with room; does not recommend a strain based on outside benchmarks.

PASS only if ALL of these hold:
- Asks for (or explicitly confirms) the weight unit instead of assuming grams or pounds
- Says per-sq-ft comparison is not possible without canopy data, so only a per-plant comparison can be made
- Caveats that 3 batches is too few for anomaly flags or a confident recommendation
- Notes strain and room are confounded
- Does not cite outside yield benchmarks

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
