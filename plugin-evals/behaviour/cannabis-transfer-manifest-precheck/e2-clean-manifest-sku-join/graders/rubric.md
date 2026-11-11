---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Joins order to manifest by SKU, finds no file-based issues, returns 'GO on file checks' with manual checks still required, and does not call the shipment compliant.

PASS only if ALL of these hold:
- Result is GO on file checks with both lines GO
- States that manual checks (license status, driver/vehicle/route, labeling) are still required
- Does not use the word 'compliant' to describe the shipment
- Includes a jurisdiction block naming California and leaves unverified CA transport rules as NEEDS VERIFICATION

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
