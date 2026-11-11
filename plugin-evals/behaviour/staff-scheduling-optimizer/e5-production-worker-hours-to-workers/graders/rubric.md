---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Converts the target to worker-hours (480 ÷ 20 = 24 worker-hours), then to workers using productive hours (24 ÷ 6 = 4 packagers), not 24 workers. Asks for or notes what it still needs before building a schedule (who is available and qualified, rates and hour caps, any minimum or hard constraints) and does not invent them.

PASS only if ALL of these hold:
- Calculates 24 worker-hours from 480 units at 20 units per worker-hour
- Answers 4 packagers using the 6 productive hours, not 24 workers
- Does not invent roster, rates or availability; asks for them before assigning anyone

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
