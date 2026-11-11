# Cannabis State Rules Lookup

Skill: [`cannabis-state-rules-lookup`](../../../skills/cannabiz-skills/compliance/cannabis-state-rules-lookup/SKILL.md)

## What it does

Gives a licensed cannabis operator a cited answer to a state rule question: the rule, the exact text, the source link, the effective date and the date it was checked. If a rule can't be verified from a primary source, it says so plainly and tells the operator where to check. It ships with detailed profiles for CA, CO, MI, MA, NY, IL and OK, plus a table of the traceability system each of 26 states uses. Every entry is labelled verified or unverified: most Michigan rules, Colorado's rule quotes since the November 2026 rule update, and the systems for PA, CT and DE are flagged for the operator to confirm.

## When to use it

- "How often do we have to reconcile Metrc in California?"
- "Which seed-to-sale system does Washington use now?"
- "Is it allowed to give samples to budtenders in Massachusetts?"
- "Colorado changed rules in November, does that affect us?"
- Any time someone wants a rule checked before changing an SOP or submitting something to the state

## How to use it

- **Inputs:** the question, the state, the license type, and whether the license is medical, adult use or both. It asks for anything missing in one question.
- **Tools / connectors:** none required. Web access makes it better, since it can check live regulator pages when the built-in profile is out of date.
- **Works in:** Claude or any LLM.
- **Limits:** not legal or tax advice. Questions about 280E are sent to a CPA.

## Example

**Input:** "We're a California distributor. How often do we have to reconcile Metrc and what happens if we're off?"

**Output:** "At least every 30 calendar days, and a significant discrepancy (5 percent) means an audit and written notice to DCC. Separately, you must report a significant discrepancy to DCC and local law enforcement within 24 hours of finding it." It cites 4 CCR sections 15051, 15034 and 15036 with the source link and date, and flags that the rule does not say whether the 5 percent is per package or on total inventory.
