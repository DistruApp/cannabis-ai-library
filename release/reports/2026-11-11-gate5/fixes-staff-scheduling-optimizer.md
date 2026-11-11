# Gate 5 fixes: staff-scheduling-optimizer

Skill: `skills/cannabiz-skills/operations/staff-scheduling-optimizer/` (no script, so no unittest). Review: `pi-staff-scheduling-optimizer.md`. Built on the files as changed by this morning's triage pass.

Verification was by quoting lines and redoing the arithmetic. The roster caps total 34+34+34+28+32+30+25 = 217 hours. The example's assignments re-add to 29 shifts, 174 hours and $3,120.

## Findings

| ID | Reviewer | Verdict | Mine | Evidence and fix | Regression |
|---|---|---|---|---|---|
| F1 | P0 | CONFIRMED | P1 | `SKILL.md` step 3.5 said "Headcount is the larger of the demand number and the minimum, plus fixed roles". With 12 peak transactions, a rate of 12, a 2-person site minimum and an ID checker, that gives max(1,2)+1 = 3; the right answer is 2. Re-rated P1: it overstaffs a draft the manager approves and breaks no safety rule. **Fix:** demand staff = floor staff + fixed roles; headcount = max(demand staff, site minimum); a role or certification rule fills a slot and doesn't add a person. The example's formula text now says this. Its numbers are unchanged, because they already matched the corrected rule. | New eval 4 `fixed-role-counts-toward-minimum` (expects 2, not 3) |
| F2 | P1 | CONFIRMED | P1 | "Do the same with units per worker-hour and the batch or output target instead of transactions" makes 480 ÷ 20 = 24 read as workers. **Fix:** worker-hours = target ÷ throughput in matching units, then workers = worker-hours ÷ productive hours each, rounded up. Ask how many productive hours there are; worked example 480/20/6 = 4. | New eval 5 `production-worker-hours-to-workers` |
| F3 | P0 | CONFIRMED | P0 | The output required "What changed vs. current schedule" without asking for one. The example invented "Current (flat 3 per shift)" = 252 h / $4,483 and claimed "72 fewer hours and about $1,255 less labor". That 252 h exceeds the roster's 217 total cap hours. This breaks the no-invented-numbers rule. **Fix:** the current schedule is now an optional input. The section is shown only when the current schedule is supplied; otherwise the output says it wasn't provided and gives no savings figure. The example's baseline column, the savings sentence and the docs' "down from a flat 252" are removed. | Eval 1 assertion "Does not report hours or cost saved against a current schedule; says none was provided" |
| F4 | P1 | CONFIRMED | P1 | The Sunday options asked Dave or Jen to volunteer (each would reach 36 of 34 hours). They also said certifying Mike or Amy "fixes every future Sunday", but Sunday has three eligible people for four slots. **Fix:** step 4 now requires each named person's hours after the change and their remaining blockers. Only people within their cap are named; the rest are marked not an option. Certification counts as a fix only if a person is also available. The example's options are now a table with hours and blockers. Certification is conditional on Tom's renewal (then Lisa + Amy open, Mike + Tom close; Tom 24 of 32). | Eval 1 expected output (options show resulting hours) |
| F5 | P1 | CONFIRMED | P1 | The example said "**Overtime:** none this week", and eval 1 expected "no overtime", with no jurisdiction or workweek given. **Fix:** the skill reports what it checked and leaves applicability to confirm. The example now says no one is above 30 hours and adds a compliance item on thresholds and the workweek. | Eval 1 assertion "Does not state 'no overtime' as settled…" |
| F6 | P1 | CONFIRMED | P2 | There was no validation step for blanks, placeholders, zero denominators, duplicates, units or formulas. Instruction-level only; re-rated P2. Fixed anyway because the fix is short: "Check the inputs before using them". It skips blank and `EXAMPLE` rows, treats placeholders, non-numbers, zero or negative denominators and formulas as missing, asks about duplicate people, and confirms units. | None (no script) |
| F7 | P1 | CONFIRMED | P1 | The skill said "Don't schedule them **after** the expiry date"; eval 1 said "on or after". **Fix:** the skill now says "on or after", unless renewal or validity through the shift is confirmed. The expiry day is NEEDS VERIFICATION, and the rule is labelled the skill's conservative default, not a legal rule. The example's Tom flag and a new compliance item now match. | Eval 1 assertion (unchanged; skill now agrees with it) |
| F8 | P1 | CONFIRMED | P2 | Eval 1 gave no jurisdiction or current hours, but expected a full schedule. **Fix:** the eval 1 prompt now supplies them: one store in Example State (fictional), every employee needs a credential, labor rules to be confirmed with HR, no other hours, and no current schedule to compare. The example's inputs say the same. Eval 2 now also expects a request for the transaction history and roster, because `files` is empty. | Eval 1 prompt; eval 2 assertion |
| F9 | P1 | CONFIRMED | P1 | The docs said "a draft schedule of 180 hours … about 17.7 percent". In fact 174 hours were assigned ($3,120, 17.1%), plus a 6-hour gap; 17.7% assumed the gap filled at an arbitrary $18. **Fix:** the output format and example now show required, assigned and open-gap hours separately. The filled-gap cost is conditional and uses the rate of the only within-cap volunteer, Sarah at $19: $3,234, 17.8%. The docs were rewritten to match. | Eval 1 assertion "Reports required, assigned and open-gap hours separately…" |

## Known-answer changes (eval 1 and 2)

- Eval 1 prompt: added the jurisdiction, no other hours and no current schedule (F8). Expected output: "no overtime" became "no one above 30 hours, applicability to confirm" (F5). "a labor summary around 180 hours" became 180 required, with assigned and gap hours shown separately (F9). Added "no comparison with a current schedule" (F3). Added "the ID checker counts toward the minimum" (F1). Added "options show resulting hours" (F4). There are three new assertions. The 245-hour budget, the headcount table and the Sunday OPEN GAP are unchanged.
- Eval 2 expected output now also asks for the unattached history and roster.
- Evals 4 and 5 are new. Their answers were checked by hand: 12 ÷ 12 = 1, plus 1 checker = 2 ≥ 2, so 2. 480 ÷ 20 = 24 worker-hours; 24 ÷ 6 = 4 workers.

## Files changed

`SKILL.md`, `examples/sample-output.md`, `evals/evals.json`, `docs/cannabiz-skills/operations/staff-scheduling-optimizer.md`.

## Shared-file changes needed

None.

## Open items

- Suite rebuild is needed for the eval 1 and 2 changes and the new evals 4 and 5.
- Not run against a model; these are instruction and example fixes checked by hand.
- Template (`templates/schedule-input-template.csv`) is unchanged. Its `EXAMPLE` rows, blank rows and `YYYY-MM-DD` are now covered by the input-check rule rather than by editing the template.
