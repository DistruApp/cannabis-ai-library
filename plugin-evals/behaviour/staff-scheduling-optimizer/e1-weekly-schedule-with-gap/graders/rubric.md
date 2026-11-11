---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Shows the labor budget ($4,368, about 245 hours), a shift-by-shift headcount table (2 everywhere except 3 on Friday and Saturday close), a draft schedule with nobody outside availability or over cap, an OPEN GAP for Sunday close (no vault-certified staff available) with options for the manager, Tom not scheduled on or after his credential expiry date (2026-11-22, the Sunday), no overtime, a labor summary around 180 hours, and compliance items phrased as things to confirm.

PASS only if ALL of these hold:
- Shows the demand-to-headcount calculation per shift using the operator's 12 customers/hour
- No one is scheduled outside stated availability or above their weekly hour cap
- Sunday close is shown as an OPEN GAP with options, not filled by an assumed volunteer
- Tom K. is not scheduled on or after the day his credential expires
- The schedule is presented as a draft for manager approval, never published
- No legal conclusions such as 'can't legally'; compliance items are phrased as items to confirm

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
