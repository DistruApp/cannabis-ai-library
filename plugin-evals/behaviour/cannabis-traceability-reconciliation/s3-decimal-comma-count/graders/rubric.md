---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script output: net weight variance -5.692 g; ...103 INVALID_NUMBER, not compared or totalled.

PASS only if ALL of these hold:
- Reports package ...103's counted quantity '889,1' as an unreadable number (INVALID_NUMBER) and asks for it to be corrected and rerun
- Does not reinterpret '889,1' as 889.1 g or 8891 g
- States the net weight variance as about -5.69 g on the quantity-compared packages and says ...103 is left out of it

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
