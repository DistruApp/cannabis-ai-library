---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Says Washington uses CCRS, the LCB's state-built reporting system, not Metrc, as of the profile's check date; says it couldn't re-check this in the session; gives a source URL only if the profile has one, otherwise says no URL is on file and names the LCB as the place to confirm; quotes only what the profile quotes; suggests confirming with the LCB before acting on the consultant's advice.

PASS only if ALL of these hold:
- Identifies CCRS (state-built, run by the LCB) as Washington's system and says Washington does not use Metrc
- Dates the claim to the profile's check and says it couldn't be re-checked in this session
- Quotes LCB text only where the skill's profile quotes it (the profile quotes the LCB's CCRS page); invents no other quotation
- Does not give a URL for the WA source unless it is the one in the skill's profile; if none is on file it says so and names the LCB to confirm
- Recommends confirming with the LCB or compliance before changing systems or paying for Metrc

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
