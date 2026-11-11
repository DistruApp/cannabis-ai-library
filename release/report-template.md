# Release report: v<version> (<date>)

Commit: `<sha>`. Prepared by: <name>. Process: [RELEASING.md](../RELEASING.md).

## Decision

**Ship / Don't ship.** One paragraph: why, and what is knowingly left open.

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| 1. Repo checks | PASS / FAIL | CI run link, or `scripts/check_repo.py` output tail |
| 2. Script tests | PASS / FAIL (n tests) | CI run link, Python versions |
| 3. Fact check | n MATCH, n OMISSION fixed, n CONFLICT fixed, n COULDN'T-VERIFY | Researcher report; compliance lead sign-off |
| 4. Behaviour evals | Per-pass scores; safety cases all 1.0? | `plugin-evals/results/...` (local), model, judge, cost |
| 5. Independent review | n P0 / n P1 / n P2 open; trial n of n cases met the mark | Reviewer report; `release/reports/<date>-trial/`; staff run notes |

## Per-skill status

| Skill | Gate 2 | Gate 4 behaviour | Gate 4 safety | Gate 4 triggers | Open issues | Evidence label |
|---|---|---|---|---|---|---|

## Changes since the last release

## Known limits shipped (release notes)

Anything NOT TESTED (for example the live Distru connection) or COULDN'T-VERIFY, and every open P1 with its reason.

## Sign-off

| Role | Name | Date |
|---|---|---|
| Release owner | | |
| Compliance lead (Gate 3) | | |
| Independent reviewer (Gate 5) | | |
