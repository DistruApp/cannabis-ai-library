---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Cites 4 CCR §15051 (at least every 30 calendar days; audit + written notice to DCC if significant) and §15034 (5% difference), §15036(a)(1) (notify DCC and local law enforcement within 24 hours of discovering a significant discrepancy, on DCC-LIC-028), notes the unofficial-compilation status and the base ambiguity of the 5%, and recommends confirming with compliance.

PASS only if ALL of these hold:
- States 'at least once every 30 calendar days' with citation §15051
- States the 5% significant-discrepancy definition with citation §15034
- Flags that the rule does not specify the base (per package vs total) for the 5%
- Includes a source URL and an access/verification date
- States the 24-hour notice to DCC and local law enforcement for a significant discrepancy, citing §15036(a)(1) (form DCC-LIC-028)
- Does not invent any other deadline not present in the cited text

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
