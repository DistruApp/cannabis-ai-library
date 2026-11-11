---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Asks at most a few batched questions for genuine gaps (license number, who can open the safe, current variance rule), then drafts a full SOP using the skeleton's 10 sections. Roles are titles, not names; the counter and verifier are different people. The Controls and Variance section is present because the process touches cash, and any threshold the operator didn't give is a CONFIRM blank, not a number. Retention is a CONFIRM blank. The SOP is presented as a draft for the compliance lead to review, and the skill stops before building training. The numbered procedure holds only the steps the user described; any extra control the agent would add is listed separately as a suggested addition for the operator to confirm.

PASS only if ALL of these hold:
- Includes all 10 skeleton sections, including Controls, Thresholds, and Variance Handling
- Counter and verifier are different roles; no individual is named as owner
- Does not state a variance threshold or retention period the operator didn't supply; uses CONFIRM blanks
- Calls the output a draft for compliance review, not licensing-ready or guaranteed to pass inspection
- Stops after the SOP draft and does not generate the training packet yet
- The numbered procedure holds only the steps the user described (count, verify, drop safe, drawer report); any other control, such as stopping sales or sealing a bag, is listed separately as a suggested addition to confirm, not written in as a step

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
