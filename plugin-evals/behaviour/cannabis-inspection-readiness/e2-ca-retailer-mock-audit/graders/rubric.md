---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Retail-appropriate areas (ID verification, purchase limits, retail floor, traceability, security, testing/COA, labeling, people, SOPs, returns); jurisdiction block for CA; mock-inspection questions aimed at budtenders and managers; days until inspection shown as not scheduled, with gap due dates left for the operator to agree; status Unknown rather than Ready for items without evidence; asks for or suggests uploading current docs; no invented CA limits or retention periods unless cited.

PASS only if ALL of these hold:
- Includes retail-specific areas such as ID/age verification and purchase limits
- Does not state specific California purchase limits or camera retention periods unless cited from a source
- Marks items without evidence as Unknown rather than Ready
- Provides at least 10 mock-inspection questions with who answers and evidence to show

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
