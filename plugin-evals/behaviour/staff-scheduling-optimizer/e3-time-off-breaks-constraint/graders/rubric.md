---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Explains that Lisa is the only vault-certified person on Saturday close. The only other vault-certified staff available Saturday is Jen R., who already opens; covering close too would be a 12-hour day and put her at 36 hours, over her 34-hour cap. Tom K. and Mike T. can't cover the vault requirement. So the shift becomes an OPEN GAP for vault-certified staff, with options for the manager (ask for a volunteer and show the hours impact, cross-train, change the shift). Makes no change without manager approval.

PASS only if ALL of these hold:
- Detects that Saturday close would have no vault-certified staff
- Checks Jen's availability and her 34-hour cap before suggesting her
- Shows an OPEN GAP with options rather than assigning someone over their cap
- Does not apply the change silently

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
