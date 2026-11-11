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
- **One account or store per run.** A brand or distributor planning several retail accounts, or a chain with several stores, runs the script once per account with both exports filtered to it. If either file has an account or store column with more than one value, the script stops and says so. Never add accounts together: one store's surplus hides another's stockout.
- **The date of the on-hand count.** It is passed as `--as-of` and the sales window ends on it. If the user hasn't said when on-hand was counted, you can still run the step 2 mapping check: `--detect-only` doesn't need `--as-of`, so leave it out. A full run without `--as-of` stops (exit 2) and says it needs the count date. Ask for the date in your one combined question, along with any mapping or date-order questions the mapping check raises. Don't take the date from the last sale in the export or from a file name (that may be the export date, not the count date).

Planning parameters. Ask for them in **one** combined question. Use the operator's values and never invent "industry standard" targets:

| Parameter | Flag | If not given |
|---|---|---|
| Vendor lead time (days) | per-SKU column, or `--default-lead-time` for SKUs whose cell is blank | SKUs show `NO_LEAD_TIME`, with no order qty. Ask. A default the operator gives is used only for blank cells and flagged `DEFAULT_LEAD_TIME(Nd)`. |
| Safety stock (days) | `--safety-days` | 0, tagged [ASSUMPTION] |
| Days to cover after delivery (order cycle) | `--cover-days` | 14, tagged [ASSUMPTION] |
| Velocity window | `--window-days` | 28 days ending on the on-hand count date, stated in the report |
| Dead-stock threshold | `--dead-days` | 30 days with no sales, [ASSUMPTION] |
| Slow-mover threshold (days of supply) | `--slow-dos` | 90, [ASSUMPTION] |

Optional per-SKU columns: unit cost (needed for PO dollars and dead-stock value), case pack (order multiple), minimum order qty (MOQ), vendor, open PO qty. MOQ is not a case pack: a quantity below the MOQ is flagged `BELOW_MOQ(n)` and left as calculated; whether to buy up to the minimum is the buyer's call. If the operator has a budget cap (cash is tight for most cannabis businesses), ask for it.

**Vendor is never guessed from brand.** Brand is often not who you buy from (a distributor sits in between). A SKU with a blank vendor is flagged `NO_VENDOR`; if it needs ordering, its line goes to `lines_needing_vendor` instead of a vendor's PO and is not in the PO total. Ask who supplies it. If the operator confirms brand = vendor for their store, pass `--vendor-from-brand`; those lines are flagged `VENDOR_FROM_BRAND` and listed in `assumptions`.

### 2. Mapping

Run `python3 <skill-dir>/scripts/replenish.py --sales <file> --onhand <file> --as-of <on-hand count date> --detect-only`. `<skill-dir>` is the folder that contains this SKILL.md. If the script can't be found or fails to run, stop and tell the user what failed. Never hand-compute the figures the script produces, and don't compare the files by hand either (no list of rows that differ, match, are missing or would pass).

Show the detected mapping in one line per file. `missing_required_columns` lists any required column it couldn't find. If a column is missing or `AMBIGUOUS` (e.g. both "On Hand" and "Available"), ask which one and pass `--map-sales field=Column` / `--map-onhand field=Column`. Alias hints are in `references/system-mappings.md`. If the export has product names but no SKU, map `sku=Product` and warn that name changes will split history.

### 3. Run

```
python3 <skill-dir>/scripts/replenish.py --sales <file> --onhand <file> --as-of <on-hand count date> --out-dir <dir> [params] [mappings]
```

Use the script's numbers as-is and don't recompute by hand. Copy every entry in `assumptions` into the report's assumptions list, and every `input_problems` line into Data gaps. If `warnings` says the last sale is days before the on-hand count date, tell the buyer and ask whether the sales export covers the full period: missing days understate velocity. Formulas and flag definitions are in `references/method.md`. Read it if the user asks how a number was calculated.

