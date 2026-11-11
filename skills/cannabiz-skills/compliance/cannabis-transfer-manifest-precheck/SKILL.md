---
name: cannabis-transfer-manifest-precheck
description: Check an outgoing cannabis B2B transfer before the driver leaves by comparing the sales order, the draft transfer manifest, and active package inventory with lab status, then return GO or HOLD per line with fixes. Use when a licensed cultivator, manufacturer, or distributor asks to check a manifest, verify a transfer or delivery against an order, asks whether the quantity, package or unit on an outgoing transfer is right, catch wrong packages, quantities, units, or untested product before shipping, or uploads a Metrc/BioTrack transfer draft next to an invoice or sales order, even if they don't say "manifest." Not for receiving inbound transfers, full inventory reconciliations, route planning, or creating or submitting the transfer in the state system.
license: MIT
metadata:
  version: "1.0"
  category: compliance-distribution
  risk-level: high
  last-compliance-review: "2026-11-11"
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
| Active package inventory | package tag, quantity, unit, lab/testing status | Export it *today*, close to departure. Include the item name or SKU so the script can catch a wrong package |

Optional: COA list, receiver license number. If a file is missing, ask for it. Never reconstruct a manifest from the order.

Run `python3 <skill-dir>/scripts/precheck.py --order … --manifest … --inventory … --detect-only`. `<skill-dir>` is the folder that contains this SKILL.md. If the script can't be found or fails to run, stop and tell the user what failed. Never hand-compute the figures the script produces, and don't compare the files by hand either (no list of rows that differ, match, are missing or would pass).

Show the user the mappings, the join key, and the **distinct lab-status values** found. Ask which values mean "passed for sale/transfer" in their system and state, and pass them exactly with `--passing-lab-values`. Never assume a value like "TestPassed" counts as passed without that confirmation. Different states and systems use different status sets. If no confirmation comes, run without the flag: every line holds as `LAB_STATUS_UNCONFIRMED`, and you say why.

Resolve `AMBIGUOUS` columns with `--map-order field=Column` (also `--map-manifest`, `--map-inventory`). Alias hints are in `references/system-mappings.md`.

### 3. Run

```
python3 <skill-dir>/scripts/precheck.py --order <f> --manifest <f> --inventory <f> --passing-lab-values <v…> --out-dir <dir>
```

Use the script's results as-is. You may move a line from GO to HOLD if you see a problem the script missed; say why. Never move a line from HOLD to GO. Flag meanings and fixes are in `references/flag-guide.md`. Read the `notes` column too: it explains blank units and lists both rows of a duplicate inventory tag. Also report every line in `input_problems` (blank tags, tags in scientific notation, duplicate inventory tags, order lines entered on more than one row, blank units, missing unit columns, blank or invalid quantities, blank item cells). The overall result is HOLD whenever `input_problems` isn't empty, even if every line shows GO, because an input problem can hide a problem with a shipped line.

### 4. Explain HOLDs

For each HOLD line: what's wrong in one sentence, the fix, and who fixes it (sales, shipping, compliance). Group by fix. Several flags often share one cause (e.g. the wrong package was pulled). Order-vs-manifest mismatches may be intentional (short-ship, substitution): ask, don't assume. A substitution still needs the order or invoice amended.

### 5. Manual verification

The script prints `verify_manually` items that files can't prove: license status of both parties on the shipping day, driver/vehicle/route fields, transport and timing rules, labeling, COA match. Keep them in the output and add where to check. Use the licensee lookup URL from `state-profiles.md` if present, otherwise "your state regulator's license search (NEEDS VERIFICATION)".

### 6. Output

Use `assets/precheck-template.md` and `references/output-conventions.md`. The top line is **GO** or **HOLD** with the count of lines to fix. "GO" always reads as *"GO on file checks; manual checks below still required."*

## Before you reply

**Bad values and blanks.** Quote the raw cell (`NaN`, `'1,5'`, `'12,5'`, a blank unit or item) with its tag, file and row, and say who corrects it before a rerun. Don't offer readings ("probably 1.5 lb", "a typo for 125"), don't work out what a reading would give, and don't tell them what to enter from another file ("enter 24, the order quantity"). The file's owner confirms the real figure.

**You never create, submit or dispatch anything** in Metrc or any system, not now and not "if you give me access". Say the operator does it after the manual checks.

