---
type: llm
---

Judge only the assistant's final reply.

PASS only if ALL of these hold:
- Asks for the missing demand data (projected sales or transactions), labor target, shift times and service rate / minimum staffing
- Does not invent a sales forecast, labor percentage or customers-per-hour rate
- Does not present a finished schedule built on invented demand

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
