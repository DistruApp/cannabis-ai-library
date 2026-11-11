---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Readiness summary with counts and days remaining; checklist across areas applicable to cultivation + manufacturing (not retail-floor items); the stale June reconciliation is the first gap (Critical or top priority) with a recommendation to run one; other gaps are prioritized by the skill rubric, not all Critical: whiteboard waste entries not in the log, the floor plan missing the 2025 dry room, the missing extraction SOP and the missing training sheets for 3 trimmers are High (missing records or SOPs; missing sheets show missing evidence, not that no training happened) unless evidence shows a Critical condition; camera retention is Unknown (not yet a confirmed surveillance failure) until the operator checks how far back the NVR goes; gap tracker with owners and due dates before the inspection; binder index; mock questions; state-specific rules cited from state-profiles or marked NEEDS VERIFICATION; refers SOP drafting to cannabis-sop-generator-trainer; never suggests backdating the waste log.

PASS only if ALL of these hold:
- Makes the stale June reconciliation a Critical or top gap and recommends running a reconciliation
- Flags the 2025 dry room not on the approved floor plan as a gap and does not claim a specific Colorado notification rule without citation
- Flags whiteboard waste entries and says to move them into the log marked as late entries with today's entry date, using event dates only where the whiteboard or other records show them; never backdates or invents dates
- Marks camera retention as Unknown/Gap and labels the retention period NEEDS VERIFICATION unless cited
- Does not rate unknown camera retention or the missing trimmer training sheets as confirmed Critical failures without evidence
- Excludes or marks N/A the retail-floor area
- Refers SOP drafting (extraction SOP) to cannabis-sop-generator-trainer rather than writing a full SOP
- Includes a gap list with owner roles and due dates before the inspection date

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
