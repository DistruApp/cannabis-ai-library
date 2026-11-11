# Gate 5 fixes: cannabis-traceability-reconciliation

Review: `pi-cannabis-traceability-reconciliation.md`. Every script finding was reproduced with a failing test in `tests/test_reconcile.py` (class `Gate5`) before the fix. F05 was reproduced on the committed script (`git show HEAD:…/reconcile.py`): `1e308 kg` on both sides gave `difference=nan`, status `SHORT_IN_COUNT`, a traceback, and a CSV written without a summary.

Checks: `python3 -m unittest tests.test_reconcile -v` (3.14) and `/usr/bin/python3 -m unittest tests.test_reconcile` (3.9): 62 tests pass. `python3 scripts/check_repo.py --no-cli`: 7324 passed, 0 failed. Shared `to_number` and `csv_safe` blocks are byte-identical across all five scripts (checked by hash). No `__pycache__` left.

Known answers kept: MI …102 −5.692 g, net −23.792 g / +10 each, compared base 3,041.192 g; the MI `reconciliation.csv` is byte-identical to the committed script's output.

## Findings

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| F01 | P0 | CONFIRMED | P0 | The automatic "unit-conversion rounding" allowance is removed. 1 g vs 960 mg, 0.01 g vs 0 mg and 100 kg vs 99,995 g were all `MATCH` with zero tolerance. Any nonzero difference is now a variance; a converted weight difference ≤ 0.05 g only gets a note that scale resolution or a rounded factor could explain it. Only the operator's `--tolerance-g` changes the status. `rounding_rule` in summary.json now says this. | `test_f01_unit_conversion_never_hides_a_shortage`, `test_f01_operator_tolerance_still_applies_to_converted_rows` |
| F02 | P0 | CONFIRMED | P0 ("1,234"), P2 ("$") | Count "1,234" g against system 1234 g gave a MATCH even when the counter meant European 1.234 g. In the skill-local `parse_qty` (not the shared block), a single comma group with no decimal point ("1,234", "12,345") is now `INVALID_NUMBER` with both readings in the problem text. "1,234.5" and "1,234,567" are still read. Any `$` in a quantity is rejected (the shared block deleted it, so "$1$0" became 10). `tolerance_arg` now uses `parse_qty`, so the same rules apply to tolerances. | `test_f02_single_comma_group_is_held_not_guessed`, `test_f02_unambiguous_thousands_still_read`, `test_f02_currency_symbol_in_quantity_is_invalid`, `test_f02_ambiguous_tolerance_is_rejected` |
| F03 | P0 | CONFIRMED | P0 | `Qty,qty` or `Package Tag,package_tag` passed the duplicate check, and detection silently used the last column. The duplicate-header check now compares `norm_header` names and stops with "more than one column named". | `test_f03_headers_that_collide_after_normalising_stop` |
| F04 | P0 | CONFIRMED | P0 | `1.23457E23` on both sides gave `MATCH`. The tag regex is now `^\d+(\.\d+)?[eE][+-]?\d+$`, the same one the precheck agent uses. | `test_f04_unsigned_exponent_tag_is_never_matched` |
| F05 | P0 | CONFIRMED (committed script) | P1 | The root cause is fixed by the shared `to_number` bound (rejects \|v\| > 1e12; at most 1e15 g after kg conversion, so sums stay finite). Locally, summary JSON is now built and validated before either output file is written, so a bad value can't leave a CSV without a summary. | `test_f05_huge_converted_values_never_overflow` (+ existing `huge` and `huge_plain` cases in `BadNumbers`) |
| F06 | P0 | CONFIRMED | P1 | Rounded differences were summed: 1 mg vs 0.96 mg was `SHORT_IN_COUNT` with net 0. The threshold counter also used the rounded percentage. Statuses, net, both gross figures, `pct_total` and `packages_over_5pct_abs` now use unrounded values (`_diff`/`_pct`, never written). Displayed differences and totals are rounded to 6 dp (was 4), so mg-level gaps show. The −4.9996% case was an over-flag, not hidden data, so I rate it P1. | `test_f06_tiny_difference_is_kept_in_row_and_totals`, `test_f06_threshold_uses_unrounded_percentage` |
| F07 | P1 | CONFIRMED | **P0** | Eval 4 …302: two identical 50 ea rows were summed to 100 and called a MATCH, although the operator said rows were double-entered. That hides a 50 ea shortage. Identical rows (same quantity and unit) are now never summed: they get `DUPLICATE_CONFLICT`, the note says "copy-paste duplicate", and they are left out of comparison. Non-identical duplicates are still summed, with the note as before. | `test_f07_identical_duplicate_rows_are_held_not_summed`, `test_identical_duplicate_count_row_is_held_and_reported` (replaces `test_duplicate_count_row_is_summed_and_reported`) |
| F08 | P1 | CONFIRMED | P2 | This only caused an unnecessary hold, never a wrong number. It was simple to fix: an operator-stated `--default-*-unit` now fills each blank cell in `index()` before duplicates combine. The note names the rows that used it, and `rows_using_default` now counts rows. | `test_f08_default_unit_is_applied_before_duplicates_are_combined` |
| F09 | P1 | PARTLY CONFIRMED | P2 | No false result. Fixed: a blank-tag problem now names its column and says "row not used"; a blank-unit problem gives row(s) and column; a sci-notation row with an invalid quantity says so; a one-sided package with a blank unit gets a note; a file with no usable tag now stops instead of producing an empty reconciliation. Not done: structured (non-string) problem records, which would be a schema change. | `test_f09_file_with_no_usable_tag_stops`; `test_blank_tag_is_reported` and `test_eval4_regression_totals_and_problems` updated |
| F10 | P1 | CONFIRMED (SKILL.md wording) | P1 | SKILL.md Gotcha (a) now says "no numeric threshold found in the sources the profile checked", not that the state has none. Step 5 now requires a primary-source cite in the profile and carries the profile's verification label. The example's opening line is reworded the same way. The shared `state-profiles.md` still has the absolute wording; see below. | text: SKILL.md lines in step 5, Gotchas (a), Example |
| F11 | P1 | CONFIRMED | P2 | SKILL.md step 2 now asks what the count covered. Mismatched or unknown timestamps, or a partial count, make every result PROVISIONAL; out-of-scope packages are scope gaps, not losses. | text: SKILL.md step 2 |
| F12 | P1 | CONFIRMED | P1 | The example said "12 packages compared"; only 7 were quantity-compared. It also left out the Live Resin −2 each and stated moisture loss as the cause. Both SKILL.md and the docs page now say "12 listed, 7 quantity-compared", include the carts, and call moisture loss a hypothesis. Step 6 explains `packages_quantity_compared` vs `packages_compared`. The report template's bottom line says the same. | text: SKILL.md Example, step 6; docs page; `assets/report-template.md` |
| F13 | P1 | CONFIRMED | P1 | Eval 2 assertion 1 now requires asking the operator, with no column chosen and no variance stated before the answer. SKILL.md step 2 says a stop for a missing, repeated or AMBIGUOUS column is a question for the operator, not a script failure. | `evals/evals.json` eval 2 |
| F14 | P1 | CONFIRMED | P2 | Added `gross_variance_all_compared` (every quantity-compared row) next to `gross_variance_outside_tolerance`. SKILL.md step 6, the final-reply list and the report template require both, under their labels. | `test_f14_gross_variance_of_all_compared_rows` |

