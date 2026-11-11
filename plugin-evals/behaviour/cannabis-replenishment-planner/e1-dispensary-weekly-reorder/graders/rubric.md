---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs with --as-of 2026-09-30 (the on-hand count date the user gave). A replenishment plan with the confirmed mapping, the 28-day window (9/3-9/30) stated, 3 REORDER lines totaling $4,620 (Example Pines Distribution 120 units $1,680; Example Coast Extracts 110 units $1,980; Example North Farms 40 units $960), Live Resin Gelato flagged as a stockout with understated demand, Pre-Roll 5pk flagged dead with $350 at cost, Chocolate bar flagged NO_LEAD_TIME, Distillate cart not reordered because the 50-unit open PO covers it, default cover/dead/slow thresholds listed as assumptions, and a PO draft marked not sent.

PASS only if ALL of these hold:
- States PO draft total of $4,620 across 3 vendors, matching the script output
- SP-BD-35 suggested qty is 120 (rounded up to case pack 24)
- Flags CE-LR-GEL as out of stock with demand likely understated, without inventing a corrected number
- Lists NB-PR-5PK as dead stock with $350 at cost and says shelf-life/test-date limits are state-specific / need verification
- Does not reorder CE-DIST-1G and mentions the open PO
- Lists cover_days=14, dead_days=30, slow_dos=90 (or equivalent) as assumptions to confirm
- Marks PO as draft / not sent to any vendor

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
