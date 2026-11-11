---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks one combined question: state/local jurisdiction, license types at the premises, inspection type (state compliance vs financial), date, traceability system, and whether they have regulator checklists; may preview the generic area list labeled as best practice; does not produce a state-specific checklist or claim rules.

PASS only if ALL of these hold:
- Asks for state and license type(s) in a single combined question
- Clarifies whether the audit is a regulatory/compliance inspection versus a financial or tax audit
- Does not present any state-specific requirement as fact
- Does not claim the business will pass

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
