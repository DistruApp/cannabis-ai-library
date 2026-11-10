---
name: cannabis-replenishment-planner
description: Turn cannabis sales and on-hand inventory exports into a replenishment plan, including sell-through, days of supply, reorder points, stockout and dead-stock flags, and a draft purchase order grouped by vendor with total cost. Use when a dispensary buyer or inventory manager asks what to reorder, which SKUs are selling through, what's about to stock out, what's sitting dead, or wants a PO draft from a POS export (Dutchie, Flowhub, Treez, etc.). Also use when a distributor or brand plans replenishment for its retail accounts from their sell-through data, even if they don't say "replenishment." Not for state traceability reconciliation, cultivation or production planning, wholesale pricing, or actually sending orders to vendors.
license: MIT
metadata:
  version: "1.0"
  category: retail-purchasing
  risk-level: medium
  last-compliance-review: "2026-10-16"
---

# Replenishment planner

Gives a buyer a reorder list they can defend: what to buy, how much, from whom, what it costs, and what not to buy because it's already sitting. The math comes from `scripts/replenish.py`. Your job is the inputs, the judgment calls, and a report the buyer can act on. **PO lines are drafts. Never send them.**

## Workflow

```
- [ ] 1. Get the two exports and the planning parameters
- [ ] 2. Confirm the column mapping
- [ ] 3. Run scripts/replenish.py
- [ ] 4. Sanity-check velocity (promos, stockouts, new SKUs, SKU churn)
- [ ] 5. Write the report and PO draft from assets/
```

### 1. Inputs

Required:
- **Sales export** by SKU with a date per row (POS for a dispensary; account sell-through for a distributor/brand). At least 4 weeks of history is ideal.
- **Current on-hand by SKU**, as of the end of the sales period. Say if the as-of dates don't line up.

Planning parameters. Ask for them in **one** combined question. Use the operator's values and never invent "industry standard" targets:

| Parameter | Flag | If not given |
|---|---|---|
| Vendor lead time (days) | per-SKU column, or `--default-lead-time` | SKUs show `NO_LEAD_TIME`, with no order qty. Ask. |
| Safety stock (days) | `--safety-days` | 0, tagged [ASSUMPTION] |
| Days to cover after delivery (order cycle) | `--cover-days` | 14, tagged [ASSUMPTION] |
| Velocity window | `--window-days` | Last 28 days in the data, stated in the report |
| Dead-stock threshold | `--dead-days` | 30 days with no sales, [ASSUMPTION] |
| Slow-mover threshold (days of supply) | `--slow-dos` | 90, [ASSUMPTION] |

Optional per-SKU columns: unit cost (needed for PO dollars and dead-stock value), case pack/MOQ, vendor, open PO qty. If the operator has a budget cap (cash is tight for most cannabis businesses), ask for it.

### 2. Mapping

Run `python3 scripts/replenish.py --sales <file> --onhand <file> --detect-only` and show the detected mapping in one line per file. If a column is missing or `AMBIGUOUS` (e.g. both "On Hand" and "Available"), ask which one and pass `--map-sales field=Column` / `--map-onhand field=Column`. Alias hints are in `references/system-mappings.md`. If the export has product names but no SKU, map `sku=Product` and warn that name changes will split history.

### 3. Run

```
python3 scripts/replenish.py --sales <file> --onhand <file> --out-dir <dir> [params] [mappings]
```

Use the script's numbers as-is and don't recompute by hand. Copy every entry in `assumptions` into the report's assumptions list. Formulas and flag definitions are in `references/method.md`. Read it if the user asks how a number was calculated.

### 4. Sanity-check before recommending

Look at `replenishment.csv` for these and adjust **the recommendation, not the math**:
- `STOCKOUT(demand understated)`: zero on hand with recent sales. Measured velocity is too low because days with no stock record no sales. Say the true need is likely higher and recommend the buyer bump the qty. Don't invent a number.
- `NEW_SKU`: velocity comes from fewer days of history. Treat it as provisional.
- Promo or holiday spikes: if a big one-day spike sits inside the window (4/20, Green Wednesday, a vendor day, a Labor Day sale), rerun with `--as-of` or `--window-days` to exclude it, or call it out. Ask the buyer whether the spike will repeat.
- `RETURNS_IN_WINDOW`: returns reduce net units. Note them.
- Open POs: a low days-of-supply SKU with a large open PO isn't a reorder. It's an "is the PO arriving on time?" question.

### 5. Report

Fill `assets/plan-template.md`, then `assets/po-draft-template.md` grouped by vendor with line and total cost. Lead with the bottom line: number of SKUs to reorder, total PO dollars, stockouts, and the dollar value tied up in dead stock. Follow `references/output-conventions.md` for labels.

## Gotchas

- **SKU churn.** Cannabis products often get a new SKU per batch, strain drop, or package redesign. Two SKUs with near-identical names, where one stopped selling as the other started, are probably one product. Ask before combining them. Combining wrongly double-counts demand, and not combining shows a fake dead SKU plus a fake new SKU.
- **Velocity is not demand when you were out of stock.** See `STOCKOUT` above.
- **Aging and test validity.** Dead or slow stock may be near the end of its shelf life or past state retesting or label-date limits. Those rules are state-specific, so mark them **NEEDS VERIFICATION** rather than stating a limit. Recommend checking package and test dates on anything flagged `DEAD`.
- **Unit mismatch.** The sales export may count units (each) while on-hand is in grams for bulk or deli-style flower. Don't mix them. Ask for the conversion or exclude those SKUs.
- **Case packs round up.** Suggested qty is rounded up to the case pack. Say so when rounding meaningfully increases cash outlay.
- **Cash first.** If the PO total exceeds the budget, rank lines by days of supply (lowest first) and margin if cost and price are known, and show where the budget runs out. Don't cut lines silently.
- **Distributor/brand use.** Running this on retail account data means the "PO draft" is a *suggested order* to propose to the account's buyer. Label it that way.
- **Never send.** The output is a draft for the buyer. No emailing vendors and no submitting orders in any system.

## Example

User: "Here's our Dutchie sales for Aug–Sep and today's on-hand. Lead times are in the sheet. Keep 3 days safety. What do I order?"

Good output opens with: "3 SKUs to reorder, $4,620 across 3 vendors (Example Pines Distribution $1,680, Example Coast Extracts $1,980, Example North Farms $960). Live Resin Gelato sold out 9/28, so its 110-unit order is probably low because velocity was measured while out of stock. $350 at cost is tied up in the Sativa 5pk pre-rolls, which haven't sold since 8/20. Check package and test dates before discounting. Chocolate bar has no lead time or vendor, so it isn't ordered yet…". It then gives the assumptions (14-day cover and 30-day dead threshold are defaults, confirm), the SKU table, the PO draft by vendor, and data gaps.
