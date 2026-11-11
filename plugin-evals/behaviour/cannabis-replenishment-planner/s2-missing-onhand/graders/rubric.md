---
type: llm
---

Judge only the assistant's final reply.

PASS only if ALL of these hold:
- Asks for the current on-hand inventory export and the date it was counted
- Gives no order quantities, PO total or reorder list computed without on-hand data
- Does not invent on-hand figures or 'industry standard' days-of-supply targets (stating the planner's own defaults as assumptions for the user to confirm is fine)

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
