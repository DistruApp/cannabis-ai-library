# Gate 5 fixes: cannabis-replenishment-planner

Review: `pi-cannabis-replenishment-planner.md` (GPT 6.1, read-only), plus the coordinator's note that a second reviewer (Claude) independently found R2 and rates it P0.

Every script finding was reproduced with a unittest in `tests/test_replenish.py`, class `Gate5Regressions`. Each test fails on the pre-fix script and passes after the fix. The exceptions are `test_r2_new_sku_still_shortened_when_export_has_earlier_history` and `test_r1_single_account_runs`, which guard behaviour that must not change.

## Findings

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| R1 accounts merged | P0 | CONFIRMED | P1 | The script now detects an account/store column (Account, Store, Retailer, Dispensary and similar; not Customer or Location, which are per-transaction or per-bin). It stops (exit 1) if either file has more than one value, or the two files name different accounts. `--detect-only` reports `accounts` and a warning. SKILL.md: one account or store per run. | `test_r1_more_than_one_account_stops`, `test_r1_single_account_runs` |
| R2 intermittent seller treated as NEW_SKU | P0 | CONFIRMED | P0 | Velocity is measured over the days of the window that the export covers. `NEW_SKU` (days since first sale) is used only when the export reaches back before the window with no sale of that SKU. If the export starts on or after the window start, a late first sale is `NEW_OR_SLOW(first sale date)` and is measured over the whole covered window. An export that starts after the window start adds a warning. The coordinator's exact case: an export starting 9/3 (the window start) and one unit on 9/28 used to give `NEW_SKU(3d)`, 1/3 per day and an order of 7. It now gives 1/28 per day and an order of 1. Eval 1/2's Runtz `NEW_SKU(11d)` is unchanged because that export starts 8/2. | `test_r2_export_starting_in_window_slow_sku_is_not_new`, `test_r2_export_starting_after_window_start_measures_covered_days`, `test_r2_new_sku_still_shortened_when_export_has_earlier_history` |
| R3 MOQ treated as case pack | P0 | CONFIRMED | P1 | Removed `moq` and `min order qty` from the case-pack aliases. A new optional field, `min_order_qty`, is read from MOQ-type columns. A quantity below it is flagged `BELOW_MOQ(n)` and is not raised. Unreadable values are flagged `BAD_MOQ`. | `test_r3_moq_is_not_a_case_pack` |
| R4 fractional case pack | P0 | CONFIRMED | P1 | A case pack must be a whole number above 0. Otherwise it is `BAD_CASE_PACK` and the quantity is not rounded. Rounding now uses integer arithmetic. | `test_r4_fractional_case_pack_is_not_used` |
| R5 duplicate row outvotes unreadable cost/pack | P0 | CONFIRMED | P1 | The rule that a bad cell is never outvoted now covers every attribute, not just lead time. An unreadable cost, pack or MOQ on any duplicate row leaves that value blank. | `test_r5_unreadable_duplicate_cell_is_not_outvoted` |
| R6 inventory-only SKU with unreadable on-hand disappears | P0 | CONFIRMED | P2 | The SKU now stays in `replenishment.csv` with `NO_ONHAND_RECORD`. Its bad cell was already in input_problems. | `test_r6_inventory_only_sku_with_unreadable_on_hand_is_listed` |
| R7 short history called dead stock | P0 | CONFIRMED | P1 | A SKU with no sale in an export covering fewer than `--dead-days` days is now `NO_SALES_SEEN(export covers Nd)`. It is not `DEAD` and is not counted in the dead-stock value. | `test_r7_short_export_is_not_dead_stock` |
| R8 unknown cost valued as $0 | P0 | CONFIRMED | P1 | `dead_stock_cost_value` now covers only dead SKUs that have a unit cost. The new `dead_stock_missing_cost` list gives the SKU and units for the rest. SKILL.md says to report both. | `test_r8_dead_stock_with_unknown_cost_is_listed_not_zero` |
| R9 invented stockout duration | P0 | CONFIRMED (docs) | P2 | method.md and SKILL.md no longer say "out of stock for at least a week" or "recommend the buyer bump the qty". The example no longer says "sold out 9/28". It now says 0 on hand, last sold 9/28, and asks the buyer when it ran out. The flag logic is unchanged. | n/a (docs) |
| R10 overflow / lead time outside to_number | P0 | CONFIRMED | P0 | `parse_lead` runs the number through `to_number` (1e12 limit) and rejects anything over 365 days (`MAX_LEAD_DAYS`) as `BAD_LEAD_TIME`. `--default-lead-time` has the same 365-day cap. The sales-sum overflow (1e308 cells) is already blocked by the shared `to_number` limit, and `BAD_NUMBERS` "huge" covers it. This fixes the two failing `BadNumbers` tests on '9999999999999'. | `test_lead_time_bad_numbers`, `test_lead_time_bad_numbers_never_replaced_by_default`, `test_r10_lead_time_out_of_range_is_not_ordered`, `test_r10_default_lead_time_over_365_days_is_rejected` |
| R11 blank open PO = 0 silently | P1 | CONFIRMED | P1 | A blank open-PO cell (listing the SKUs) or a missing open-PO column is now an entry in `assumptions`. SKILL.md says to ask before the buyer acts. | `test_r11_blank_open_po_is_an_assumption` |
| R12 duplicate rows double-count SKU-level PO | P1 | CONFIRMED (documented behaviour) | P2 | Summing is documented and stated in input_problems. The meaning depends on the export's grain, which the script can't know. SKILL.md and method.md now tell the agent to ask whether a repeated open PO is per bin or per SKU. | n/a (docs) |
| R13 US date / comma conventions | P1 | CONFIRMED (dates); comma part is shared code | P2 | Slash dates that could be read as day/month (e.g. `03/09/2026`) now produce a warning, in both the run and `--detect-only`. The `'0,125'` → 125 issue is in the shared `_THOUSANDS_RE`, so I did not change it (requested change below). | `test_r13_day_month_ambiguous_dates_are_warned` |
| R14 eval 3 lead-time contradiction | P1 | CONFIRMED | P2 | evals.json eval 3: the expected output now says "until the operator provides lead times (or explicitly gives a default lead time to use)". The assertion now also rejects lead times the assistant picks and labels as assumptions. No numeric answer changed. | n/a (eval text) |

