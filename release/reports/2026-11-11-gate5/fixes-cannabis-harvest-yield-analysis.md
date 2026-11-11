# Gate 5 fixes: cannabis-harvest-yield-analysis

Review: `pi-cannabis-harvest-yield-analysis.md`. Paths are relative to `skills/cannabiz-skills/operations/cannabis-harvest-yield-analysis/` unless they start with `docs/` or `tests/`.

## Findings

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| F01 | P0 | CONFIRMED | P1 | `evals/files/harvests_2026_q3.csv` row 9 is `BD-F1-1004,…,2026-10-04`, but eval 1's prompt, the SKILL.md example and the docs example called all 8 rows "Q3". The script run on the 7 calendar-Q3 rows gives 76,208.2 g / 168.01 lb, Flower 1 28.57 g/sq ft and three gaps, as the reviewer said. **Eval 1's expected figures are not changed.** They are right for the 8 rows the file holds (the reviewer re-traced them). What was wrong was the period label, so eval 1's prompt, the SKILL.md example and the docs example now say "July through early October" / "12 July to 4 October". The fixture keeps its name and rows, because `plugin-evals/tools/build_suite.py` and the cogs skill (`BD-F1-1004` smalls) refer to them. New SKILL.md rule (Step 1, **Period**): check the harvest dates against any period the user names, name the batches outside it, ask, and label figures by the dates they cover until the operator answers. Added a "period covered" line to the final-reply checklist and the report template. New eval 6 tests this period check on the same file with a "Q3" prompt. | `test_eval6_calendar_q3_without_the_october_batch` |
| F02 | P0 | CONFIRMED | P0 | `Batch,Wet,Dry,Dry,Unit` / `H1,5000,1000,2000,g` gave 2,000 g and 60% dry-down with no problem. Headers that match after ignoring case, spaces and underscores (`Dry Weight` / `dry_weight`) did the same. The script now stops with exit 1, naming the columns, before detection (so `--detect-only` stops too) and before writing any output. Blank headers are ignored. SKILL.md Step 2 says to ask which column is right. | `test_duplicate_column_names_stop_the_run` |
| F03 | P0 | CONFIRMED (in part) | P1 | The reviewer's case (`1e308` kg) is **NOT REPRODUCED**: the shared `to_number` now rejects values over 1e12 (`out of range: '1e308'`). Tiny denominators still overflowed. `1e12` kg over a `1e-300` sq ft canopy raised a traceback and left a half-written `summary.json`. A `1e12` cost over a `1e-300` g dry weight wrote `inf` into `yield_by_batch.csv`. Fix: a nonzero value under 1e-6 (`_MIN_ABS`, defined outside the shared block) is reported and treated as blank, so every ratio is at most about 1e23. As a backstop, the summary and batch rows are serialized with `allow_nan=False` before any file is written. A non-finite result exits with a message, and no output is written. | `test_tiny_values_never_overflow_or_leave_partial_outputs` |
| F04 | P1 | CONFIRMED | P1 | All three cases reproduced: A=dry with no B/trim/waste columns gave `OK`, an all-blank breakdown gave `NO_BREAKDOWN` with no problem line, and A 800 + B 300 with trim blank on 1,000 g dry gave only `INCOMPLETE_BREAKDOWN`. Fix: a part with no column counts as missing, so the batch is `INCOMPLETE_BREAKDOWN`, with one file-level problem naming the absent columns. An all-blank breakdown on a batch with a dry weight now gets a problem line. Recorded parts that exceed dry weight give `PARTS_EXCEED_DRY` even when other parts are blank. SKILL.md's sum-check text is updated, and `NO_BREAKDOWN` is now documented. | `test_breakdown_completeness_and_excess` |
| F05 | P1 | CONFIRMED | P2 | `"5,000"` lb was read as 5,000 lb with no note. This is documented behaviour of the shared `to_number`, but in a file that uses a decimal comma it is wrong by 1,000 times. The shared code is unchanged. `yield.py` now adds one file-level `input_problems` line listing the comma-read cells (up to three, then "...") and asking to confirm the number format. SKILL.md Units also says to confirm it. | `test_us_thousands_separator_is_read` (updated: see "Known answers changed") |
| F06 | P1 | CONFIRMED | P1 | SKILL.md said "compared per plant only" even when there were no plant counts. With no canopy column, groups kept file order (A at 100 g/plant ranked before B at 200 g/plant). Fix: the script ranks by g/sq ft, else by g/plant, else by g/light. A new `ranking_metric` field in the summary names the metric, or is `null` when no ranking is possible, and groups then keep file order. The key names `by_*_ranked_by_g_per_sqft` stay the same so nothing that reads them breaks. In SKILL.md, the Interpret step and the final-reply checklist now follow `ranking_metric`: no recommendation when it is `null`. Eval 2's assertion now reads "only a per-plant comparison can be made". | `test_ranking_falls_back_when_canopy_is_missing` |
| F07 | P0 | CONFIRMED | P1 | SKILL.md:94 said "Label it as still curing in the report" for any blank dry weight. It now says to report "dry weight missing", ask whether the batch is still curing, and call it still curing only if the operator or their records say so. The report template's coverage example no longer says "still curing". The docs page no longer says "such as one still curing". Eval 4 is unaffected, because its operator states that EX-R1-0829 is still curing. | SKILL.md text (no script change) |
| F08 | P1 | CONFIRMED | P2 | `references/interpreting-yield.md`: "dry weight taken before the cure finished" makes the dry weight heavier, so it lowers dry-down (1,000 g dry → 80%, 1,200 g dry → 76% on 5,000 g wet). It was listed under "much higher". It is now replaced with "dry weight taken after material was removed (bucked/trimmed dry vs. total dry plant material)", and the unit mix-up example now says it is the dry weight entered in the wrong unit. The "lower" row already had the early dry weight. | n/a (reference text) |

