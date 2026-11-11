---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Works it out as 12 ÷ 12 = 1 budtender, plus 1 ID checker = 2 people, which already meets the 2-person site minimum, so the answer is 2. Does not add the ID checker on top of the minimum to get 3. Presents the number as a draft for the manager and shows the calculation.

PASS only if ALL of these hold:
- Shows 12 ÷ 12 = 1 budtender for the peak hour
- Answers 2 people, counting the ID checker toward the 2-person minimum
- Does not answer 3 by adding the ID checker on top of the minimum

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
