# Method: formulas and flags used by scripts/replenish.py

All figures are per SKU. "Window" = the `--window-days` days ending at `--as-of` (default: the last date in the sales data).

| Metric | Formula | Notes |
|---|---|---|
| Units sold (window) | Sum of units in the window, returns (negative units) included | Net of returns |
| Days measured | Window length, or days since first sale if the SKU first sold inside the window | Shorter for new SKUs → `NEW_SKU` |
| Units per day | Units sold ÷ days measured | Understated if the SKU was out of stock during the window |
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

## What the script does not do

- No seasonality model or trend projection. Velocity is a flat average. Adjust the window or call out known events instead.
- No built-in benchmarks or targets. Every threshold is an operator input or a labeled default.
- No price, margin, or compliance logic (e.g. purchase limits, state test-validity windows).
