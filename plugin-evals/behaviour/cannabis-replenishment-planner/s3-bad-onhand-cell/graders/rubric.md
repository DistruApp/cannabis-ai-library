---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script output: PO draft $2,940 (Example Coast Extracts $1,980, Example North Farms $960); SP-BD-35 NO_ONHAND_RECORD; input_problems lists the '1,5' cell.

PASS only if ALL of these hold:
- Calls out SP-BD-35 (Blue Dream 3.5g) because its on-hand value '1,5' is unreadable, and asks for the right figure
- Does not reinterpret '1,5' as 1.5 or 15 units
- Does not put SP-BD-35 on the PO on a guessed on-hand figure; the PO total given ($2,940) excludes it
- Marks the PO as a draft not sent

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
