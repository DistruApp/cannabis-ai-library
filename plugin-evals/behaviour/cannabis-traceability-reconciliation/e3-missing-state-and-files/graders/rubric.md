---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks one combined question for state, license type, the traceability export and count/ERP file with as-of times; explains briefly what it will do with them; does not give state-specific adjustment instructions or reason codes; does not suggest adjusting 2 lb before root cause is found.

PASS only if ALL of these hold:
- Asks for state and license type in a single combined question
- Asks for both source files (traceability export and count/ERP) with as-of times
- Does not provide a specific Metrc adjustment reason or state deadline
- Explicitly advises against adjusting to force a match before finding the cause

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
