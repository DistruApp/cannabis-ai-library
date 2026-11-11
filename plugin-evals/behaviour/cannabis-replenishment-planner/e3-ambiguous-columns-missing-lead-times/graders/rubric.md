---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Detects that the sales file has no SKU column and the on-hand file has two candidate quantity columns (On Hand vs Available); asks one combined question covering which on-hand column to use, whether product name can serve as SKU, the date of the on-hand count, vendor lead times, safety stock and order cycle; does not produce order quantities until lead times are provided or explicitly assumed and labeled.

PASS only if ALL of these hold:
- Identifies the On Hand vs Available ambiguity and asks which to use
- Notes there is no SKU column and proposes using product name with the SKU-churn caveat
- Asks for lead times (and safety/cover days) in a single combined question
- Asks for the date of the on-hand count instead of taking the last sale date
- Does not present order quantities based on invented lead times

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
