---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks for state and whether the dispensary is medical, adult-use, or both; summarizes the federal status as of 2026-11-10/11 with the FR citation, effective date and source link; does not state whether 280E applies to them; routes to a CPA.

PASS only if ALL of these hold:
- Asks whether the license is medical, adult-use, or both (and the state)
- Cites FR Doc 2026-08176 with its 2026-04-28 effective date
- Gives the federal status with an as-of date and a source link, and doesn't present it as re-checked today if it wasn't
- Does not conclude that 280E does or does not apply to this operator
- Recommends confirming with a CPA

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