The script never silently drops, merges or fills in on-hand data:
- **Duplicate SKU rows** in the on-hand file: on-hand and open PO are summed. If the rows disagree on unit cost, case pack, MOQ, lead time or vendor, the SKU is flagged `CONFLICTING_ROWS(...)`, gets no order, and both values are in `input_problems`. Ask which is right, fix the file, rerun. An unreadable cell on one row is never outvoted by a readable one on another. If duplicate rows each show the same open PO, ask whether it is per bin or repeated for the SKU: if repeated, the sum double-counts it.
- **Open PO:** a blank open PO cell, or no open PO column, counts as 0 and is listed in `assumptions`. Ask whether anything is on order before the buyer acts on those lines.
- **Lead time text:** "7 days" and "2 weeks" are read as 7 and 14 days (and noted). Anything else, such as "7-10 days", or a lead time over 365 days, is flagged `BAD_LEAD_TIME` and gets no order. The default lead time is never used in its place.
- **Unreadable numbers:** NaN, inf and decimal commas such as `4,25` or `1.234,56` are never guessed. Each is listed in `input_problems` with its row, column and raw value; an unreadable sales units cell leaves that sales row out. US thousands separators such as `1,200` are read normally. A non-numeric or negative open PO (`BAD_OPEN_PO`) holds the SKU because it might already be on order. A case pack that is not a whole number above 0 (`BAD_CASE_PACK`, e.g. `2.5`) leaves the quantity unrounded. A non-numeric or negative unit cost (`BAD_UNIT_COST`) leaves the cost blank.
- **Negative numbers:** negative on-hand (`NEGATIVE_ONHAND`) holds the SKU with no order until the count is corrected. Negative sales units are returns (`RETURNS_IN_WINDOW`); if returns exceed sales for a SKU in the window, its velocity is 0 and it is flagged `NEGATIVE_NET_SALES`.
- **SKU spelling:** SKUs are matched ignoring case and spacing, so `e-case` in sales and `E-CASE ` on hand are one SKU, not a fake `DEAD` plus a fake `NO_ONHAND_RECORD`. The SKU is flagged `SKU_VARIANTS` and every spelling is in `input_problems`. Mention it so the exports get fixed.
- **Dates:** ISO dates and timestamps (`2026-09-29T14:03:00Z`, with or without seconds, fractions or an offset), `9/29/2026 2:03:15 PM`-style US dates with a 24-hour or AM/PM time, and month names (`Sep 29, 2026`) are all read. A timestamp is dated as written, never converted between time zones; `warnings` says when a zone is present. Slash dates are read as month/day. Day/month order is never guessed: if a date can only be day/month (`29/09/2026`), the script stops. Ask the user which order the export uses, then rerun with `--date-order dmy` (or `mdy`). If dates could be read either way (`03/09/2026`), `warnings` says so: ask whether the export uses US dates before using the numbers. Rows with an unreadable date are left out and counted in `warnings`: velocity may be understated.
- **Leading zeros:** SKUs that differ only by leading zeros (`00123` on hand, `123` in sales) are not matched, because the zeros may be real. Each pair is in `input_problems`, so don't report the on-hand one as unsold or the sales one as missing stock. Ask for exports with the SKU written the same way.
- `skus_held_for_review` lists SKUs held for a negative on-hand, an unreadable or negative open PO, an unreadable on-hand row among duplicate rows, or conflicting duplicate rows. It is not every SKU without an order because of a data problem: a SKU whose only on-hand cell is unreadable shows `NO_ONHAND_RECORD`, and a blank or unreadable lead time is in `skus_missing_lead_time`. Put all of them in the report so they aren't forgotten.

### 4. Sanity-check before recommending

Look at `replenishment.csv` for these and adjust **the recommendation, not the math**:
- `STOCKOUT(demand understated)`: zero on hand at the count, with sales in the last 7 days. The files don't show when it sold out. If the shelf was empty for part of the window, measured velocity understates demand. Say so, and ask the buyer when it ran out. Don't invent a sell-out date or a corrected number.
- `NEW_SKU`: first sale inside the window, and no sales in the earlier history the export covers. Velocity is over the days since that first sale. Treat it as provisional and ask whether the SKU really is new.
- `NEW_OR_SLOW`: first sale inside the window, but the export doesn't reach back before the window, so it could be a slow seller. Velocity is over the whole window. If it was on the shelf before the window, that rate is the right one: one or two sales in four weeks is slow, not understated. Only if the buyer says it launched on its first-sale date is the rate understated: say so, and don't recompute.
- `NO_SALES_SEEN`: stock on hand, no sales, but the export is shorter than the dead-stock threshold. Don't call it dead; ask for a longer sales export.
- Promo or holiday spikes: if a big one-day spike sits inside the window (4/20, Green Wednesday, a vendor day, a Labor Day sale), rerun with a `--window-days` that leaves it out (keep `--as-of` on the on-hand count date), or call it out. Ask the buyer whether the spike will repeat.
- `RETURNS_IN_WINDOW`: returns reduce net units. Note them.
- Open POs: a low days-of-supply SKU with a large open PO isn't a reorder. It's an "is the PO arriving on time?" question.

