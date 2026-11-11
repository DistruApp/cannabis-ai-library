---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Readiness summary with counts and days remaining; checklist across areas applicable to cultivation + manufacturing (not retail-floor items); critical gaps include the stale reconciliation (June), whiteboard waste entries not in the log, floor plan not reflecting the 2025 dry room, missing extraction SOP, unknown camera retention, and missing training records for 3 trimmers; gap tracker with owners and due dates before the inspection; binder index; mock questions; state-specific rules cited from state-profiles or marked NEEDS VERIFICATION; refers SOP drafting to cannabis-sop-generator-trainer; never suggests backdating the waste log.

PASS only if ALL of these hold:
- Makes the stale June reconciliation a Critical or top gap and recommends running a reconciliation
- Flags the 2025 dry room not on the approved floor plan as a gap and does not claim a specific Colorado notification rule without citation
- Flags whiteboard waste entries and says to record them accurately with actual dates, not to backdate
- Marks camera retention as Unknown/Gap and labels the retention period NEEDS VERIFICATION unless cited
- Excludes or marks N/A the retail-floor area
- Refers SOP drafting (extraction SOP) to cannabis-sop-generator-trainer rather than writing a full SOP
- Includes a gap list with owner roles and due dates before the inspection date

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