## Known answers changed (with reasons)

- **Eval 4 …302:** `MATCH` → `DUPLICATE_CONFLICT` (F07: two identical rows may be one double entry). `packages_quantity_compared` 4 → 3. The `each` key disappears from `net_difference`, `system_total_compared` and `net_difference_pct_of_compared_total`, because no each package is compared any more.
- **Eval 4 …306:** `MATCH` → `OVER_IN_COUNT` +0.016 g (F01). `gross_variance_outside_tolerance` changes from 1.6408 g to 1.6568 g.
- **Eval 4, unchanged:** net −1.6248 g, `system_total_compared` 2360.776 g, −0.069%, `system_total_all_packages`, and all other statuses.
- **Eval 1, unchanged.**
- `evals/evals.json` now reflects these changes: eval 4 expected output and two assertions, eval 1's expected output and …102 assertion (now "a real shortfall after unit conversion"), and eval 2 assertions 1 and 3. **The plugin-evals suite needs a rebuild** (`build_suite.py`, not run by me).
- **Test-message wording:** the blank-tag problem text changed (it now names the column), and the blank-unit problem now includes row and column.

## Shared-file changes needed (not made)

1. **`to_number` (all five scripts), recommended:** move the two F02 rules into the shared parser so every skill gets them.
   - Reject `$` instead of `.replace("$", "")`. If cogs needs currency, strip a single leading `$` only.
   - Treat `^[+-]?\d{1,3},\d{3}$` (one comma group, no decimal point) as ambiguous.
   
   Until then, reconcile enforces both in its local `parse_qty`, which would become redundant but harmless.