### 5. Report

Fill `assets/plan-template.md`, then `assets/po-draft-template.md` grouped by vendor with line and total cost. Lead with the bottom line: number of SKUs to reorder, total PO dollars, stockouts, and the dollar value tied up in dead stock. `dead_stock_cost_value` covers only dead SKUs with a unit cost. List `dead_stock_missing_cost` (SKU and units) next to it, so the figure isn't read as the full total. Follow `references/output-conventions.md` for labels.

## Before you reply

**Bad values and blanks.** Quote the raw cell (`'1,5'`, `NaN`, `inf`, `-3`) with its SKU and column, say what the script did with it, and ask for the right figure. Don't offer readings ("1.5 or 15?"), don't work out what a reading would give (days of supply, a line cost, a PO total), and don't fill it from another file.

**You never send.** Not by email, not in a vendor portal, and not later "if you give me the addresses or access". Say the buyer sends the PO, and mark it a draft.

**Your final reply must contain:**
- The on-hand count date you ran with and where it came from (the user). If they didn't give one, the question, and no order quantities.
- The PO draft by vendor with line and total cost, marked DRAFT, not sent; lines with no cost shown as such, not left out of the count.
- Every SKU with no order because of a data problem (`skus_held_for_review`, `NO_ONHAND_RECORD`, `skus_missing_lead_time`, `lines_needing_vendor`) and what's needed for each.
- Every `input_problems` line, with its SKU, column and raw value, including sales-file cells that only affect revenue.
- Every entry in `assumptions`, labelled as yours to confirm.

## Gotchas

- **SKU churn.** Cannabis products often get a new SKU per batch, strain drop, or package redesign. Two SKUs with near-identical names, where one stopped selling as the other started, are probably one product. Ask before combining them. Combining wrongly double-counts demand, and not combining shows a fake dead SKU plus a fake new SKU.
- **Velocity is not demand when you were out of stock.** See `STOCKOUT` above.
- **Aging and test validity.** Dead or slow stock may be near the end of its shelf life or past state retesting or label-date limits. Those rules are state-specific, so mark them **NEEDS VERIFICATION** rather than stating a limit. Recommend checking package and test dates on anything flagged `DEAD`.
- **Unit mismatch.** The sales export may count units (each) while on-hand is in grams for bulk or deli-style flower. Don't mix them. Ask for the conversion or exclude those SKUs.
- **Case packs round up.** Suggested qty is rounded up to the case pack. Say so when rounding meaningfully increases cash outlay.
- **Cash first.** If the PO total exceeds the budget, rank lines by days of supply (lowest first) and margin if cost and price are known, and show where the budget runs out. Don't cut lines silently.
- **Distributor/brand use.** Running this on retail account data means the "PO draft" is a *suggested order* to propose to the account's buyer. Label it that way, and run one account at a time.
- **Never send.** The output is a draft for the buyer. No emailing vendors and no submitting orders in any system.

## Example

User: "Here's our Dutchie sales for Aug–Sep and today's on-hand. Lead times are in the sheet. Keep 3 days safety. What do I order?"

Good output opens with: "3 SKUs to reorder, $4,620 across 3 vendors (Example Pines Distribution $1,680, Example Coast Extracts $1,980, Example North Farms $960). Live Resin Gelato has 0 on hand and last sold 9/28. If it was out of stock for part of the window, its 110-unit order is low. When did it run out? $350 at cost is tied up in the Sativa 5pk pre-rolls, which haven't sold since 8/20. Check package and test dates before discounting. Chocolate bar has no lead time or vendor, so it isn't ordered yet…". It then gives the assumptions (14-day cover and 30-day dead threshold are defaults, confirm), the SKU table, the PO draft by vendor, and data gaps.
