# Method: formulas and flags used by scripts/replenish.py

All figures are per SKU. "Window" = the `--window-days` days ending at `--as-of`, the date of the on-hand count (required). If the last sale in the export is more than 1 day before it, `warnings` in summary.json says so.

| Metric | Formula | Notes |
|---|---|---|
| Units sold (window) | Sum of units in the window, returns (negative units) included | Net of returns |
| Days measured | Window length, or days since first sale if the SKU first sold inside the window | Shorter for new SKUs → `NEW_SKU` |
| Units per day | Units sold ÷ days measured | Understated if the SKU was out of stock during the window. 0 if net units are negative (`NEGATIVE_NET_SALES`) |
| Sell-through % | Units sold ÷ (units sold + ending on hand) × 100 | Period sell-through. Beginning inventory isn't needed. |
| Days of supply | On hand ÷ units per day | "no sales" when velocity is 0 |
| Reorder point | Units per day × (lead time + safety days) | Reorder when on hand + open PO ≤ reorder point |
| Suggested order qty | ceil(units per day × (lead + safety + cover days) − on hand − open PO), rounded **up** to case pack | 0 if above the reorder point |
| Order cost | Suggested qty × unit cost | Blank if no cost given |
| Dead-stock value | On hand × unit cost for `DEAD` SKUs | At cost, not retail |

## Flags

| Flag | Condition | What it means for the buyer |
|---|---|---|
| `REORDER` | At/below reorder point and qty > 0 | On the PO draft |
| `STOCKOUT(demand understated)` | On hand ≤ 0 and sales in the last 7 days | Real demand is higher than measured. Consider ordering more. |
| `STOCKOUT` | On hand ≤ 0, sales in window but not in the last 7 days | Out of stock for at least a week |
| `DEAD(no sales Nd+)` | On hand > 0 and no sale in the last `--dead-days` | Cash tied up. Check shelf-life and test dates. |
| `SLOW` | Days of supply > `--slow-dos` | Overstocked relative to velocity |
| `NEW_SKU(Nd of history)` | First sale inside the window | Provisional velocity |
| `NO_LEAD_TIME` | Selling but no lead time available | Can't compute a reorder point. Ask. |
| `NO_ONHAND_RECORD` | In sales but not in on-hand file | Mapping or SKU-churn issue. Investigate. |
| `RETURNS_IN_WINDOW(n)` | Negative units in window | Net velocity reduced |
| `DEFAULT_LEAD_TIME(Nd)` | Lead time cell blank, `--default-lead-time` used | Confirm the real lead time with the vendor |
| `BAD_LEAD_TIME` | Lead time cell not readable as days or weeks (e.g. "7-10 days") | No order until a lead time in days is given. The default is not used. |
| `NO_VENDOR` | Vendor cell blank (and `--vendor-from-brand` not passed) | Line kept off the vendor PO and listed under `lines_needing_vendor`. Ask who supplies it. |
| `VENDOR_FROM_BRAND` | Vendor blank, filled from brand because the operator confirmed brand = vendor | Listed in assumptions |
| `CONFLICTING_ROWS(field)` | Duplicate on-hand rows for the SKU disagree on unit cost, case pack, lead time or vendor | No order until the operator says which value is right |
| `BAD_OPEN_PO` | Open PO cell is not a number, or is negative | No order: the SKU may already be on order |
| `BAD_CASE_PACK` | Case pack is not a positive number | Quantity not rounded to a case pack |
| `BAD_UNIT_COST` | Unit cost is not a number, or is negative | Order cost blank |
| `BAD_ONHAND_ROW(row n)` | One of several on-hand rows for the SKU has an unreadable quantity | No order until fixed |
| `NEGATIVE_ONHAND` | An on-hand cell for the SKU is negative | No order, sell-through or days of supply until the count is corrected |
| `NEGATIVE_NET_SALES(n)` | Returns exceed sales for the SKU in the window | Velocity set to 0, not negative. Check the returns. |

## Duplicate on-hand rows

When the on-hand file lists a SKU more than once (e.g. two rooms or two bins), on-hand and open PO are summed across the rows. Unit cost, case pack, lead time and vendor are used only when the rows agree or only one row has a value. Otherwise the SKU is flagged `CONFLICTING_ROWS` and both values are reported.

## What the script does not do

- No seasonality model or trend projection. Velocity is a flat average. Adjust the window or call out known events instead.
- No built-in benchmarks or targets. Every threshold is an operator input or a labeled default.
- No price, margin, or compliance logic (e.g. purchase limits, state test-validity windows).
