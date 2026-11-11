---
name: cannabis-harvest-yield-analysis
description: Analyze cannabis harvest results by batch, strain, and room. Covers wet-to-dry loss (dry-down), dry yield per plant / per square foot of canopy / per light, A-flower vs. smalls vs. trim mix, unaccounted weight, and cost per gram, with anomalies flagged against the grower's own history. Use when a licensed cultivator shares harvest weights, a harvest log, or a traceability harvest batch export and asks which strains or rooms perform best, why a harvest came in light, what their cost per gram is, or for a harvest/yield report, even if they don't say "yield analysis." Not for inventory reconciliation against Metrc, manufacturing/extraction yields or batch costing, or forecasting future harvest schedules.
license: MIT
metadata:
  version: "1.0"
  category: cultivation
  risk-level: medium
  last-compliance-review: "2026-10-16"
---

# Harvest yield analysis

Shows a head grower or operations lead which rooms and strains actually produce, where weight goes missing between wet and dry, and what each gram costs. All math runs in `scripts/yield.py`. Comparisons are only ever against the operator's **own** batches or targets, never an "industry average."

## Workflow

```
- [ ] 1. Collect harvest data and confirm units
- [ ] 2. Confirm the column mapping (--detect-only)
- [ ] 3. Run scripts/yield.py
- [ ] 4. Interpret: rankings, dry-down, breakdown gaps, cost
- [ ] 5. Write the report from assets/report-template.md
```

### 1. Collect data

One row per harvest batch. **Required:** batch/harvest name, wet weight, dry weight. **Strongly useful:** strain, room, harvest date, plant count, canopy sq ft, light count, dry breakdown (A flower, smalls/B, trim, waste), cycle cost.

Ask in one message for whatever's missing that the user's question needs. For example, "best room per sq ft" needs canopy, and "cost per gram" needs a cost figure. If the user only has some fields, run with what's there. The script leaves metrics blank rather than guessing.

**Units:** a file may mix g and lb row by row. If there's no unit column, ask for the unit and pass `--weight-unit`. The script refuses to assume one. If there is a unit column, a blank unit cell skips that row unless `--weight-unit` is also given, in which case the row is filled from it, flagged `UNIT_FROM_WEIGHT_UNIT_ARG` and listed in `input_problems`. Confirm those rows with the operator. Ask whether "dry weight" means **bucked/trimmed dry** or **total dry plant material**, because that changes dry-down and mix percentages.

**Costs:** use only costs the operator provides (cycle cost per batch, or cost per sq ft × canopy, which you calculate and show). If they give a monthly facility cost, ask how they allocate it to rooms before using it, and list the allocation as an **[ASSUMPTION]**.

### 2. Mapping

`python3 <skill-dir>/scripts/yield.py --harvests <file> --detect-only`. `<skill-dir>` is the folder that contains this SKILL.md. If the script can't be found or fails to run, stop and tell the user what failed. Never hand-compute the figures the script produces.

Show the mapping in one line. Fix missing or AMBIGUOUS columns with `--map field=Column`. Alias hints are in the `ALIASES` table at the top of the script and in the harvest-fields section of `references/system-mappings.md`. For Excel files, export to CSV first.

### 3. Run

```
python3 <skill-dir>/scripts/yield.py --harvests <file> --out-dir <dir> [--weight-unit g|lb|kg|oz] [--map ...]
```

Use the script's numbers. Report every `input_problems` line.

The script never drops, merges or fills in a number silently:
- A batch missing an input is left out of the ratios that need it, in both the numerator and the denominator. Dry-down needs wet and dry weight. Per plant, per sq ft and per light need dry weight and that count. Each aggregate carries a `coverage` line (e.g. "3 of 4 batches; 1 excluded: H3 (no dry weight)"), and `totals_coverage` does the same for the file totals. Quote the coverage whenever it is not all batches.
- A dry weight of 0, or a zero or negative count, is reported as a data problem (`ZERO_DRY`, `BAD_DRY`, `BAD_WET`) and never divided by.
- An unreadable number (NaN, inf, a decimal comma such as `4,25` or `1.234,56`) or a negative breakdown weight or cycle cost is listed in `input_problems` with its row, column and raw value, flagged `BAD_<FIELD>` (`BAD_WET` / `BAD_DRY` for the weights), and treated as blank. Ask the operator for the right figure; never reinterpret it yourself. US thousands separators such as `25,000` are read normally.
- Per-batch `flags` also carry `MISSING_WET`, `MISSING_DRY`, `DRY_EXCEEDS_WET`, `DUPLICATE_ID` and `UNIT_FROM_WEIGHT_UNIT_ARG`, and `excluded_from` lists the metrics that batch was left out of.
- Duplicate harvest IDs are kept as separate rows, counted in totals, flagged `DUPLICATE_ID` and listed in `duplicate_harvest_ids`. Ask the operator whether one is a re-entry. If it is, remove it and rerun.

