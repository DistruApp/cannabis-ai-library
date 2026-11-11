---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs the script with no default units (none were stated). Reports ...301 count rows 500 g + 1.1 lb summed after converting to g (998.951 g, SHORT_IN_COUNT -1.0488 g); ...302 two identical 50 ea rows NOT summed (DUPLICATE_CONFLICT, a possible copy-paste double entry, so no MATCH against the system's 100 ea); ...303 (blank quantity + 500 g) and ...304 (12 ea + 300 g) as DUPLICATE_CONFLICT with each row listed and no quantity compared; ...305 (blank count unit) and ...320 (blank system unit) as MISSING_UNIT with no unit borrowed from the other file; ...306 (2 lb vs 907.2 g) as a small +0.016 g OVER_IN_COUNT (no automatic rounding allowance; the note says scale resolution or a rounded factor could explain it); ...307 (1 lb vs 453.0 g) as a real -0.592 g shortfall; ...311 / ...313 kept as IN_SYSTEM_NOT_COUNTED and COUNTED_NOT_IN_SYSTEM with a near-match note, the counted-not-in-system row ranked high priority. Net weight -1.6248 g on 3 quantity-compared packages (system_total_compared 2360.776 g, -0.069%; gross 1.6568 g), with the not-compared rows listed next to the total reading. Every input_problems line appears in the report; asks the operator for the missing units and to fix the duplicate rows before rerunning.

PASS only if ALL of these hold:
- Reports ...301 as summed after converting to grams (998.951 g) and SHORT_IN_COUNT by 1.0488 g, not as a 500 g or 1.1 unit count
- Reports ...302 as DUPLICATE_CONFLICT: two identical 50 ea rows that were not summed because they may be a copy-paste duplicate, and does not call it a match
- Reports ...303 and ...304 as DUPLICATE_CONFLICT, lists each row's quantity and unit, and does not state a variance for them
- Reports ...305 and ...320 as MISSING_UNIT, names which file's unit is blank, and does not assume grams or pounds for the blank side
- Reports ...306 (2 lb vs 907.2 g) as a +0.016 g OVER_IN_COUNT, not a match, and ...307 (1 lb vs 453.0 g) as a -0.592 g shortfall
- Keeps ...311 and ...313 as separate open variances (not counted / counted not in system) and mentions the possible tag typo only as something to check on the label
- States the net weight variance as -1.6248 g (or -1.6 g) on quantity-compared packages and lists the packages left out of that total
- Includes every input_problems entry in the report

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
