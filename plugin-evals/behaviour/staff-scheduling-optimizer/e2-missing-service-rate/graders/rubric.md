---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks how many customers one budtender can serve per hour at peak (or offers to estimate it from a shift the operator considers well staffed) and for the operator's minimum per shift, before giving a headcount. Does not assume an industry-standard service rate.

PASS only if ALL of these hold:
- Asks for the service rate or offers the well-staffed-shift estimate
- Does not use a default service rate of its own
- Asks for minimum staffing or hard constraints if not given

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
