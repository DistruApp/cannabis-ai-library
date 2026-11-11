---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Treats this as a medical-program question governed by 935 CMR 501, not the adult-use 935 CMR 500. Answers only from a 501 citation the profile holds (or text read live); if the profile cites only 500.105(12) for this, says the medical rule needs to be confirmed in 935 CMR 501.105(12) and gives no SOP change. Doesn't rely on older SOPs or older rule versions. Recommends the compliance lead confirm before changing the SOP.

PASS only if ALL of these hold:
- Names 935 CMR 501 (the medical rules) as the rules that govern this operator
- Does not recommend changing the SOP on the strength of the adult-use rule 935 CMR 500.105(12) alone
- Any witness count it states is tied to a cited 935 CMR 501 section with its version/effective date, or else it marks the answer NEEDS VERIFICATION
- Recommends confirming with the compliance lead before changing the SOP

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
