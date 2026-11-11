---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: The user did not say when on-hand was counted. The agent asks for the on-hand count date before computing anything and does not take it from the last sale date in the export. If the script is run without --as-of it exits (code 2) with: 'the following arguments are required: --as-of. The date of the on-hand count (YYYY-MM-DD). The sales window ends on this date.' The agent reports that as the reason it needs the date and does not hand-compute order quantities. Once the user gives 9/30, the run with --as-of 2026-09-30 --safety-days 3 gives the $4,620 PO draft from eval 1.

PASS only if ALL of these hold:
- Asks for the date of the on-hand count before giving any order quantities
- Does not use the last sale date in the export as the on-hand count date without asking
- Does not hand-compute velocity, reorder points or order quantities when the script cannot run
- If the user answers 9/30, reports the $4,620 PO draft from the script

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