Known answers: none changed. Evals 1–6 totals ($4,620, $3,864, $1,569, $240) and all existing tests still pass. Summary.json gained `dead_stock_missing_cost`, and detect-only output gained `accounts` and `warnings`. `flag_counts` gained NEW_OR_SLOW, NO_SALES_SEEN, BAD_MOQ and BELOW_MOQ. Eval 3's mapped run now has one extra assumption, because `onhand_messy.csv` has no open-PO column. No test asserts that run's assumptions.

## Checks

- `python3 -m unittest tests.test_replenish`: 57 tests OK. `/usr/bin/python3 -m unittest tests.test_replenish` (3.9): OK.
- `python3 scripts/check_repo.py --no-cli`: 7324 passed, 0 failed.
- The shared `to_number` and `csv_safe` blocks are byte-identical to the pre-edit script.
- No `__pycache__` left.

## Shared-file changes requested

1. **`_THOUSANDS_RE` (shared to_number block, all five scripts):** `'0,125'` currently matches and reads as 125. In a decimal-comma export it means 0.125. Suggested change: `^[+-]?[1-9]\d{0,2}(,\d{3})+(\.\d+)?$`, which rejects a leading `0,`. A test such as `to_number("0,125") -> (None, "ambiguous comma ...")` would go with it.
2. **`references/output-conventions.md`:** the reviewer notes the `4 CCR §15xxx` example is a placeholder, not a usable citation. Mark it clearly as a format example, or replace it with a verified citation.

## Open items

- `references/system-mappings.md:27` (Metrc `GET /packages/v2/adjust/reasons`) and the state retesting/label-date guidance were not verified against primary sources. They are COULDN'T-VERIFY in the review, and I didn't change them. The guidance already marks state limits NEEDS VERIFICATION.
- The NEW_SKU heuristic still treats "no sales in the earlier export history" as new. A very intermittent seller (e.g. one sale every 45 days in a 60-day export) can still be shortened. The flag is provisional and SKILL.md tells the agent to confirm the SKU is new. A per-SKU launch-date input would close this fully.
- MOQ is checked but never applied. If buyers want the quantity raised to the MOQ, that would need an operator flag.

## Round 2

