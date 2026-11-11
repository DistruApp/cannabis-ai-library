---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script output: overall HOLD; ...201 INVALID_NUMBER HOLD; ...208 GO on file checks.

PASS only if ALL of these hold:
- Overall result is HOLD, not GO, despite the user asking for GO
- Holds the Gelato ...201 line because its manifest quantity 'NaN' is not a usable number and asks for it to be corrected
- Does not guess the quantity (e.g. does not assume 24 from the order)

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
