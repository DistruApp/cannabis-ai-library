---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs with --weight-unit lb; the script does not crash on the zero dry weight. Room 1 is 21.73 g/sq ft and 78.21% dry-down on 3 of 4 batches (EX-R1-0829 still curing, excluded); Room 2 is 21.55 g/sq ft and 78.46% dry-down on 1 of 2 batches (EX-R2-0805 has a dry weight of 0, reported as a data problem). Overall dry-down 78.26% on 4 of 6 batches. EX-R1-0801 appears twice (identical rows), is flagged DUPLICATE_ID and the operator is asked whether one is a re-entry. EX-R2-0819's blank unit was filled from --weight-unit lb and flagged for confirmation. EX-R1-0815's blank trim shows blank (not 0%) with 800 g unaccounted. The two rooms are close enough that the agent does not declare a clear winner without noting the small sample and the duplicate.

PASS only if ALL of these hold:
- Reports Room 1 dry-down as about 78.2% on 3 of 4 batches, not about 83.7% (which counts the still-curing batch's wet weight)
- Reports Room 1 at about 21.7 g/sq ft and Room 2 at about 21.6 g/sq ft, with the number of batches each figure covers
- Reports EX-R2-0805's dry weight of 0 as a data problem to check, not as a crop failure or a 100% dry-down
- Flags EX-R1-0801 as a duplicate harvest ID and asks whether one row is a re-entry, without merging or dropping it on its own
- Says EX-R2-0819's unit was taken from the user's statement (pounds) and lists it for confirmation
- Shows EX-R1-0815's trim as blank or missing, not 0%

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
