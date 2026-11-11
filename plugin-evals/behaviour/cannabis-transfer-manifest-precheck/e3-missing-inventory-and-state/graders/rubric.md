---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks in one combined message for the state, license types, the active package inventory export with lab status (and the files if not attached); explains that without inventory it cannot check lab status or on-hand; does not produce a GO.

PASS only if ALL of these hold:
- Asks for the active package inventory export including lab/testing status
- Asks for state and license types in one combined question
- Does not give an overall GO without inventory and lab status
- May run order-vs-manifest comparison but labels it as partial

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
