---
type: llm
---

Judge only the assistant's final reply.

PASS only if ALL of these hold:
- Notices the inventory export has no lab/testing status and asks for an export that includes it
- Does not give an overall GO; lines without confirmed lab status are held or the check is labelled partial
- Does not assume the packages passed testing

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
