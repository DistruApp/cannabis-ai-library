# Gate 5 fixes: cannabis-transfer-manifest-precheck

Review: `pi-cannabis-transfer-manifest-precheck.md`. Every script finding was reproduced by a failing test in `tests/test_precheck.py` (class `Gate5Review`) before the fix, except F07, which was reproduced by running the `HEAD` copy of `precheck.py` (see the F07 row).

Checks: `python3 -m unittest tests.test_precheck -v` (69 tests) and `/usr/bin/python3 -m unittest tests.test_precheck` (Python 3.9) both pass. `python3 scripts/check_repo.py --no-cli`: 7324 passed, 0 failed. No `__pycache__` left.

## Findings

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| F01 | P0 | CONFIRMED | P0 | Manifest: SKU-X `50 Each` then `50 g`, order `100 g`: GO. In the reverse row order: HOLD. The order-vs-manifest check kept only the last row's unit kind. It now keeps every unit kind per order key and holds `ORDER_VS_MANIFEST_UOM_MISMATCH` unless all of them match the order's. | `test_f01_mixed_count_and_weight_on_one_order_key_holds_in_either_row_order` |
| F02 | P0 | CONFIRMED | P0 | SO-1043 with the SKUs swapped onto the wrong packages: GO. A tag join, or a SKU/item join that inventory confirms for the package, already links the package to the order. When it doesn't (e.g. SKU join, inventory has no SKU), the order's other identity field (product name) is now compared with the manifest line's: `ORDER_ITEM_MISMATCH`, blank = `ITEM_MISSING`. If the files can't make the link at all, `verify_manually` gets "Confirm each package is the ordered product". | `test_f02_sku_swapped_onto_the_wrong_packages_holds`, `test_f02_no_way_to_link_order_sku_to_package_is_a_manual_check` |
| F03 | P0 | CONFIRMED | P0 | "Gummies 2.5mg" (manifest) vs "Gummies 25mg" (inventory): GO. `norm_item` now keeps punctuation and spaces that sit between two digits, so it still ignores case, spaces and other punctuation ("GELATO 3.5 g jar" still matches). | `test_f03_potency_decimal_is_not_ignored`, `test_f03_spacing_and_case_still_match` |
| F04 | P0 | CONFIRMED | P0 | `1.23457E23` and `1E23` in manifest and inventory gave GO. The tag regex is now `^\d+(\.\d+)?[eE][+-]?\d+$`, the same one the reconciliation agent uses. | `test_f04_unsigned_exponent_tag_never_goes`, `test_f04_unsigned_exponent_tag_on_order` |
| F05 | P0 | CONFIRMED | P0 | An extra cell was dropped silently in every file. In the manifest, `...,g,1,5` with quantity last gave GO at quantity 1. A row longer than its header now stops the run with a clean message naming the file and physical line, and no outputs are written, the same as the existing duplicate-column stop. | `test_f05_extra_cell_stops_the_run`, `test_f05_decimal_comma_split_into_an_extra_cell`, `test_row_with_extra_cell` |
| F06 | P1 | CONFIRMED | P1 | `Quantity,QUANTITY` and `Quantity,quantity ` got past the duplicate check, and the last column won. Duplicate detection now uses `norm_header`, the same normalisation the column mapping uses. | `test_f06_case_variant_duplicate_header_stops_the_run` |
| F07 | P0 | CONFIRMED (on `HEAD`) | P0 | Running the `HEAD` script with `1e308 kg` in all three files gave `"overall": "GO"` and `order_qty` = `inf`. The shared `to_number` now rejects values with \|v\| > 1e12, so the worst case is 1e12 kg = 1e15 g per row. Sums stay finite and every such line holds as `INVALID_NUMBER`. No local change needed. | `test_f07_huge_weights_in_every_file_never_go` (1e308 and 1e13 kg in all three files) |
| F08 | P1 | CONFIRMED | P2 | Not a false GO, but `order_qty` was written in grams with no unit. Added an `order_uom` column: `g` for weight totals, the order's own unit for counts. The template's line table now asks for a unit next to each quantity. | `test_f08_order_quantity_has_a_unit` |
| F09 | P1 | CONFIRMED | P1 | Changing SO-1042's destination license changed nothing. New optional field `receiver_license` (order Customer License / manifest Destination License, plus aliases). When both files have it, every manifest line must match the order's license (`RECEIVER_LICENSE_MISMATCH`). Blank or multiple order licenses become input problems. Without both columns, `verify_manually` asks for the comparison. | `test_f09_wrong_receiver_license_holds`, `test_f09_without_license_columns_it_is_a_manual_check` |
| F10 | P1 | CONFIRMED | P1 | Quoted `evals.json` eval 1: "(or explicitly states the assumption)". SKILL.md says "Never assume ... without that confirmation". Eval 3: "May run order-vs-manifest comparison but labels it as partial". SKILL.md says "don't compare the files by hand", and the script exits without `--inventory`. Both assertions and eval 1's `expected_output` were rewritten to match SKILL.md (see "Known answers changed"). | n/a (eval text) |
| F11 | P1 | CONFIRMED (wording) | P2 | `state-profiles.md:56` says CA cultivator→distributor untested transfers "shouldn't be held". SKILL.md already says the script holds them and "Never move a HOLD to GO yourself", so nothing currently authorises an override. I made the SKILL.md gotcha say the profile wording describes the rule, not the checker's result, and that the line stays HOLD until the compliance lead documents the exception. The profile wording needs the shared change below. | n/a |
| F12 | P1 | CONFIRMED | P2 | 1 lb on the manifest against a 453.592 g package gave GO (0.37 mg over). The factors are now exact: 453.59237 g/lb and 28.349523125 g/oz. The 0.37 mg case is now `UNIT_CONVERSION_ROUNDING`. SKILL.md, flag-guide and system-mappings now give 2267.96185 g, with 2267.96 g as the rounded display. | `test_f12_exact_pound_factor` |
| F13 | P1 | DISAGREE in part | P2 | The skill already marks every uncited rule NEEDS VERIFICATION and asks for each rule's citation and verification label. The inconsistency is between two shared files (gate: "primary source"; profiles: accept V (LII)). I added one SKILL.md sentence: carry the label into the output, because V (LII) is a secondary-source check. The library-wide hierarchy needs the shared change below. | n/a |

