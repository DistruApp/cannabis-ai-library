# Cannabis Harvest Yield Analysis

Skill: [`cannabis-harvest-yield-analysis`](../../../skills/cannabiz-skills/operations/cannabis-harvest-yield-analysis/SKILL.md)

## What it does

Shows a cultivator which rooms and strains produce the most dry weight per square foot, plant and light, and what each gram costs to grow. It does not look at sales prices, revenue or profit. A bundled script calculates wet to dry loss, dry yield per plant, per square foot of canopy and per light, the split between top flower, smalls and trim, any weight that is not accounted for, and cost per dry gram when costs are provided. It ranks strains and rooms and flags unusual batches using the grower's own numbers. It doesn't invent industry benchmarks. A batch with a missing or zero weight, such as one still curing, is left out of the figures that need that weight, and the report says how many batches each figure covers. Duplicate harvest IDs are flagged, not merged.

## When to use it

- "Which strains or rooms are performing best?"
- "Why did this harvest come in light?"
- "What's our cost per gram?"
- Uploading a harvest log or a traceability harvest export and asking for a yield report

## How to use it

- **Inputs:** per harvest batch: strain, room, harvest date, plant count, canopy square feet, wet and dry weight, and the dry breakdown. Optional: lights per room and room cost per cycle. Mixed grams and pounds are fine as long as the unit is stated.
- **Tools / connectors:** none. Works from uploaded files and needs an assistant that can run Python for the bundled calculator.
- **Works in:** Claude or any LLM with code execution.

## Example

**Input:** 8 Q3 harvests with a goal of 25 g per square foot.

**Output:** 197.5 lb dry in total. The best room is at 28.3 g per square foot, above goal, and one room is at 15.3 g per square foot with the highest cost per gram. Four batches have unrecorded weight that needs a record before the harvests are closed. A per-batch table, rankings, the anomaly rule used and data gaps follow.
