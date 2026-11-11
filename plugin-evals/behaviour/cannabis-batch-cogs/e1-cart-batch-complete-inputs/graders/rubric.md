---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Cost per unit $9.51 (total $4,680.75) from the script; materials $3,429.75, labor $336, overhead $490, testing $425; distillate ~46% of cost; yield variance -8 units adding ~$0.15/unit; sensitivity on distillate, hardware, overhead; no assumptions; one-line note that 280E treatment needs a CPA.

PASS only if ALL of these hold:
- Reports cost per unit of $9.51 (9.5137) and total batch cost $4,680.75
- Shows a line-by-line roll-up including labor ($336), overhead ($490), and testing ($425)
- Reports yield variance of -8 units and about $0.15 added cost per unit
- Includes sensitivity for the top drivers (distillate first) at plus/minus 10% and 20%
- Mentions 280E/tax treatment only as out of scope requiring a CPA, without explaining tax law

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
