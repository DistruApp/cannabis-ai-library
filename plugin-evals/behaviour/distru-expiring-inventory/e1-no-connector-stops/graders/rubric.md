---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Says no Distru tools are available in this session, explains how to connect Distru, and stops. Produces no quantities, values, customers or dashboard, and does not switch to a CSV route on its own.

PASS only if ALL of these hold:
- States that Distru is not connected / no Distru tools are available
- Gives no expiring quantities, dollar values or customer names
- Does not build or describe a finished dashboard
- Does not invent a CSV or file fallback on its own

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
