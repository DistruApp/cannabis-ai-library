# Gate 5 fixes: cannabis-batch-cogs

Review: `pi-cannabis-batch-cogs.md`. `B/` = `skills/cannabiz-skills/operations/cannabis-batch-cogs/`. Tests: `tests/test_cogs.py`, class `Gate5Regressions` unless noted.

## Findings

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| F1 | P0 | CONFIRMED | P0 | Reproduced: headers `Unit Cost,unit_cost` with values 2 and 20 gave `materials: 200.0` from the second column, and `--detect-only` showed `unit_cost: unit_cost` with no AMBIGUOUS flag. Exact duplicate `Unit Cost,Unit Cost` also ran OK at $200 (DictReader keeps the last). Fix: `detect()` now keeps every header that normalises to an alias, so the collision is `AMBIGUOUS:Unit Cost\|unit_cost` and the run stops until `--map`. Non-blank exact duplicate headers stop the script with a message (blank trailing Excel headers are still allowed). `--map` to a column that does not exist, or to an unknown field, now stops with a message instead of reading blanks. SKILL.md step 2 tells the agent to ask which column, not pick. | `test_f1_columns_that_normalise_to_one_name_are_ambiguous`, `test_f1_exact_duplicate_headers_exit_with_message`, `test_f1_blank_trailing_headers_are_not_duplicates`, `test_map_to_a_column_that_is_not_there_exits_with_message` |
| F2 | P0 | CONFIRMED | P0 | `evals.json` eval 2 expected answer allowed "uses an explicitly tagged ASSUMPTION value" and assertion 2 allowed "uses a value labeled ASSUMPTION", against `SKILL.md:80` "ask for a number they choose; you never pick one". Rewrote eval 2's expected answer and all four assertions: the reply must start with BLOCKED, name the missing solvent price, and ask for the real price or an operator-chosen placeholder. It must not pick or suggest one, even labelled, and must report no cost per jar, total, subtotal or biomass line cost. Overhead stays 12% of materials. Removed the "if it shows a biomass cost, ~$9,500" branch because a blocked run shows none. `SKILL.md:39` "proceed without a number" now says the operator chooses the placeholder; "use whatever" is not a number. The script's `how_to_fix` says the same. Eval 3 now says placeholders are operator-chosen. | `test_f2_eval2_without_an_operator_chosen_solvent_price_is_blocked` |
| F3 | P0 | CONFIRMED | P0 | Reproduced: a BOM at `cogs_out/cogs_lines.csv` run with the default `--out-dir` was overwritten with the report. Fix: before writing, the script stops if either output path resolves (realpath, or samefile for hard links) to the BOM. Overwriting earlier *reports* in the out-dir is intended and is not changed (DISAGREE with that part of the suggestion: they are regenerated outputs, not source data). | `test_f3_outputs_never_overwrite_the_bom` (both output names, direct and through a symlinked dir) |
| F4 | P0 | NOT REPRODUCED | n/a | The shared `to_number` now rejects \|v\| > 1e12, so `1e308` is BLOCKED with row, column and raw value. The largest accepted line (1e12 kg priced per mg at 1e12) costs 1e30, and with every flag at 1e12 the output is finite, strict JSON. No calculation can reach float overflow from capped inputs, so no code change. | `test_f4_largest_accepted_numbers_give_finite_output`; `BadNumbers` (huge, huge_plain) |
| F5 | P1 | CONFIRMED | P2 | `SKILL.md:90` said mixed weight/volume lines block "until the operator gives a density or conversion", but the script has no way to take one. It blocks safely, so this is a dead end, not a wrong number. Fix (the reviewer's smallest option): SKILL.md, the script message and the docs page now say the script applies no density. The operator restates the line in one kind of unit in the BOM. The agent never converts it, even when given a density. | `Structure.test_mixed_unit_kinds_are_blocked` (message updated) |
| F6 | P1 | CONFIRMED | P1 | Reproduced: `Oil,,ml,NaN,g` reported only the NaN cost. The blank quantity and the ml/g mix were hidden until reruns, against `SKILL.md:57` "it lists every problem, not just the first". Fix: the row loop collects bad numbers, a blank quantity, a missing price, and unknown or mixed units before moving on. Messages now carry location: `column 'Qty' is blank (quantity missing)`, `cost:<component> (row N): column '<col>' is blank`, `unknown unit '<u>' in column '<col>'`, and `Skipped N fully blank row(s) in the BOM: rows 7, 8.` | `test_f6_every_problem_in_a_row_is_listed_in_one_run`; updated `test_eval3_*`, `test_eval4_*`, `test_blank_required_cells_block_the_batch`, `test_unknown_unit_is_blocked` |
| F7 | P1 | CONFIRMED | P2 | `references/cost-elements.md:13` listed "per machine hour", which the script can't take. Fix: the reference and SKILL.md step 1 now say that, for another base such as machine hours, the agent asks for the overhead dollars charged to this batch and passes `--overhead-per-batch`. It never converts to labor hours. | none (docs only) |

P2 / notes from the review:
- Eval 5's sentence about what the "pre-fix script" did can't be checked from the current source, so I removed it from the expected answer. The assertions are unchanged.
- The trigger query "distillate goes up 15% … margins" is kept. It is a triggering test only, and the skill does cover unit-cost sensitivity. Margin needs a selling price the operator gives.
- A zero-byte BOM exits with a message, not BLOCKED JSON. This is unchanged and already covered by `test_empty_file_exits_with_message`.

## Known answers

Unchanged: eval 1 is $4,680.75 and $9.5137 per unit. The live-resin run with a $10/kg solvent placeholder is still $12,973.98 and $10.9949 (`test_eval2_live_resin_converts_kg_to_lb_and_tags_assumption`). That test now runs as an operator-supplied-placeholder case (comment on `EVAL2_ARGS`), not as eval 2's expected behaviour. Eval 2's expected answer changed for the reason under F2.

Changed message strings (not known answers): missing price is now `cost:<component> (row N): column '<col>' is blank`, matching the existing `cost_uom:<component> (row N): …` format. The `--assume` key is still `cost:<component>`.

## Checks

- `python3 -m unittest tests.test_cogs -v`: 38 tests OK (Python 3.14). `/usr/bin/python3 -m unittest tests.test_cogs`: 38 tests OK (Python 3.9.6).
- `python3 scripts/check_repo.py --no-cli`: 7324 checks passed, 0 failed.
- The shared `to_number` and `csv_safe` blocks are byte-identical across all five scripts (checked by hash).
- No `__pycache__` left behind.

## Shared-file changes needed

None.

## Open items

- `plugin-evals/` must be rebuilt for eval 2 (new expected answer and assertions), plus the small wording changes in evals 3 and 5. I did not run `build_suite.py`.
- No mixed-dimension conversion input (F5) was added. If operators often price oil per gram but meter it in mL, a validated per-line `--density` could come later.

## Round 2

Review: second independent reviewer (Claude), `REVIEW.md` § cannabis-batch-cogs, fresh-session trials and fact check, written against `a46f0fe`. Each finding was rechecked against the current tree (round 1 = `313a239`) by rerunning the reviewer's repro. Tests are in `tests/test_cogs.py`, class `Round2Regressions`. All seven new tests fail on the `313a239` script and pass on the fixed one.

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| C1 | P1 | CONFIRMED | P1 | Reproduced on the live tree: `Item,Qty,UOM,Cost,Cost UOM` holding line totals ran OK at $3,182.52 per unit (materials $1,565,041.25). Fix: a price column headed just `Cost` is detected as `CONFIRM:Cost`. `--detect-only` adds a `confirm` question. A run puts the question in `missing_inputs` and is BLOCKED, with every other missing input and problem still listed in the same run (one combined question). `--map unit_cost=Cost` is the operator's confirmation. If `Cost` is a line total, the agent asks for a per-unit export and never divides it. SKILL.md step 2 and the docs page say the same. The trial cogs1 BOM (`Item,Qty,UOM,Cost`) now raises the question too. | `test_c1_cost_header_must_be_confirmed_as_per_unit`, `test_c1_cost_header_question_comes_with_every_other_problem`; `test_eval3_preroll_thin_inputs_blocked` updated |
| C2 | P1 | ALREADY FIXED | n/a | Same-named columns stop the script with a message (round 1, F1). The reviewer's repro now exits 1 with "more than one column named 'unit_cost'". | `test_f1_exact_duplicate_headers_exit_with_message` |
| C3 | P2 | PART ALREADY FIXED, part CONFIRMED | P2 | `--map` naming a missing column has been rejected since round 1. Still reproduced: `Unit Cost ($)` wasn't detected (normalised to `unit cost ()`). Fix: `nh()` drops empty parentheses left after the `$` is removed. | `test_map_to_a_column_that_is_not_there_exits_with_message`, `test_c3_dollar_sign_in_parentheses_is_detected` |
| C4 | P2 | ALREADY FIXED | n/a | `1e200` is BLOCKED as "out of range", because the shared `to_number` rejects values with \|v\| > 1e12. | `test_f4_largest_accepted_numbers_give_finite_output`, `BadNumbers` |
| C5 | P2 | CONFIRMED | P2 | Both parts reproduced. Fix: `--overhead-pct-materials` over 100 adds an `input_problems` note asking the agent to confirm it, without blocking. An unknown `--assume` key (`labour_rate`), or one given with its own flag, now stops the script with a message. A `cost:`/`cost_uom:` key naming no BOM line blocks the batch. One naming a line whose cell is already filled is noted as not used. | `test_c5_overhead_pct_over_100_is_noted`, `test_c5_bad_assume_keys_are_not_ignored` |
| C6 | P2 | CONFIRMED | P2 | `cost_of_shortfall_per_unit` is −2.3722 when 100 units are made against 90 expected. I kept the key name, because the template, evals and SKILL.md use it. When actual units exceed expected, `yield_variance.note` says the figure is a saving per unit. SKILL.md step 4 tells the agent to report it that way. Eval 1's `yield_variance` is unchanged (no note on a shortfall). | `test_c6_over_yield_says_the_negative_figure_is_a_saving` |
| C7 | P2 | CONFIRMED (documented) | P2 | `"1,250"` kg is still read as 1,250 kg. That is intended: US thousands separators are documented. Fix: a weight or volume quantity in exactly the `1,250` form now adds a non-blocking `input_problems` note asking the operator to confirm it isn't 1.25. Count lines get no note, because a count can't be fractional. Eval 5's `1,200` jars is still not flagged. | `test_c7_single_group_comma_on_weight_line_is_noted` |
| C8 | P1 | CONFIRMED | P1 | Trial cogs2 transcript: the skill was loaded but never invoked. The agent hand-computed a materials-only figure, "about $21.52" per jar. Fix: the description now covers a batch, run or lot, cost per jar/cart/pre-roll/gummy/pack, and "shares a BOM or production cost file". It says "even if the sum looks simple: the bundled script does the roll-up, so never total a BOM by hand" (986 characters). The SKILL.md intro now says to run the script for every cost question, even when the operator sends only a BOM and a unit count. It never answers with a materials-only figure. The trial prompt is added to `evals/trigger_queries.json` as a should-trigger query. On that BOM the script returns BLOCKED, listing labor, overhead and testing. No rule was weakened. | none (description and trigger query; see open items) |

The fact-check section has no batch-cogs claims.

### Known answers

- Eval 1 ($4,680.75, $9.5137) and the live-resin placeholder run ($12,973.98) are unchanged.
- `test_eval3_preroll_thin_inputs_blocked` changed: `missing_inputs` gains the C1 `Cost` question. Reason: the eval 3 BOM header is `Item,Qty,Unit,Cost,Per`, and a bare `Cost` header must now be confirmed as per-unit.
- In `evals.json`, eval 3's expected answer now includes that question, and the eval gains a fifth assertion: "Asks whether the Cost column is the price per unit or the line total, in the same message, without assuming either".

### Checks

- `python3 -m unittest tests.test_cogs`: 45 OK (3.14). `/usr/bin/python3 -m unittest tests.test_cogs`: 45 OK (3.9.6).
- `python3 scripts/check_repo.py --no-cli`: 7526 passed, 0 failed.
- The shared `to_number` and `csv_safe` blocks are untouched and byte-identical across all five scripts (hash-checked). No `__pycache__` left.

### Shared-file changes needed

None.

### Open items

- `plugin-evals/` needs a rebuild for eval 3 (new expected text and fifth assertion) and the new trigger query. I did not run `build_suite.py`.
- C8 is fixed in the description and body, but not re-verified with a fresh-session trial. Trigger reliability needs repeated `claude -p` runs of the cogs2 prompt.
- Other `ALIASES` entries can also be ambiguous in ERP exports (for example `amount` under qty, which some ERPs use for a dollar total). It is AMBIGUOUS whenever a `Qty`/`Quantity` column is also present, so I left it unchanged.
