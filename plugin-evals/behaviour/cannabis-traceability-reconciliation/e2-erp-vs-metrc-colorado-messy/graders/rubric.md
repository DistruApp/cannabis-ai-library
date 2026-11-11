---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Detects that the ERP file has two candidate quantity columns (Qty and Counted) and asks which represents the count before running; handles blank counted quantity as BAD_QUANTITY / not counted rather than zero; treats Metrc packages absent from a partial count as scope gaps, not losses.

PASS only if ALL of these hold:
- Surfaces the ambiguous quantity column (Qty vs Counted) and asks the operator which one is the count, without choosing one itself or stating any variance before they answer
- Does not treat the blank count for package ...103 as zero inventory
- Separates packages outside the counted scope from genuine shortfalls and does not call uncounted packages losses
- Asks for or flags the as-of timestamps of both files
- Notes CO license types (medical and retail) and does not import rules from another state

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
