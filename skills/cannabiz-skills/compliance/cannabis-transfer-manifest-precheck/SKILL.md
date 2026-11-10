---
name: cannabis-transfer-manifest-precheck
description: Check an outgoing cannabis B2B transfer before the driver leaves by comparing the sales order, the draft transfer manifest, and active package inventory with lab status, then return GO or HOLD per line with fixes. Use when a licensed cultivator, manufacturer, or distributor asks to check a manifest, verify a transfer or delivery against an order, catch wrong packages, quantities, units, or untested product before shipping, or uploads a Metrc/BioTrack transfer draft next to an invoice or sales order, even if they don't say "manifest." Not for receiving inbound transfers, full inventory reconciliations, route planning, or creating or submitting the transfer in the state system.
license: MIT
metadata:
  version: "1.0"
  category: compliance-distribution
  risk-level: high
  last-compliance-review: "2026-10-16"
---

# Transfer manifest pre-check

Catches the shipment problems that get transfers rejected, held, or flagged before the product leaves the building: wrong package, wrong quantity, wrong unit, untested or failed product, or more product than the package holds. The output is a GO/HOLD sheet a shipping lead can work through in minutes. Nothing is created or submitted in the traceability system.

## Workflow

```
- [ ] 1. Jurisdiction gate
- [ ] 2. Collect the three files and confirm mappings + passing lab values
- [ ] 3. Run scripts/precheck.py
- [ ] 4. Explain each HOLD and the fix
- [ ] 5. Add the manual-verification list
- [ ] 6. Write the sheet from assets/precheck-template.md
```

### 1. Jurisdiction gate

Read `references/jurisdiction-gate.md`. Get state, your license type, the receiver's license type, and the traceability system. Look up the state in `references/state-profiles.md`. Required manifest fields, transport rules, and which license types may receive which products are state-specific. Unless they're cited there or supplied by the operator, they're **NEEDS VERIFICATION**. The file checks in steps 2–4 don't depend on state, so run them while you wait for answers.

### 2. Files and mapping

| File | Must contain | Notes |
|---|---|---|
| Sales order / invoice | quantity + package tag, SKU, or item name | Join key is chosen automatically: tag → SKU → item name |
| Draft manifest / transfer export | package tag, quantity, unit | A line with no unit is held as `MISSING_UNIT`. The unit is never taken from the order or inventory |
| Active package inventory | package tag, quantity, unit, lab/testing status | Export it *today*, close to departure |

Optional: COA list, receiver license number. If a file is missing, ask for it. Never reconstruct a manifest from the order.

Run `python3 scripts/precheck.py --order … --manifest … --inventory … --detect-only`. Show the user the mappings, the join key, and the **distinct lab-status values** found. Ask which values mean "passed for sale/transfer" in their system and state, and pass them exactly with `--passing-lab-values`. Never assume a value like "TestPassed" counts as passed without that confirmation. Different states and systems use different status sets. If no confirmation comes, run without the flag: every line holds as `LAB_STATUS_UNCONFIRMED`, and you say why.

Resolve `AMBIGUOUS` columns with `--map-order field=Column` (also `--map-manifest`, `--map-inventory`). Alias hints are in `references/system-mappings.md`.

### 3. Run

```
python3 scripts/precheck.py --order <f> --manifest <f> --inventory <f> --passing-lab-values <v…> --out-dir <dir>
```

Use the script's results as-is. Flag meanings and fixes are in `references/flag-guide.md`. Read the `notes` column too: it explains blank units and lists both rows of a duplicate inventory tag. Also report every line in `input_problems` (blank inventory tags, duplicate inventory tags, blank units, missing unit columns, non-numeric quantities). The overall result is HOLD whenever `input_problems` isn't empty, even if every line shows GO, because an input problem can hide a problem with a shipped line.

### 4. Explain HOLDs

For each HOLD line: what's wrong in one sentence, the fix, and who fixes it (sales, shipping, compliance). Group by fix. Several flags often share one cause (e.g. the wrong package was pulled). Order-vs-manifest mismatches may be intentional (short-ship, substitution): ask, don't assume. A substitution still needs the order or invoice amended.

### 5. Manual verification

The script prints `verify_manually` items that files can't prove: license status of both parties on the shipping day, driver/vehicle/route fields, transport and timing rules, labeling, COA match. Keep them in the output and add where to check. Use the licensee lookup URL from `state-profiles.md` if present, otherwise "your state regulator's license search (NEEDS VERIFICATION)".

### 6. Output

Use `assets/precheck-template.md` and `references/output-conventions.md`. The top line is **GO** or **HOLD** with the count of lines to fix. "GO" always reads as *"GO on file checks; manual checks below still required."*

## Gotchas

- **Unit conversion rounding.** 5 lb is 2267.96 g, not 2268 g. A manifest that restates a pound-based package in rounded grams asks for more than the package holds. The script flags this as `UNIT_CONVERSION_ROUNDING`. Fix it by stating the quantity in the package's own unit. The rounding flags only appear when the units really differ (lb vs. g). 100.3 g against a 100 g package is `EXCEEDS_ON_HAND`, because "g" and "Grams" are the same unit.
- **Blank units.** A blank unit is never filled in from another file. The line holds as `MISSING_UNIT` (manifest), `INVENTORY_UNIT_MISSING` (inventory) or `ORDER_UNIT_MISSING` (order), and the quantities aren't compared. Ask the file's owner for the unit and rerun.
- **Same tag twice in inventory** (`DUPLICATE_INVENTORY_TAG`). The script keeps neither row: the line holds and the note lists each row's quantity and lab status. Find out which row is current before shipping.
- **Same tag twice** on a manifest (`DUPLICATE_TAG_ON_MANIFEST`) is usually a copy-paste error even when the total matches the order.
- **Lab status is a snapshot.** A status can change between the inventory export and departure. Re-export inventory right before shipping if hours have passed.
- **On-hand ≠ available.** Packages on hold, allocated to another order, or in quarantine can still show quantity. Ask whether the inventory export excludes holds.
- **Partial ships and substitutions** appear as `ORDER_QTY_MISMATCH` / `NOT_ON_ORDER`. They aren't necessarily wrong, but the order or invoice has to match what ships.
- **GO isn't clearance.** The script can't see license status, vehicle and driver details, or state transport rules. Never call a shipment "compliant."

## Example

User: "Driver leaves at 2. Here's SO-1042, the draft manifest, and this morning's Metrc active packages. Michigan, we're a processor shipping to a retailer."

Good output opens with: "**HOLD.** 8 of 9 lines need action. Two packages aren't passed (Gummies …205 *TestFailed*, Rosin …207 *SubmittedForTesting*), so pull them. The pre-roll line ships 60 but the package holds 48 and the order is 50. Blue Dream is written as 2268 g but the package is 5 lb (2267.96 g), so restate it in pounds. Tincture …208 is on the order but not on the manifest. Package …206 isn't in active inventory and isn't on the order…" It then gives the jurisdiction block, the line table, the fixes grouped by owner, the manual-verification list, and the sign-off.