P2s also fixed: added a close-out trigger query to `evals/trigger_queries.json` (the reviewer noted none existed). Eval 5's expected output now mentions the thousands-comma confirmation line.

## Known answers changed (with reason)

- `tests/test_yield.py::test_us_thousands_separator_is_read`: `input_problems` used to be `[]`. It is now the single thousands-comma confirmation line (F05). The value read is unchanged (62,000).
- `test_every_eval_with_files_is_covered`: {1,2,4,5} → {1,2,4,5,6}, because eval 6 was added (F01).
- Eval 1: prompt wording and the start of the expected output only. Every figure is unchanged (see F01).
- No other eval or test figure changed. Eval 4's `len(input_problems) == 5` and eval 5's figures still pass.

## Shared-file changes needed

- None in the shared `to_number` / `csv_safe` blocks. They are byte-identical across all five scripts (checked by hash). `_MIN_ABS` lives outside the shared block in `yield.py`.
- Suggestion only, for the other four scripts: if they divide by a parsed value, the same tiny-denominator overflow (a nonzero value under about 1e-6 with a numerator near 1e12) probably applies. If you want this handled in the shared code, `to_number` could reject `0 < abs(v) < 1e-6` and return `"too small to be a real figure"`.

## For the orchestrator (outside my files)

- `plugin-evals/tools/build_suite.py` has scenarios s1–s4 for this skill that use `harvests_2026_q3.csv` with "Q3 harvests attached". The new period rule means an agent will now (correctly) point out `BD-F1-1004` (2026-10-04). s3 (`flower2-24-75`, "quick answer") should still pass, since the rule says to label the figures, not to withhold them. If you want those scenarios to test other behaviour, change "Q3 harvests attached" to "Harvests since July attached" in s1–s4. The `e1` prompt comes from evals.json, so it updates when the suite is rebuilt. Rebuild the suite to pick up eval 6.

## Open items

