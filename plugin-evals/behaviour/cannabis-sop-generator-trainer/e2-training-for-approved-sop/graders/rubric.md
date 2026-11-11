---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Builds a quick-reference summary that keeps every hold, escalation and role restriction from the SOP (a unit-count or unconfirmed-threshold weight mismatch holds the shipment, the Warehouse Lead escalates to the Compliance/Inventory Manager, no undocumented batch or SKU substitution, the picker never verifies), a 5 to 10 question comprehension check tied to the SOP's critical steps with critical questions marked, a separate answer key that cites the SOP step for each answer, a pass rule (every critical question right and at least 80% overall, unless the operator sets another), what happens on a fail (review missed steps, retake before working unsupervised), a sign-off log naming the SOP ID and version, with score, result and retest date, and a retraining trigger tied to the SOP's review date.

PASS only if ALL of these hold:
- Every question maps to a step, warning or control in the SOP
- Quick-reference summary keeps the Section 7 hold and escalation (a unit-count or weight mismatch holds the shipment until the Compliance/Inventory Manager resolves it) and the no-undocumented-substitution warning, not only the manifest-match rule
- Includes an answer key with the source step for each answer
- States a pass rule and a retrain-and-retest rule on fail
- Sign-off log identifies the SOP ID and version and has columns for score, result and retest date
- Retraining is tied to the SOP's own review date and to any revision

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
