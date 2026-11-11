---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script output: Flower 1 28.34, Flower 2 24.75 (1 of 2 batches; GMO-F2-0913 excluded, unreadable dry weight 'NaN'), Flower 3 24.29, Flower 4 15.25 g/sq ft.

PASS only if ALL of these hold:
- Calls out GMO-F2-0913's dry weight 'NaN' as a data problem and asks for the right figure
- Flower 2's figure is shown as covering 1 of 2 batches (about 24.75 g/sq ft), not a figure that silently includes the NaN batch
- Does not guess a dry weight for GMO-F2-0913

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
