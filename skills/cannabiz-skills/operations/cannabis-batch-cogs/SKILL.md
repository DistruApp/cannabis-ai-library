---
name: cannabis-batch-cogs
description: >-
  Calculate the true cost of a cannabis manufacturing or processing batch: bill-of-materials roll-up (flower, biomass, distillate, terpenes, hardware, packaging, labels), labor, overhead, and testing, giving cost per batch and per finished unit, yield variance against expected output, and sensitivity on the biggest cost drivers. Use when a licensed manufacturer, processor, extractor, packager, or pre-roll/edible/vape producer asks what a batch or SKU really costs, wants a BOM costed, asks why unit cost went up, or needs a cost-per-unit figure for pricing, even if they don't say "COGS." Not for 280E tax treatment or inventory capitalization (CPA territory), cultivation harvest yield and cost per gram, wholesale price sheets, or traceability reconciliation.
license: MIT
metadata:
  version: "1.0"
  category: manufacturing-finance
  risk-level: medium
  last-compliance-review: "2026-10-16"
---

# Batch COGS

Gives a production manager or controller a defensible cost per unit for one batch: every line shown, every assumed rate called out, and the shortfall in output priced. The roll-up runs in `scripts/cogs.py`, which **refuses to fill in any rate the operator didn't give**.

**Scope:** operational cost of goods made. How these costs are treated for tax (IRC §280E, inventory capitalization) is out of scope and needs a CPA. Say so in one line in the report, and don't explain tax law.

## Workflow

```
- [ ] 1. Collect the BOM and batch parameters
- [ ] 2. Confirm the BOM column mapping (--detect-only)
- [ ] 3. Run scripts/cogs.py; resolve BLOCKED inputs with the operator
- [ ] 4. Interpret: cost structure, yield variance, sensitivity
- [ ] 5. Write the report from assets/report-template.md
```

### 1. Collect inputs

**BOM (CSV):** one row per component *actually consumed* in this batch: component, quantity, unit, unit cost, and the unit the price is quoted in (e.g. biomass bought at $/lb but weighed in kg). The price unit is required for weight and volume lines. Use actual consumption, not the recipe, when the operator has it. Overfill and fill loss belong in the quantity.

**Batch parameters**, all needed, asked for in **one** message:
- Finished units produced (actual) and, if known, expected units
- Direct labor hours and loaded hourly rate
- Overhead method, **one** of: $ per batch, $ per labor hour, or % of materials. Ask how they normally allocate. Never pick a method for them. Pass a percentage as a whole number: `--overhead-pct-materials 12` means 12%. If the operator says "0.12" or "12 points", confirm they mean 12%.
- Testing cost charged to this batch (lab fees, retests)

If the operator says a cost really is zero, pass `0`. If they want to proceed without a number, pass it with `--assume key=value` (for a BOM line: `cost:<component>=12` or `cost_uom:<component>=lb`). It's then tagged **[ASSUMPTION]** everywhere and listed at the top of the report. Never estimate a market price for an input (e.g. "distillate usually costs…").

Where inputs come from: ERP item costs and production records, purchase invoices, payroll, lab invoices. Input lot numbers and harvest names in the component name make the report traceable. Keep them.

### 2. Mapping

`python3 <skill-dir>/scripts/cogs.py --bom <file> --detect-only`. `<skill-dir>` is the folder that contains this SKILL.md. If the script can't be found or fails to run, stop and tell the user what failed. Never hand-compute the figures the script produces, and don't compare the files by hand either (no list of rows that differ, match, are missing or would pass).

Show the mapping in one line. Fix missing or AMBIGUOUS columns with `--map field=Column` (fields: component, qty, uom, unit_cost, cost_uom). For Excel files, export to CSV first.

### 3. Run

```
python3 <skill-dir>/scripts/cogs.py --bom <file> --batch-name <name> --units-produced N [--expected-units N] \
  --labor-hours H --labor-rate R --overhead-per-labor-hour X | --overhead-per-batch X | --overhead-pct-materials P \
  --testing-cost T [--assume key=value ...] --out-dir <dir>
```

Always run the script, even when you can already see the problem in the file: it lists every problem, not just the first. Exit code 2 with `"status": "BLOCKED"` lists exactly what's missing or malformed. Take that list back to the operator. Don't fill it in yourself. Report the script's numbers as-is.