- `references/system-mappings.md` Metrc endpoint and `last-compliance-review` date are unverifiable (reviewer's "could not check"): not P0/P1, left as is.
- There is no date filter in the script. Scoping to a period means running on a copy of the file after the operator confirms, as SKILL.md now says.

## Checks

- `python3 -m unittest tests.test_yield -v`: 42 tests OK (Python 3.14). `/usr/bin/python3 -m unittest tests.test_yield`: 42 tests OK (Python 3.9.6).
- `python3 scripts/check_repo.py --no-cli`: Gate 1, 7324 checks passed, 0 failed, 0 warnings.
- No `__pycache__` created (`PYTHONDONTWRITEBYTECODE=1`).

## Round 2

Review: second independent reviewer (Claude), `REVIEW.md` section "cannabis-harvest-yield-analysis", plus the "Fresh-session trials" (yield1, yield2) and "Fact check" sections. That review was written against `a46f0fe`. Each finding was re-checked against the current tree (round 1 committed as `313a239`).

| ID | Reviewer | Verdict | Mine | Fix or reason | Regression test |
|---|---|---|---|---|---|
| Y1 | P1 | CONFIRMED | P1 | Reproduced on the live tree: `Blue Dream` / `Blue Dream ` / `blue dream` gave three strain groups (3.0, 2.5, 2.0 g/sq ft) and `input_problems: []`. Fix: strain and room groups use `name_key()` (case and repeated spaces ignored, the same rule as the replenishment planner's `sku_key`). The group shows the first spelling with spacing tidied. Each name written more than one way gets one `input_problems` line listing every spelling and its rows, and those batches are flagged `STRAIN_VARIANTS` / `ROOM_VARIANTS`. `yield_by_batch.csv` keeps each name as written. Names spelled differently (`GMO Cookies` / `GMO Cookie`) are never merged. SKILL.md Step 3 says to report the line and to ask before treating differently spelled names as one. The report template and docs page mention it. | `test_strain_and_room_spelling_variants_are_grouped_and_reported` |
| Y2 | P2 | ALREADY FIXED | n/a | Round 1 F03. Rerun of the reviewer's repro: `1e308` is rejected by the shared `to_number` as out of range, and `1e-320` as too small (`_MIN_ABS`). Exit 0, no traceback. | `test_tiny_values_never_overflow_or_leave_partial_outputs` |
| Y3 | P2 | CONFIRMED | P2 | Reproduced: `Wet Wt.`, `Strain(s)` and `Unit Of Weight` were not matched. Added the aliases `wet wt.`, `dry wt.`, `strain(s)` and `unit of weight` to `ALIASES` and to the harvest table in `references/system-mappings.md`. `Name` was **not** added as a harvest ID alias: it is too generic to match safely, and `--map harvest_id=Name` handles it. The aliases are still unverified hints (not tested against a real Metrc export). | `test_metrc_style_header_punctuation_is_matched` |
| Y4 | P1 | CONFIRMED | P1 | Trial yield1: the skill was listed as available but didn't fire. The agent read the file and compared two named strains by hand. The description only said "which strains or rooms perform best". Fix: the description now covers "whether one named strain or room beats another", a harvest log "file or pasted", and "Use it even if ... the question looks quick: its script does the math, never sum or compare harvests by hand" (996 characters, under the 1,024 limit). SKILL.md Step 1 now says to go straight to Step 2 when the file has already been shared, without computing totals or a comparison first. Added the yield1-style prompt to `evals/trigger_queries.json` (should trigger) and to the docs page's "When to use it". No rule was weakened. | Trigger query (n=1 in trial; not re-run here) |

Trial yield2 passed. Its only note (a garbled dry-down sentence in the agent's reply) is about the agent's wording, not a skill instruction, so no change. The fact check covered only the shared `references/state-profiles.md`, which this skill doesn't use, so there is nothing to act on here.

### Known answers changed

- None. Every eval and existing test figure is unchanged. The eval fixtures have no strain or room spelling variants, so no `input_problems` count moved.

### Shared-file changes needed

- None. The `to_number` and `csv_safe` blocks are byte-identical across all five scripts (checked by hash).

### For the orchestrator

- `evals/trigger_queries.json` gained one should-trigger query. Rebuild the suite to pick it up.
- Y4 was a single sample. Re-run the yield1 trial against the new description to confirm the skill fires.

### Checks

- `python3 -m unittest tests.test_yield`: 44 tests OK (3.14). `/usr/bin/python3 -m unittest tests.test_yield`: 44 tests OK (3.9.6).
- `python3 scripts/check_repo.py --no-cli`: Gate 1, 7526 checks passed, 0 failed, 0 warnings.
- No `__pycache__` created (`PYTHONDONTWRITEBYTECODE=1`).
