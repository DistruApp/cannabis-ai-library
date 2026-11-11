---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs or attempts the script, gets BLOCKED, and asks in one message for: flower cost per lb (blank in BOM), units produced, labor hours and rate, overhead method, testing cost; notes whether flower cost should be internal transfer cost or cultivation cost per gram; does not estimate any of them; offers to proceed with tagged assumptions if the user prefers speed.

PASS only if ALL of these hold:
- Identifies the missing flower cost in the BOM
- Asks for units produced, labor, overhead method, and testing in a single combined request
- Does not invent a flower price, labor rate, or overhead rate
- Asks whether flower cost should be internal transfer cost or cultivation cost

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
