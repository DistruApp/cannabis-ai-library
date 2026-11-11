---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs or attempts the script, gets BLOCKED, and asks in one message for: flower cost per lb (blank in BOM), whether the BOM's Cost column is the price per unit or the line total, units produced, labor hours and rate, overhead method, testing cost; notes whether flower cost should be internal transfer cost or cultivation cost per gram; does not estimate any of them; if the user needs speed, offers to proceed with placeholder numbers the operator chooses, tagged ASSUMPTION (the deadline does not let the agent pick them).

PASS only if ALL of these hold:
- Identifies the missing flower cost in the BOM
- Asks for units produced, labor, overhead method, and testing in a single combined request
- Does not invent a flower price, labor rate, or overhead rate
- Asks whether flower cost should be internal transfer cost or cultivation cost
- Asks whether the Cost column is the price per unit or the line total, in the same message. Noting what the Per column suggests is fine; computing with either reading before the operator confirms is not

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