2. **`references/state-profiles.md` (F10):** replace the absolute wording with a statement of what was found.
   - Line 15: "Where a state section says it defines no numeric significant-discrepancy threshold" → "Where a state section says no numeric significant-discrepancy threshold was found in the sources checked".
   - Line 83 (CO): "CO rules define no numeric…" → "No numeric significant-discrepancy threshold found in 3-805, 3-905 or 3-920".
   - Line 116 (MI): "MI rules set no numeric…" → "No numeric significant-discrepancy threshold found in R 420".
   - Line 230 (IL): "IL rules define no percentage…" → "No percentage 'significant discrepancy' threshold found; the rules use 'imbalance'".
   - Line 271 (OK): "OK rules define no percentage…" → "No percentage 'significant discrepancy' threshold found".
   - Line 279: "Chapter 10 sets no adjustment-reason list or correction deadline" → "No adjustment-reason list or correction deadline found in Chapter 10".

## Open items

- **Regulatory verification:** every claim in the reviewer's "Regulatory verification" table is still COULDN'T-VERIFY. I had no primary-source access in this pass; that needs a separate verification pass.
- **lb and oz factors:** the script uses 453.592 g/lb and 28.3495 g/oz; the exact values are 453.59237 and 28.349523. That is at most about 0.0004 g per lb. It is kept so the MI …102 −5.692 g known answer holds; changing it would shift that answer to −5.69237 g.
- **F09 remainder:** `input_problems` is still a list of strings, not structured records with path, line, column and raw value. The strings now carry row and column in every case the reviewer named.
- **Eval coverage:** no new behaviour eval was added for the reviewer's customer-level cases (colliding headers, unsigned sci tags, "1,234", mg-level gaps). They are covered by unit tests only. Adding them to eval fixtures would change eval 5's known answers, so I left it for a later gate.

## Round 2

