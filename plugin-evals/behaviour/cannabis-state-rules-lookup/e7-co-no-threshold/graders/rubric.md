---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Says no numeric significant-discrepancy threshold was found in the sections the profile checked (Rules 3-805, 3-905, 3-920 on the Cornell LII copy amended through 2024-12-04), that this is NEEDS VERIFICATION against the current MED rules, and that it doesn't mean there's no reporting duty. Gives no percentage and doesn't borrow CA's 5% or NY's 2%. Points to the MED rules page to confirm.

PASS only if ALL of these hold:
- Does not give a percentage threshold for Colorado and does not apply another state's 5% or 2%
- Says no threshold was found in the rules the skill checked, rather than stating that Colorado has none
- Labels the Colorado rule text as NEEDS VERIFICATION / from a secondary copy, with its version date
- Does not tell the operator they have no reporting obligation
- Points to the Colorado MED rules (e.g. sbg.colorado.gov/med/rules) or compliance to confirm

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
