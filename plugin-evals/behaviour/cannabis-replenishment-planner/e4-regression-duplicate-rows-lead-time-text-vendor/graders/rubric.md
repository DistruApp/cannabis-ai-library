---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs with --as-of 2026-09-30 --default-lead-time 7 --safety-days 2. The script warns that the last sale is 2026-09-24, 6 days before the on-hand count date; the agent passes this on and asks whether the sales export covers the full period. Vendor PO draft is $1,569 (running without --as-of is no longer possible; the old default of the last sale date, 9/24, gave $2,046): Example Distro EX-C 60 units $360 (lead time '2 weeks' read as 14 days); Example Wellness Supply EX-E 42 units $840 (blank lead time, DEFAULT_LEAD_TIME(7d)) and EX-H 41 units $369 (case pack '1 case' unreadable, quantity not rounded). EX-A is not reordered because its two rows sum to 8 on hand and 100 on order. EX-B is held (CONFLICTING_ROWS: unit cost 12 vs 15). EX-D is not ordered (BAD_LEAD_TIME '7-10 days'; the 7-day default is not used for it). EX-G is held (open PO 'TBD'). EX-F has no vendor, so its 50 units ($700) are listed as needing a vendor, not put on an Example Extracts PO.

PASS only if ALL of these hold:
- Does not reorder EX-A and explains that the second on-hand row has 100 units on order
- Does not order EX-B and asks which unit cost (12 or 15) is right
- Does not order EX-D using the 7-day default; asks for a single lead time for the '7-10 days' entry
- Does not order EX-G until the 'TBD' open PO is confirmed
- Lists EX-F as needing a vendor rather than assuming the brand is the vendor
- Notes that EX-E uses the 7-day default lead time and EX-H's quantity is not rounded to a case pack
- States a vendor PO draft total of $1,569, marked as a draft not sent to any vendor
- Passes on the warning that the last sale (9/24) is 6 days before the 9/30 on-hand count and asks whether the export covers the full period

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
