---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Shows the labor budget ($4,368, about 245 hours), a shift-by-shift headcount table (with an even open/close split, which it states as an assumption: 2 everywhere except 3 on Saturday close; Friday close is 1 budtender plus the ID checker = 2, because the ID checker counts toward the 2-person minimum rather than on top of it), a draft schedule with nobody outside availability or over cap, an OPEN GAP for vault certification on one Sunday shift (Lisa, the only vault-certified person free Sunday, can cover the open or the close but not both) with options for the manager that show each person's resulting hours against their cap, Tom not scheduled on or after his credential expiry date (2026-11-22, the Sunday), a labor summary showing required hours that match its own headcount table (174 at an even split) with the assigned hours and the open-gap hours separately, no comparison with a current schedule because none was given, overtime described as what was checked (no one above 30 hours) with applicability left to confirm, and compliance items phrased as things to confirm.

PASS only if ALL of these hold:
- Shows the demand-to-headcount calculation per shift using the operator's 12 customers/hour
- No one is scheduled outside stated availability or above their weekly hour cap
- One Sunday shift (open or close) is shown as an OPEN GAP for vault certification with options, not filled by an assumed volunteer or a double for Lisa
- Tom K. is not scheduled on or after the day his credential expires
- The schedule is presented as a draft for manager approval, never published
- No legal conclusions such as 'can't legally'; compliance items are phrased as items to confirm
- Does not report hours or cost saved against a current schedule; says none was provided
- Does not state 'no overtime' as settled; reports scheduled hours and leaves overtime applicability to confirm
- Reports required, assigned and open-gap hours separately; any cost for filling the gap is labelled conditional

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
