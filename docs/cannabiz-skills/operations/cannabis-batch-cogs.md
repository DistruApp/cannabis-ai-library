# Cannabis Batch COGS

Skill: [`cannabis-batch-cogs`](../../../skills/cannabiz-skills/operations/cannabis-batch-cogs/SKILL.md)

## What it does

Tells a manufacturer what a batch or SKU really costs. A bundled script adds up every input (flower, biomass, distillate, terpenes, hardware, packaging, labels), labor, overhead and lab testing, then shows the line by line cost, cost per finished unit, the cost of yield shortfalls, and a sensitivity table on the top three cost drivers. It refuses to fill in missing rates silently, and it stops to ask "price per what unit?" when a weight or volume input has no price unit. An assumed value must be a number the user chooses: it is listed for them to confirm, and any line built on it (such as overhead set as a % of materials) is marked as an assumption too. It also stops when two BOM columns could both be the price, asks whether a column headed just "Cost" is the price per unit or the line total, and never writes its report over the BOM file.

## When to use it

- "What does this batch really cost per unit?"
- "Can you cost this BOM?"
- "What's the real per-jar cost on this run?"
- "Why did our unit cost go up?"
- Needing a cost per unit figure for pricing a vape, edible, pre-roll or extract SKU

## How to use it

- **Inputs:** the bill of materials with quantities and input costs, expected and actual units produced, labor hours and rate, the overhead method or rate, and testing cost per batch.
- **Tools / connectors:** none. Works from uploaded files and needs an assistant that can run Python for the bundled calculator.
- **Works in:** Claude or any LLM with code execution.
- **Limits:** this is operational COGS. 280E tax treatment and inventory capitalization need a CPA. A line weighed in one kind of unit and priced in another (for example oil in mL priced per gram) has to be restated in one kind in the BOM; the calculator does not apply a density.

## Example

**Input:** a vape cartridge batch BOM, 14 labor hours at 24 dollars, overhead at 35 dollars per labor hour, a 425 dollar lab fee, 500 units expected and 492 produced.

**Output:** 9.51 dollars per cart and 4,680.75 dollars per batch. Distillate is 46 percent of cost, the 8 missing units added 0.15 dollars per cart, and each 10 percent move in distillate price changes unit cost by about 0.44 dollars. Line by line and sensitivity tables follow.