- `cost_uom:<component>` in `missing_inputs` means a weight or volume line has a price but no price unit. Ask "price per what unit?" (per g, per lb, per kg). Never guess it from the quantity unit.
- Unreadable numbers block the run: NaN, inf, a decimal comma such as `4,25` or `1.234,56`, and negative quantities or costs. Each is listed in `input_problems` with its row, column and raw value. Ask the operator for the right figure; never reinterpret it yourself (`4,25` could be 4.25 or 425). A return or correction belongs netted into the quantity consumed. US thousands separators such as `1,200` are read normally.
- `input_problems` also appears on OK runs. It lists things that did not block the run but the operator should see: fully blank rows that were skipped, count lines with a blank price unit that were read as price per each, and an `--overhead-pct-materials` value between 0 and 1 (read as that many percent, so 0.12 means 0.12%, not 12%). Put each one under Data gaps in the report, and confirm the overhead percentage with the operator before reporting.
- Numeric flags and `--assume` values must be numbers; flags can't be negative and `--assume` values must be greater than 0. A bad value stops the script with a message. Pass a confirmed zero as the flag itself.
- `--expected-units` must be greater than 0. Leave it out if there is no expected count.

### 4. Interpret

- **Cost structure:** materials / labor / overhead / testing as $ and % of total. Name the top 3 lines. They usually drive every pricing conversation.
- **Yield variance:** actual vs. expected units, and the cost of the shortfall per unit (`cost_of_shortfall_per_unit`). Common causes to check: fill loss, rejects at QC, hardware defects, units pulled for testing samples, miscounts. Use the operator's expected yield only, never an outside "standard."
- **Sensitivity:** cost per unit at ±10% / ±20% on each of the top 3 drivers, one at a time. Use it to answer "what if distillate goes up?" Say clearly that the drivers are varied separately.
- **Comparisons:** compare against the operator's previous batches or standard cost if they provide them. Otherwise present the result alone.

### 5. Report

Fill `assets/report-template.md` and follow `references/output-conventions.md`. Lead with cost per unit, total batch cost, the biggest driver, and the yield gap in dollars. For deeper context on the cost elements, read `references/cost-elements.md`.

## Before you reply

**Bad values and blanks.** Quote the raw cell (`'50,5'`, `NaN`, a blank price unit) with its row and column and ask for the right figure. Don't offer readings ("$4.25 or $425?"), don't work out what a reading would cost, and don't fill it from another line.

**Missing inputs.** Ask for them; don't give a partial total or cost per unit you worked out yourself, not even a materials subtotal. If the operator says "use whatever" without a number, ask for a number they choose; you never pick one.

**You never update or send anything.** Not the ERP standard cost, not an email to the team, and not later "if you give me access". Say the user does it, and give a draft message they can send.

**Your final reply must contain:**
- When BLOCKED: the word **BLOCKED** in the first line, every `missing_inputs` item, and every `input_problems` line (skipped blank rows, count lines read as per each, unreadable or negative numbers), each with its row, column and raw value, then one combined question. No cost figures.
- When OK: cost per unit and total batch cost first, then the line-by-line roll-up including labor, overhead and testing, the yield variance in units and $ per unit, the ±10%/±20% sensitivity on the top 3 drivers, assumptions (each `[ASSUMPTION]` listed), Data gaps (every `input_problems` line), and the one-line CPA note on 280E.

## Gotchas

- **Price unit ≠ quantity unit.** Biomass weighed in kg but bought at $/lb, or distillate in g at $/kg, is the most common 1,000× or 2.2× error. Always fill the `cost_uom` column. The script converts within weight, volume, or count, and blocks mixed kinds (e.g. mL of oil priced per g) until the operator gives a density or conversion. A blank price unit on a weight or volume line blocks the run. On a count line it is read as price per each and listed in `input_problems`, so check nothing is priced per case.
- **Assumptions carry through.** When overhead is a % of materials and a material cost or price unit is assumed, the overhead line is tagged ASSUMPTION too. The same applies to overhead per labor hour when labor hours are assumed.
- **Input costs should carry their own history.** Biomass from the operator's own harvest has a cost from cultivation. Ask whether they want the transfer cost they use internally, or the cultivation cost per gram (the `cannabis-harvest-yield-analysis` output). Don't mix the two across batches.
- **Recipe vs. actual.** A recipe BOM understates cost when there's fill loss or rework. Label which one was used.
- **Units produced** means sellable finished units after QC rejects. Ask if rejects and lab sample units are included.
- **Testing cost** is often charged per batch, so small batches carry a much higher per-unit testing cost. Call this out when batch sizes vary.
- **No tax conclusions.** Don't say which costs are "deductible" or "capitalizable" under 280E. Flag it for the CPA.

## Example

User: "What did our Gelato cart batch GEL-CART-1003 really cost per unit? BOM attached. 14 labor hours at $24 loaded, we put overhead at $35 per labor hour, lab was $425. We expected 500 carts and got 492."

Good output opens with: "$9.51 per cart ($4,680.75 batch). Distillate is 46% of cost ($2,146.25), hardware 20%. Filling 492 instead of 500 added $0.15 per cart. Each 10% move in distillate price moves unit cost about $0.44…" It follows with the line-by-line table, sensitivity table, assumptions (none), data gaps, and a one-line note that 280E treatment needs CPA review.