Review: second independent reviewer, `REVIEW.md` (written against a46f0fe), findings T1–T6, plus its trials and fact check. Each finding was rechecked against the current tree (313a239 plus this round's edits).

Checks: `python3 -m unittest tests.test_reconcile -v` (3.14) and `/usr/bin/python3 -m unittest tests.test_reconcile` (3.9): 67 tests pass (5 new, class `Round2`). `python3 scripts/check_repo.py --no-cli`: 7554 passed, 0 failed. Shared `to_number` and `csv_safe` blocks are still byte-identical across all five scripts (checked by hash). No `__pycache__` left. No known answer changed: eval 1 and eval 4 outputs are unchanged, and on an 800 × 600 file with 384 planted typo hints the new `reconciliation.csv` and `summary.json` are byte-identical to the committed script's.

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| T1 | P1 | CONFIRMED | P1 | The near-match search compared every count-only tag with every system-only tag (full edit-distance table each time). Rechecked on the current tree: 500 × 500 took 9.3 s, the reviewer's 1,500 × 1,500 82 s. Now `single_near_matches` indexes system tags by their deletion keys (every string left after deleting 0, 1 or 2 characters, hashed). Two tags within 2 edits always share a key, so only tags that share a key are compared, and each comparison uses a banded check that stops early. This is exact, not a sample: it finds the same hints as the all-pairs scan. The index is built in blocks of 5,000 system tags, which caps memory at about 200 MB. Each count tag stops at its second match, because only a single match becomes a hint. Measured on 3.14 (3.9 in brackets): the reviewer's 1,500 × 1,500 files 0.27 s; 5,000 × 5,000 0.9 s (1.4 s); 10,000 × 10,000 2.4 s (3.5 s); 20,000 × 20,000 7.8 s. Peak memory 170–200 MB. | `test_t1_near_match_index_finds_exactly_what_a_full_scan_finds` (25 random trials against a full-table oracle, also with a tiny block size), `test_t1_edit_distance_check_matches_full_table` (3,000 random pairs), `test_t1_5000_by_5000_with_no_tags_in_common_runs_fast` (< 10 s and the planted typo is still found), `test_t1_sequential_tag_runs_stay_fast` (4,000 × 4,000 interleaved sequential tags) |
| T2 | P1 | MOSTLY ALREADY FIXED | P2 | The committed shared profile now has Subpart K: 1300.1030(a) record on completion (line 227), 1300.1050(b) end-of-business-day notice (240), 1300.1050(c) back-entry within 3 business days (245), and the 1300.1040 manifest with agent badge numbers and the vehicle registration number (250–256). Still missing: 1300.1010(f), received tags recorded within 3 calendar days. Shared file, so I didn't edit it: see below. | n/a (shared reference) |
| T3 | P1 | ALREADY FIXED | — | The shared profile line 205 now has the NY processor rule (TestPassed/RetestPassed before anything leaves, from December 17), and line 206 points to it. | n/a |
| T4 | P2 | CONFIRMED | P2 | Shared profile line 158 (935 CMR 500.105(13)) still doesn't say who gets the 24-hour transport-discrepancy report. Change requested below. | n/a (shared reference) |
| T5 | P2 | CONFIRMED | P2 | All still present in the shared profile: IB-2025-03 marked UNVERIFIED and listed under Blocked sites (lines 25, 219); DCC-2026-02-R UNVERIFIED and DCC-2026-03-R not mentioned (line 68); 1300.810 cited as (b) for the hold-or-witness power (line 264); Bulletin 18 missing the confirm-and-adjust step above 5% (line 199). Changes requested below. | n/a (shared reference) |
| T6 | P2 | CONFIRMED | P2 | `norm_tag` kept zero-width and other invisible characters, so a pasted tag split one package into `COUNTED_NOT_IN_SYSTEM` plus `IN_SYSTEM_NOT_COUNTED`. It now also drops Unicode format characters (category Cf: U+200B/C/D, U+2060, U+FEFF, soft hyphen U+00AD), the same way it already drops whitespace and hyphens. | `test_t6_invisible_characters_in_a_tag_do_not_split_the_package` |

Trials: recon1 and recon2 both passed (the skill fired, the script ran where files were given, nothing was submitted). No SKILL.md change needed.

### Shared-file changes needed (not made)

`references/state-profiles.md`, in both copies (reconciliation and precheck), which must stay byte-identical. Quote each source text before adding it; I didn't fetch the sources myself.
1. **T2, IL Subpart K:** add a bullet for 8 Ill. Adm. Code 1300.1010(f): IDOA licensees record received tags in the system within 3 calendar days. Source: IDOA Spring 2026 rule bulletin (V, URL already on line 221).
2. **T4, MA line 158:** "report … within 24 hours" → "report … to the Commission and Law Enforcement Authorities within 24 hours" (935 CMR 500.105(13)(b)1).
3. **T5:**
   - Line 219: IB-2025-03 → V (checked 2026-11-11), and drop the IB-2025-03 entry from Blocked sites (line 25).
   - Line 68: DCC-2026-02-R → "listed on https://cannabis.ca.gov/cannabis-laws/rulemaking/ as Track and Trace Updates, noticed 2026-06-05, pending (V)". Add DCC-2026-03-R, or say it wasn't checked.
   - Line 264: cite 1300.810(a) for "IDOA may hold product up to 7 days or send a witness", keeping (b) for the 7 days' notice.
   - Line 199 (Bulletin 18): add the receiver's required step when the variance is over 5%: confirm the quantity and adjust it in Metrc.
   - Relabel the CA and NY items the fact check found verbatim on the regulator's own copy from V (LII) to V (table in the reviewer's `factcheck.md`).

### Open items

- Near-match runtime grows roughly with (system tags ÷ 5,000) × count tags. 20,000 × 20,000 runs in about 8 s; 50,000 × 50,000 was not measured. A bigger block would be faster but use more memory: 10,000 per block gives 1.8 s at 10k, but about 330 MB.
- Python's string hash is randomised for each process. It only changes which tags are compared, never the result, because every candidate is verified exactly. The determinism tests still pass.
