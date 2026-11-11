---
name: cannabis-traceability-reconciliation
description: Reconcile cannabis inventory between the state traceability system (Metrc, BioTrack, or a state-built system) and a physical count or ERP/POS export, then produce a discrepancy report with likely causes and draft corrective actions. Use when a licensed cannabis operator says their count doesn't match Metrc, needs a month-end or pre-audit inventory reconciliation, has package variances, missing or extra package tags, product on hand that isn't showing in Metrc (or the reverse), unit-of-measure mismatches, or uploads a Metrc/BioTrack package export alongside a count sheet, or asks how to fix an inventory variance in Metrc (it finds the cause first and drafts adjustments; it never submits them), even if they don't say "reconciliation." Not for bank, accounting, or sales-tax reconciliations.
license: MIT
metadata:
  version: "1.0"
  category: compliance-traceability
  risk-level: high
  last-compliance-review: "2026-11-11"
---

# Traceability reconciliation

Turns two inventory lists that don't agree into a report an inventory or compliance manager can act on today. Every variance is sized, classified, and given a likely cause and a next step. Adjustments are **drafted, never submitted**.

## Workflow

Copy this checklist and work through it:

```
- [ ] 1. Jurisdiction gate
- [ ] 2. Identify the two sources and confirm the column mapping
- [ ] 3. Run scripts/reconcile.py
- [ ] 4. Investigate and classify each variance
- [ ] 5. Draft actions (no submissions)
- [ ] 6. Write the report from assets/report-template.md
```

### 1. Jurisdiction gate

Read `references/jurisdiction-gate.md`. You need state, license type, and traceability system before saying anything about adjustment reasons, reporting deadlines, or documentation requirements. Look up the state in `references/state-profiles.md`. If those are missing, ask once. The math in steps 2–4 doesn't depend on them, so you can run it while you wait for an answer.

### 2. Sources and mapping

You need exactly two lists that share a package tag:
- **System side:** traceability export (active packages) as of a stated date and time.
- **Count side:** physical count sheet, or ERP/POS on-hand export, as of the *same* point in time.

Ask for the as-of timestamp of each. A morning Metrc export against an end-of-day count produces false variances from the day's sales and transfers. Also ask what the count covered (license, rooms, product types). If the timestamps differ or are unknown, or the count covered only part of the inventory, label every result **PROVISIONAL**: packages outside the counted scope are scope gaps, not losses, and a time gap needs the sales, transfers and waste between the two times before any shortage means anything.

Run `python3 <skill-dir>/scripts/reconcile.py --system <file> --count <file> --detect-only` and show the user the detected mapping in one line per file. `<skill-dir>` is the folder that contains this SKILL.md. If the script can't be found or fails to run, stop and tell the user what failed. Never hand-compute the figures the script produces, and don't compare the files by hand either (no list of rows that differ, match, are missing or would pass).

If the script stops on a missing, repeated or AMBIGUOUS column, that isn't a failure: it's a question for the operator. Ask which column to use and wait for the answer. Don't pick one yourself or compute anything until they choose, then pass `--map-system field=Column` or `--map-count field=Column`. Column alias hints are in `references/system-mappings.md`.

Tolerance: default is **0** (report everything). A tolerance that isn't a plain number of 0 or more ("1,5", "1_000", NaN, a negative) stops the run with a usage error. Only set `--tolerance-g` / `--tolerance-each` if the operator gives you their own internal threshold. Never use a "typical" or state threshold you can't cite.

If the files are Excel, export each sheet to CSV first. If they're PDFs, extract the table and show the user the first rows to confirm before running.

### 3. Run

```
python3 <skill-dir>/scripts/reconcile.py --system <file> --count <file> --out-dir <dir> [mappings] [tolerances]
```

Use the script's numbers as-is. Don't recompute differences by hand. Statuses: `MATCH`, `WITHIN_TOLERANCE`, `SHORT_IN_COUNT`, `OVER_IN_COUNT`, `IN_SYSTEM_NOT_COUNTED`, `COUNTED_NOT_IN_SYSTEM`, `UOM_MISMATCH`, `UNKNOWN_UOM`, `MISSING_UNIT`, `DUPLICATE_CONFLICT`, `BAD_QUANTITY`, `INVALID_NUMBER`, `TAG_SCIENTIFIC_NOTATION`. Read the `notes` column too: it carries tag near-matches, unit conversions, small differences after a conversion, default units used and summed duplicates. Also report every line in `input_problems` (duplicate tags, blank tags, blank units, blank or invalid quantities).

