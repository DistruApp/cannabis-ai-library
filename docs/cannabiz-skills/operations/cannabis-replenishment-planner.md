# Cannabis Replenishment Planner

Skill: [`cannabis-replenishment-planner`](../../../skills/cannabiz-skills/operations/cannabis-replenishment-planner/SKILL.md)

## What it does

Answers "what do I order this week?" A bundled script calculates units sold per day, days of supply, sell-through, reorder points and order quantities rounded to case packs, then groups the suggested order into a draft PO by vendor with total cost. It flags SKUs that sold out (where demand is understated), dead stock tying up cash, new SKUs and missing lead times. It never sends orders to vendors. Built for dispensary buyers and for brands or distributors planning their retail accounts.

## When to use it

- "What should I reorder this week?"
- "Which SKUs are about to stock out?"
- "What's sitting dead on the shelf?"
- Building a PO draft from a POS export such as Dutchie, Flowhub or Treez
- A brand or distributor planning replenishment from a retailer's sell-through data

## How to use it

- **Inputs:** a sales export by SKU (date, product, units, revenue), current on-hand by SKU, vendor lead times, and safety stock days. Optional: open POs, unit cost and case pack sizes.
- **Tools / connectors:** none. Works from uploaded files and needs an assistant that can run Python for the bundled calculator.
- **Works in:** Claude or any LLM with code execution.
- **Safeguards:** every default the user did not set (sales window, days of cover, dead stock threshold) is listed as an assumption to confirm. It doesn't use invented industry targets.

## Example

**Input:** two months of POS sales, today's on-hand and lead times, with 3 days of safety stock.

**Output:** 3 SKUs to reorder for 4,620 dollars across 3 vendors. A sold-out live resin cart is flagged because its order is probably low. 350 dollars at cost is tied up in pre-rolls that have not sold in 40 days. One SKU has no lead time or vendor, so it is not ordered yet. The PO draft by vendor follows.