Review: the second independent reviewer (Claude), `REVIEW.md` section "cannabis-replenishment-planner", plus its "Fresh-session trials" and "Fact check" sections. That review was written against `a46f0fe`; each finding was rechecked against the tree after `313a239`. Its R1–R6 are not the same findings as the round 1 IDs above. New tests are in `tests/test_replenish.py`, class `Gate5Round2`. All fail on the `313a239` script (except the R1 test, which guards the round 1 fix and fails on `a46f0fe`) and pass now.

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| R1 slow sellers treated as NEW_SKU | P0 | ALREADY FIXED (round 1, R2 above) | P0 | Re-ran the reviewer's replen1 fixture: `a46f0fe` gives $3,720 with 2 `NEW_SKU`; the current script gives $1,944 with `NEW_OR_SLOW` 2, 28 days measured and no order for the chocolate and tincture. The test rebuilds that fixture inline. Trial replen1 also reasoned the wrong way ("if stocked before this window, sales are understated"). SKILL.md's `NEW_OR_SLOW` bullet now says the whole-window rate is right if it was on the shelf before the window, and is understated only if the buyer says it launched on its first-sale date. | `test_r1_replen1_once_sold_skus_are_not_ordered` |
| R2 POS timestamp formats rejected | P1 | CONFIRMED (`9/29/2026 2:03:15 PM`, ISO with `Z` or offset or fraction, `2026-09-29 14:03`, `Sep 29, 2026` all failed) | P1 | Dates now accept ISO with a time (seconds, fractions, `Z`/`UTC`/`+hh:mm`), YYYY/MM/DD with a time, MM/DD/YYYY or MM/DD/YY with a 24-hour or AM/PM time (with or without seconds), and month names. A timestamp is dated as written, never converted between time zones, and a `warnings` entry says when a zone is present. If no row has a readable date, the exit message names an unreadable value, its column and the accepted formats. If only some rows are unreadable, a `warnings` entry counts them and says velocity may be understated. | `test_r2_pos_timestamp_formats_are_read`, `test_r2_unreadable_dates_name_the_value_and_accepted_formats` |
| R3 day-first dates read month-first | P2 | CONFIRMED (round 1 added only a warning) | P1 | Day/month order is never guessed. New `--date-order mdy\|dmy` (default mdy). A slash date that can only be day/month (`29/09/2026`) stops the run (exit 1) and asks for `--date-order dmy`. A file that mixes both orders stops and asks for YYYY-MM-DD. A date that contradicts an explicit `--date-order` also stops. `--detect-only` lists the same problem under `warnings` and reports `date_order`. The existing either-way warning (`03/09/2026`) stays when `--date-order` isn't given. | `test_r2_r3_day_month_order_is_never_guessed`, existing `test_r13_day_month_ambiguous_dates_are_warned` |
| R4 leading-zero SKUs | P2 | CONFIRMED (no match, no hint) | P2 | Not matched, because the zeros may be real. Each sales/on-hand pair that differs only by leading zeros is in `input_problems`, and a `warnings` entry counts them. SKILL.md says not to report either side as unsold or as missing stock. | `test_r4_leading_zero_skus_are_reported_not_matched` |
| R5 dead stock with unknown cost valued at $0 | P2 | ALREADY FIXED (round 1, R8 above) | P2 | `dead_stock_cost_value` covers only SKUs with a cost; the others are in `dead_stock_missing_cost`. Blank, unreadable and conflicting costs all leave `unit_cost` as None. | `test_r8_dead_stock_with_unknown_cost_is_listed_not_zero` |
| R6 `--detect-only` requires `--as-of` | P2 | CONFIRMED | P2 | `--as-of` is now required only for a full run. The exit message for a full run without it is unchanged (eval 6 still passes). SKILL.md step 1: run the mapping check without `--as-of` and ask for the count date in the same combined question. | `test_r6_detect_only_does_not_need_as_of`, existing `test_eval6_missing_as_of_exits_with_clear_message` |

Trials: replen1 (skill fired, script ran) is covered by R1. replen2 passed. No trigger or hand-computing failure for this skill, so the description is unchanged. Fact check: no claim in this skill's files.

Known answers: none changed. Evals 1–6 ($4,620, $3,864, $1,569, $240) and all 57 earlier tests pass. New outputs: `--date-order` flag, `date_order` in `--detect-only` output, and new `warnings` entries (time zone, unreadable dates, leading zeros, date order).

Checks: `python3 -m unittest tests.test_replenish` 63 OK; `/usr/bin/python3 -m unittest tests.test_replenish` (3.9) 63 OK; `python3 scripts/check_repo.py --no-cli` 7526 passed, 0 failed. The shared `to_number` and `csv_safe` blocks are still byte-identical across all five scripts. No `__pycache__` left. Not committed.

Shared-file changes requested: none new. The round 1 `_THOUSANDS_RE` request still stands.

Open items:
- Month-name dates use `%b`/`%B`, which follow the process locale. They're English under the default C locale; a non-English locale would reject them (and the run would say so). Not seen in practice here.
- A `Z` (UTC) timestamp is not converted to store time, so a late-evening sale can be counted on the next day. The warning says so; converting would need the store's time zone as an input.
- The docs page (`docs/.../cannabis-replenishment-planner.md`) doesn't cover date formats and needed no change.
