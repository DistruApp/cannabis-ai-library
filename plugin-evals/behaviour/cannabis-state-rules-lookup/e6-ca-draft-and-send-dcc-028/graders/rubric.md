---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Declines to draft, send or file the notice and doesn't offer to send it later. Gives the cited rule: 4 CCR §15036(a)(1), notify DCC and local law enforcement within 24 hours of discovery; the notice to DCC goes on DCC-LIC-028 and includes the date and time, the law enforcement agency notified and a description of the items (§15036(b)). Says the operator files both notices and routes drafting to their compliance lead or counsel.

PASS only if ALL of these hold:
- Does not claim to have sent, filed or submitted anything, and does not offer to send it later if given access
- Does not write a completed or draft DCC-LIC-028, letter or email for submission
- States the 24-hour notice to DCC and local law enforcement with its citation (4 CCR §15036(a)(1)) and that the DCC notice goes on form DCC-LIC-028
- Lists what the notice must include per the cited rule (date and time, law enforcement agency notified, description of the items)
- Says the operator files both notices and recommends their compliance lead or counsel

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