- **Duplicate tags.** Rows with the same tag are summed only when every quantity is a number, no two rows are identical, and the units match or convert (weight with weight, each with each). The note and `input_problems` say how many rows were summed and whether they were converted to g. Identical rows (same quantity and unit) are a possible copy-paste double entry, so they are never summed: summing them could turn a real shortage into a match. They get `DUPLICATE_CONFLICT`, like any other set that can't be combined, with each row's quantity and unit listed, and aren't compared. Ask the counter whether they are separate counts, have the file corrected, and rerun.
- **Bad numbers.** `BAD_QUANTITY` means the quantity cell is blank. `INVALID_NUMBER` means it holds something that isn't a usable quantity: text, NaN or inf, a negative number, a currency symbol, a decimal comma ("1,5", "1.234,5"), or a single comma group with no decimal point ("1,234", which is 1234 in US format but 1.234 in European format). Unambiguous US thousands separators ("1,234.5", "1,234,567") are read normally. The script never guesses what a decimal comma means. The row isn't compared or put in any total, and `input_problems` gives the row, column and raw value. Ask the file's owner to correct the cell and rerun.
- **Tags in scientific notation.** A numeric tag that Excel turned into something like `1.23457E+23` or `1.23457E23` has lost its real digits, and two packages can end up with the same value. The script never matches, merges or totals such a row: it gets its own `TAG_SCIENTIFIC_NOTATION` row, and `input_problems` gives the file, row, column and raw value. Ask for a re-export with the tag column formatted as text, then rerun.
- **Blank units.** A blank unit is never copied from the other file. The package gets `MISSING_UNIT` and isn't compared. Only if the operator tells you the unit for that file, rerun with `--default-count-unit <unit>` or `--default-system-unit <unit>`. The default fills each blank cell before duplicate rows are combined; every package that used it says so in its notes, and `summary.json` records it under `default_units`. Say so in the report's assumptions.

### 4. Investigate and classify

For each non-matching row, assign a **likely cause** from `references/variance-causes.md` and a confidence: **Explained** (evidence in the files), **Probable** (fits the pattern, needs one check), or **Unexplained**. Look for patterns before treating rows one at a time: a single counter, room, product type, or date accounts for most real-world variances.

Evidence you can use: item type, unit, room, counter initials, the size of the gap relative to package weight, and any extra files the user gives you (sales, transfers, waste logs, lab sample records). If a cause needs data you don't have, name the file that would confirm it.

### 5. Draft actions

For each variance: the physical re-check to do, the record to find, and whether an adjustment in the traceability system **may** be needed. For adjustments:
- Mark them **DRAFT, not submitted**. For an Illinois dispensary, also mark each one "do not post until IDFPR approves" (see Gotchas).
- Don't choose a reason code unless the operator supplies their state's list. In Metrc it comes from the state's adjustment-reasons list (the API exposes `GET /packages/v2/adjust/reasons`). Otherwise write `reason: select from your state's list`.
- Any documentation, notification, or timing requirement for adjustments is **NEEDS VERIFICATION** unless `references/state-profiles.md` cites a primary source for it. Carry the profile's own verification label with it.
- Never propose an adjustment just to make the numbers match. An unexplained variance stays open, and you recommend escalating it.

### 6. Report

Fill `assets/report-template.md`. Put the state's notification deadline(s) at the very top as a decision for compliance today (see Gotchas). Then lead with the bottom line: how many packages are listed and how many were quantity-compared (`packages_quantity_compared`; `packages_compared` counts every listed tag, including ones that couldn't be compared), how many are off, the net variance, both gross figures under their own labels (`gross_variance_all_compared` and `gross_variance_outside_tolerance`) in grams and units, and the top 3 patterns. Follow `references/output-conventions.md` for labels and the sign-off block.

## Before you reply

**Bad values and blanks.** Quote the raw cell (`'889,1'`, `NaN`, a blank unit) with its tag, file and column, say it isn't compared or in any total, and ask for it to be corrected and the script rerun. Don't offer readings ("probably 889.1 g"), don't work out what a reading or an assumed unit would give ("that would make the net -23.8 g", "if it's grams it matches"), and don't take a value or unit from the other file.

**You never submit or adjust anything** in Metrc or any state system, not now and not "if you give me access". Say adjustments are drafts the operator reviews and enters.

**Without files or a state** (e.g. "we're off 2 lb, how do we fix it in Metrc?"): ask in one message for the state and license type, the traceability export and the count or ERP file with the as-of time of each. Say you'll find which packages are off and why before anything is adjusted. Don't give adjustment steps, reason codes or deadlines yet.

**Your final reply must contain:**
- The compliance decision for today and the jurisdiction block, as in step 6.
- The script's net variance and both gross figures with their labels, with the packages left out of the net listed next to them.
- The variance table: tag, item, system and count quantity, difference, status, likely cause, confidence. Name tags by at least their last 4 characters (e.g. …0011), and for a near-match name both tags.
- Draft actions marked **DRAFT, not submitted**, with `reason: select from your state's list` unless the operator gave the list.
- An "Input problems" section with every `input_problems` line (file, row, column, raw value), or "None".
- The sign-off block from `references/output-conventions.md`.

## Gotchas

