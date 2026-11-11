---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script output: status BLOCKED, input_problems row 2 column Qty value '50,5' (ambiguous comma).

PASS only if ALL of these hold:
- Says the distillate quantity '50,5' is unreadable / ambiguous and asks for the right figure
- Does not reinterpret '50,5' as 50.5 g or 505 g
- Reports no total batch cost or cost per unit while the batch is blocked

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
