# Replenishment Plan — [Store / Account] — sales window [start] to [end]

## Bottom line
[2–4 sentences: SKUs to reorder, total PO $ by vendor, stockouts, dead-stock $ at cost, the one decision the buyer must make today.]

## Sources
| File | Covers | Rows | Mapping confirmed |
|---|---|---|---|
| Sales | [date range] | | |
| On hand | as of [date] | | |

## Assumptions to confirm
- [every default the script used: window, safety days, cover days, dead/slow thresholds]
- [lead times or case packs filled in by the buyer verbally]

## Reorder now
| SKU | Product | Vendor | Units/day | On hand | Open PO | Days of supply | Suggested qty | Est. cost | Notes |
|---|---|---|---|---|---|---|---|---|---|

## Needs a vendor before it can go on a PO
| SKU | Product | Brand | Suggested qty | Est. cost | Who supplies it? |
|---|---|---|---|---|---|
(From `lines_needing_vendor`. Not included in the PO total.)

## Held for review (no order until fixed)
| SKU | Product | Flag | What to fix |
|---|---|---|---|
(From `skus_held_for_review`: conflicting duplicate rows, unreadable open PO, unreadable lead time.)

## Stockouts
| SKU | Product | Last sale | Units/day (understated) | Recommendation |
|---|---|---|---|---|

## Dead and slow stock
| SKU | Product | On hand | Last sale | Days of supply | $ at cost | Suggested action | Shelf-life / test date check |
|---|---|---|---|---|---|---|---|
(Shelf-life and retest limits are state-specific: NEEDS VERIFICATION.)

## Watch list
- New SKUs (provisional velocity), SKUs with open POs covering a low on-hand, possible SKU-churn pairs, SKUs with no lead time, SKUs ordered on a default lead time (`DEFAULT_LEAD_TIME`)

## Data gaps
- [Every `input_problems` line from the script: duplicate SKU rows summed, conflicting values, lead times read from text, unreadable open PO / case pack / cost]
- ...

---
Prepared by AI-assisted analysis on [date] from files: [list]. PO lines are a draft for buyer review. Nothing has been sent to any vendor.