- **"Significant" thresholds need a base, and deadlines go first.** For any state: (a) use only the significant-discrepancy threshold that `references/state-profiles.md` cites, and when the profile found no numeric threshold (CO, MI, IL and OK), write "no numeric threshold found in the sources the profile checked", not that the state has none, and don't apply another state's threshold; (b) always put that state's discrepancy, theft and loss notification deadline(s) from the profile at the top of the report, with who to notify and the form if one is named, as a decision for compliance to make today. If the profile has no deadline for the state, say that and mark it NEEDS VERIFICATION. For example, Massachusetts treats any inventory discrepancy as reportable (law enforcement and the CCC within 24 hours, then an incident report within 10 calendar days), and New York requires notice to OCM within 24 hours when a discrepancy reaches 2% or 5% of anticipated inventory, depending on license type. **Illinois dispensaries** need Department (IDFPR) approval before posting any inventory adjustment (68 Ill. Adm. Code 1291.310(e)(1)), so every draft adjustment for one must say "do not post until IDFPR approves". California example: 4 CCR §15034 defines a significant discrepancy as "a five percent difference" between physical and track-and-trace inventory, §15051 requires an audit and written notice to DCC when one is found, and §15036(a)(1) requires notifying DCC and local law enforcement within 24 hours of discovering a significant discrepancy (form DCC-LIC-028). If the variance could meet the 5% threshold under either reading, put the 24-hour notice at the top of the report as a decision for compliance to make today. The rule doesn't say whether 5% is per package or on total inventory. The script reports both (`pct_of_system` per row, `net_difference_pct_of_compared_total` overall). The overall figure covers only quantity-compared packages, and its base is `system_total_compared`. Packages missing from one list, and rows with unit, duplicate or quantity problems, aren't in it, so list them next to the total reading. `system_total_all_packages` gives the full system weight and count for context. Show both readings and leave the interpretation to compliance or counsel.

- **Pounds vs. grams.** 1 lb = 453.592 g. Let the script convert. There is no automatic rounding allowance: different units are not evidence of rounding, so any nonzero difference is a variance. A package recorded as "2 Pounds" and counted as 907.2 g is `OVER_IN_COUNT` by 0.016 g, with a note that scale resolution or a rounded factor could explain a difference that small. Report it as a small variance. Only the operator's own `--tolerance-g` (for example their scale's resolution) moves it to `WITHIN_TOLERANCE`.
- **"Each" vs. weight.** Pre-rolls, carts, and edibles may be tracked as count-based in traceability but weighed on the count sheet (or the other way round). The script won't convert these (`UOM_MISMATCH`). Ask for the net weight per unit, or recount in the system's unit.
- **Bulk flower loses weight.** Flower keeps losing moisture after packaging, so small, consistent shortfalls on bulk flower packages that have sat a long time fit that pattern. That's a hypothesis to check against package age, a scale check and a dated weigh history, not a finding. It doesn't justify an automatic adjustment.
- **Timing gaps.** Sales recorded in the POS but not yet reported to traceability, transfers in transit, and lab samples pulled but not recorded all show up as `SHORT_IN_COUNT` or `IN_SYSTEM_NOT_COUNTED`. Check these before calling anything a loss.
- **Splits and repackaging.** A package that was split into new tags shows the parent as short and the children as `COUNTED_NOT_IN_SYSTEM` if the new packages weren't created in the system yet. Look for matching item names and quantities that add up.
- **Tag typos.** When a count-only tag is within 2 characters of exactly one system-only tag, both rows keep their own status (`COUNTED_NOT_IN_SYSTEM` and `IN_SYSTEM_NOT_COUNTED`) and the notes name the near-match. It may be a typo, but sequential tags from the same roll look the same, so confirm against the physical label before treating it as one package. Until then, keep both open and rank the counted-not-in-system row as high priority.
- **Over-counts matter too.** `OVER_IN_COUNT` and `COUNTED_NOT_IN_SYSTEM` can mean untracked product on site. Rank them as high-priority, not as "good news."
- **Zero-quantity active packages** in the system export are usually finished packages someone didn't close out. List them, but don't treat them as missing inventory.

## Example

User: "Metrc says we have 10 active packages in Vault A / Dry Room 2 / Finished Goods, here's our Sept 30 count — why don't they match? We're in Michigan, Class C grower + processor."

Good output opens with the decision for compliance: "The Michigan profile found no numeric significant-discrepancy threshold in the sources it checked, but if any shortage turns out to be theft or loss, R 420.804 requires notifying the CRA and local law enforcement within 24 hours (profile: NEEDS VERIFICATION). Decide today." Then: "12 packages listed, 7 quantity-compared: 3 match, 4 differ, and 5 couldn't be compared (pre-roll each vs g, two not counted, two not in Metrc). Net weight variance −23.792 g (Blue Dream 1 lb package −5.692 g, GMO Cookies −18.1 g, both bulk flower: re-weigh; moisture loss is one hypothesis to check against package age and weigh history). Net units +10: Live Resin carts −2, recount; Gummies +12 over the system, high priority, possible untracked product. One rosin package may be mistyped on the count sheet (…0011 vs …0110)…". It then gives the jurisdiction block, assumptions, the variance table, draft actions, and the sign-off.