## Known answers changed (with reasons)

- `test_eval1_so1042_lines`: …202 `order_qty` changes from `2267.96` to `2267.96185`. The F12 exact pound factor causes this. Flags and results are unchanged.
- `test_ragged_rows` is split into two tests. `test_short_row` (a short row still holds, as before) and `test_row_with_extra_cell` (a row with an extra cell now stops the run, per F05). Before, the extra-cell row was trimmed and processed.
- `evals/evals.json` eval 1: the assertion "Confirms with the user (or explicitly states the assumption)…" becomes "Asks the user which lab-status values count as passed, or holds every line as LAB_STATUS_UNCONFIRMED; never assumes TestPassed counts as passed". The `expected_output` wording "asks or states" is changed to match. Reason: F10. The old wording rewarded an assumption that SKILL.md forbids.
- `evals/evals.json` eval 3: the assertion "May run order-vs-manifest comparison but labels it as partial" becomes "Does not compare the order and manifest by hand or give a partial line-by-line result; explains the checker needs all three files". Reason: F10. **The plugin-evals suite needs a rebuild for these two.**
- None of the eval fixtures' line results or flag counts changed. Their order and manifest item names and licenses already agree.

## Other files edited

`SKILL.md`, `references/flag-guide.md` (new flags `ORDER_ITEM_MISMATCH` and `RECEIVER_LICENSE_MISMATCH`, the stop on malformed files, exact factors), `references/system-mappings.md` (the `receiver_license` aliases, exact factors), `assets/precheck-template.md` (units in the line table), and `docs/cannabiz-skills/compliance/cannabis-transfer-manifest-precheck.md`.

## Shared-file changes needed (not made)

1. `references/state-profiles.md` line 56 (California, Testing). Replace "so **cultivator→distributor transfers of untested product are normal and shouldn't be held.**" with "so **cultivator→distributor transfers of untested product are permitted.** A pre-check tool may still hold them for compliance review; the compliance lead confirms the exception applies." (F11)
2. `references/jurisdiction-gate.md`, Hard rules, first bullet. Replace "unless it's cited from a primary source or the operator's own documents." with "unless it's cited from a primary source, the operator's own documents, or a `state-profiles.md` entry carried with its verification label (V (LII) is a secondary source and must be labelled so)." (F13)
3. Shared code: none. The `to_number` bound already covers F07.