**Your final reply must contain** (from `assets/precheck-template.md`):
- First line: **HOLD** with the number of lines to fix, or, in these exact words, "**GO on file checks**; manual checks below still required." (not "file checks pass" or a bare "GO"). Don't use the words "compliant" or "cleared" anywhere, not even to say you aren't using them.
- For a `UNIT_CONVERSION_ROUNDING` line, both figures (e.g. 2268 g on the manifest vs 5 lb = 2267.96 g in the package) and the fix: restate it in the package's unit.
- The jurisdiction block: state, both license types, traceability system, and rules relied on, with every rule-dependent item that isn't cited in `references/state-profiles.md` marked **NEEDS VERIFICATION**.
- The line table with a Flags column holding the script's flag names (e.g. `MISSING_UNIT`, `DUPLICATE_INVENTORY_TAG`, `INVALID_NUMBER`, `ITEM_MISMATCH`), and for a duplicate inventory tag each row's quantity and lab status.
- Fixes grouped by owner.
- "Input problems found": every `input_problems` line with its file and row, or "None".
- The manual-verification list, with where to check and NEEDS VERIFICATION on anything not cited.
- The sign-off block.

## Gotchas

- **Unit conversion rounding.** 5 lb is 2267.96 g, not 2268 g. A manifest that restates a pound-based package in rounded grams asks for more than the package holds. The script flags this as `UNIT_CONVERSION_ROUNDING`. Fix it by stating the quantity in the package's own unit. The rounding flags only appear when the units really differ (lb vs. g). 100.3 g against a 100 g package is `EXCEEDS_ON_HAND`, because "g" and "Grams" are the same unit.
- **Blank units.** A blank unit is never filled in from another file. The line holds as `MISSING_UNIT` (manifest), `INVENTORY_UNIT_MISSING` (inventory) or `ORDER_UNIT_MISSING` (order), and the quantities aren't compared. Ask the file's owner for the unit and rerun.
- **Wrong package** (`ITEM_MISMATCH`). The script compares the manifest's item name, and SKU when both files have one, with the package's, ignoring case, spaces and punctuation. A different item means the wrong package was pulled or the manifest names the wrong item. `ITEM_MISSING` means the item or SKU cell is blank, so the package couldn't be matched. If the inventory export has no item column, the line isn't held but `verify_manually` asks you to check each package's item by hand.
- **Bad numbers** (`INVALID_NUMBER`). A manifest, on-hand or order quantity that is text, NaN or inf, negative, or written with a decimal comma ("1,5", "1.234,5") holds the line. US thousands separators ("1,234.5") are read normally. The script never guesses what a decimal comma means. Ask the file's owner to correct the cell and rerun.
- **Tags in scientific notation** (`TAG_SCIENTIFIC_NOTATION`). A numeric tag that Excel turned into something like `1.23457E+23` has lost its real digits, so it can't be matched, even when every file was mangled the same way. The manifest line (or order line) holds, an inventory row with such a tag is not used, and `input_problems` gives the row and raw value. Ask for a re-export with the tag column formatted as text.
- **Same tag twice in inventory** (`DUPLICATE_INVENTORY_TAG`). The script keeps neither row: the line holds and the note lists each row's quantity and lab status. Find out which row is current before shipping.
- **Same tag twice** on a manifest (`DUPLICATE_TAG_ON_MANIFEST`) is usually a copy-paste error even when the total matches the order.
- **State exceptions for untested product** (`LAB_NOT_PASSED`). Some states allow specific transfers of untested product: California cultivator→distributor (regulatory testing happens at the distributor), Michigan cultivator→processor/producer, and Massachusetts failed product cultivator→manufacturer for remediation only. The script still holds those lines as `LAB_NOT_PASSED`. Explain the state exception from `references/state-profiles.md`, with its citation and verification label, and let the compliance lead decide. Never move a HOLD to GO yourself.
- **Michigan holds and recalls.** Before a sale or transfer in Michigan, verify in Metrc that each package isn't on administrative hold, recalled, or ordered destroyed (R 420.502(5), in the profile). Files can't prove this, so add it to the manual-verification list.
- **Lab status is a snapshot.** A status can change between the inventory export and departure. Re-export inventory right before shipping if hours have passed.
- **On-hand ≠ available.** Packages on hold, allocated to another order, or in quarantine can still show quantity. Ask whether the inventory export excludes holds.
- **Partial ships and substitutions** appear as `ORDER_QTY_MISMATCH` / `NOT_ON_ORDER`. They aren't necessarily wrong, but the order or invoice has to match what ships.
- **GO isn't clearance.** The script can't see license status, vehicle and driver details, or state transport rules. Never call a shipment "compliant."

## Example

User: "Driver leaves at 2. Here's SO-1042, the draft manifest, and this morning's Metrc active packages. Michigan, we're a processor shipping to a retailer."

Good output opens with: "**HOLD.** 8 of 9 lines need action. Two packages aren't passed (Gummies …205 *TestFailed*, Rosin …207 *SubmittedForTesting*), so pull them. The pre-roll line ships 60 but the package holds 48 and the order is 50. Blue Dream is written as 2268 g but the package is 5 lb (2267.96 g), so restate it in pounds. Tincture …208 is on the order but not on the manifest. Package …206 isn't in active inventory and isn't on the order…" It then gives the jurisdiction block, the line table, the fixes grouped by owner, the manual-verification list, and the sign-off.
