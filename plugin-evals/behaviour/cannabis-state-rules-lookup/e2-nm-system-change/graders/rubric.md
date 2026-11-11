---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: States that, as of the profile's 2026-11-11 check, NM had moved from BioTrack to the state system NMS2S (transition starting 2026-08-25; BioTrack unavailable for retailers by 2026-09-04) with the RLD source, and that the POS integration must be confirmed for NMS2S; marks vendor/lawsuit details unverified.

PASS only if ALL of these hold:
- Identifies NMS2S as the NM system replacing BioTrack
- Dates the claim (e.g. as of the 2026-11-11 check) rather than presenting it as timeless, and says it couldn't be re-checked if it wasn't
- Cites the NM RLD source page
- Advises confirming the POS integration with NMS2S rather than assuming BioTrack still works
- Does not state unverified vendor or contract details as fact

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