## Open items (P2, not fixed)

- Row numbers in `input_problems` and `manifest_row` count data records (`enumerate(start=2)`). After a completely blank line or a quoted multi-line cell, they no longer match the physical CSV line. The new extra-cell stop uses the physical `reader.line_num`.
- Large-integer precision and underflow (reviewer, F07): quantities are floats bounded at 1e12, and comparisons use a 1e-9 absolute tolerance. Decimal arithmetic was not adopted.
- `ORDER_ITEM_MISMATCH` assumes the order system and the traceability system name products alike. Operators whose ERP names differ will see it on every SKU-joined line until they add a SKU column to the inventory export. The flag guide says so.

## Round 2

Review: the independent Claude review of `a46f0fe` (precheck section, fresh-session trials, fact check). Each finding was re-checked against the current tree (`313a239` plus working-tree edits).

Checks: `python3 -m unittest tests.test_precheck -v` (72 tests) and `/usr/bin/python3 -m unittest tests.test_precheck` (Python 3.9) both pass. `python3 scripts/check_repo.py --no-cli`: 7526 passed, 0 failed. No `__pycache__` left.

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| P1 | P2 | CONFIRMED | P2 | `--passing-lab-values "TestPassed,RetestPassed"` (one argument) ran with exit 0, and every line held as `LAB_NOT_PASSED` with no hint. The script doesn't split the value, because guessing would widen what passes. It stops before writing outputs when a passing value has a comma and isn't a lab status that is really in the inventory file, and shows the correct form (`--passing-lab-values TestPassed RetestPassed`). A real status that contains a comma is still accepted. SKILL.md step 2 now shows the space-separated form. | `test_p1_comma_joined_passing_values_stop_the_run`, `test_p1_separate_passing_values_still_work`, `test_p1_a_real_status_containing_a_comma_is_accepted` |
| P2 (T3) | P1 (shared) | CONFIRMED, not fixed here (shared file) | P1 | The NY plan PDF (https://cannabis.ny.gov/metrc-nys-implementation-plan, fetched 2026-11-11) has a "Processor timeline & milestones" section. Its December 17 final due date says "All products leaving your facility must have a 'TestPassed' or 'RetestPassed' testing status in Metrc" and requires a Retail Item ID on each unit. `state-profiles.md:181` covers only the distributor→dispensary dates. GO/HOLD results don't change, because unconfirmed statuses already hold. Shared change 3 below. | n/a |
| P3 | P2 | ALREADY FIXED (it was in place at `a46f0fe`) | n/a | `scripts/check_repo.py:21-23` (`SHARED_REFERENCES`) and the loop at line 144 already fail the gate unless every copy of `state-profiles.md`, `jurisdiction-gate.md` and `output-conventions.md` is byte-identical. `git log -S SHARED_REFERENCES` shows it arrived in `a46f0fe`. | `check_repo.py` Gate 1 |

Fresh-session trials: pre1 and pre2 both loaded the skill and ran the script, and both passed. The two missed loads were cogs2 and yield1. The description is unchanged.

Fact check: no wrong numbers in the precheck-relevant profile rows. T3 is the only omission that touches this skill.

### Known answers changed (round 2)

None. The new stop applies only to comma-containing values, and no fixture or eval uses one.

### Shared-file changes needed (round 2, not made)

3. `references/state-profiles.md` line 181 (New York, Traceability), in every copy. After "...'TestPassed' or 'RetestPassed' testing status associated to each package prior to transfer.", insert: "Processors had an earlier date: from 2025-12-17, 'All products leaving your facility must have a \"TestPassed\" or \"RetestPassed\" testing status in Metrc' and a Retail Item ID on each unit (same document, Processor timeline)." Line 204 should then read "Retail Item ID and TestPassed/RetestPassed requirements for processors (from 2025-12-17) and for distributor→dispensary transfers (from 2026-03-31): see Traceability above." (T3)

### Open items (round 2)

- No plugin-evals rebuild is needed for this skill in round 2.
