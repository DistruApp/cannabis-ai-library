---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs with --as-of 2026-09-30 (same on-hand file as before, counted 9/30) and --window-days 35 so 9/1 is included, recognizes the GMO Cookies velocity is inflated by the 40-unit promo day and either reruns excluding it or explains the effect; treats NB-SM-14 velocity as provisional (NEW_SKU, 11 days); uses safety_days=0 as operator-provided, not as an assumption. GH-CHOC-100 has a blank lead time and a blank vendor: it uses the operator's 7-day default (flagged DEFAULT_LEAD_TIME(7d)) and is flagged NO_VENDOR, so its 18-unit ($162) suggestion is listed as needing a vendor instead of being placed on an Example Edibles Co PO. On the 35-day run that includes the promo day, the vendor PO draft totals $3,864 and does not include the chocolate line.

PASS only if ALL of these hold:
- Uses a 35-day window ending 2026-09-30
- Calls out that the 9/1 promo spike inflates GMO Cookies velocity and asks whether it will repeat or shows the result without it
- Labels Runtz smalls velocity as provisional due to limited history
- Does not invent an industry sell-through or days-of-supply benchmark
- Does not put GH-CHOC-100 on a vendor's PO by assuming its brand is the vendor; asks who supplies it and notes its lead time is the operator's 7-day default

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