### 4. Interpret

When a number looks off, read `references/interpreting-yield.md` for the data and process checks to run before drawing cultivation conclusions.

- **Rankings** (`by_strain…`, `by_room…`): ranked by dry g per sq ft, the fairest comparison across room sizes. Mention per plant and per light when they tell a different story. Strain and room are often confounded (one strain per room). Say so instead of crediting the strain.
- **Dry-down %** = 1 − dry/wet. Compare batches with each other. A batch well outside the operator's usual range points to a weighing, timing, or recording issue (wet weight taken late, dry weight taken before cure was complete, or units mixed up). Check those before blaming genetics.
- **Breakdown sum-check:** `UNACCOUNTED` means A + B + trim + waste < dry weight. That weight is unrecorded and needs an explanation (unrecorded waste, samples, a missing bin, a weighing error). `PARTS_EXCEED_DRY` means a data-entry error. `INCOMPLETE_BREAKDOWN` means one or more breakdown cells are blank. The blank part shows blank, not 0%, and the unaccounted weight includes whatever that part weighs. Cost per flower gram is left blank when A or B flower is blank.
- **Anomaly flags** use one stated rule: outside 1.5 × IQR of this file's own batches, which needs at least 4. With few batches the fences are tight. Present flags as "worth a look," not as failures, and always state the rule.
- **Cost per gram:** per dry gram and per sellable flower gram (A + B). Trim value isn't credited unless the operator gives a trim price. If they do, show it separately.
- If the operator gives targets (e.g. "we budget 25 g/sq ft"), compare against them and label them as **their target**.

### 5. Report

Fill `assets/report-template.md` and follow `references/output-conventions.md`. Lead with the bottom line: total dry output, best and worst room/strain per sq ft, the biggest unexplained weight gap, and cost per gram if available.

## Gotchas

- **No outside benchmarks.** Never write "typical yield is X g/sq ft" or "normal dry-down is Y%." Published figures vary widely by method and aren't verified here. Compare against the operator's own history or stated targets. If there's no history, report the values without a benchmark and say that more batches are needed to judge.
- **Pound conversions:** 1 lb = 453.592 g. The script converts per row, so mixed-unit files are fine as long as each row's unit is right.
- **Traceability tie-out:** harvest weights in this analysis should match the wet weight, waste, and package records in the state traceability system. Which weights must be recorded, when, and how is state-specific: **NEEDS VERIFICATION** with the state's rules. If the user's numbers differ from their traceability harvest records, point them to the `cannabis-traceability-reconciliation` skill and don't pick a winner.
- **Unaccounted weight is a compliance signal** as well as a yield one. Don't just call it "shrink." Recommend finding the record (waste log, sample, packaging) before closing the harvest.
- **Partial harvests** (still curing, not yet bucked) produce misleading dry-down and mix numbers. The script leaves a batch with a blank dry weight out of dry-down, dry totals and every per-plant / sq ft / light figure, and says so in `coverage`. Label it as still curing in the report.
- **Plant count:** use plants harvested, not plants started. Ask if it's unclear.

## Example

User: "Q3 harvests attached. Which rooms are pulling their weight and what's our cost per gram? Our goal is 25 g/sq ft."

Good output opens with: "8 harvests, 197.5 lb dry. Flower 1 (Blue Dream) leads at 28.3 g/sq ft, above your 25 g/sq ft goal. Flower 4 (Papaya, 1 batch) is at 15.3 g/sq ft with the highest cost per dry gram ($2.70 vs. $1.36–$1.63 elsewhere). 4 batches have unrecorded weight (125–400 g each) that needs a record before the harvests are closed…" It follows with the per-batch table, rankings with the strain/room confound noted, the anomaly rule, and data gaps.
