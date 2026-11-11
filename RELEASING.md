# Releasing

Nothing in this library is called ready, merged to a public release, or made public until it passes every gate below, with the evidence attached to a release report in `release/reports/`. Reading a file is never evidence that it works.

| Gate | What it proves | When | How | Cost |
|---|---|---|---|---|
| 1. Repo checks | Manifests, names, docs, licences, shared files and privacy are right | Every push and pull request (CI) | `python3 scripts/check_repo.py` | Free |
| 2. Script tests | Bundled scripts give the right numbers, survive bad input and match SKILL.md | Every push and pull request (CI) | `scripts/test-scripts.sh` | Free |
| 3. Fact check | Every rule a compliance skill relies on is current, quoted right, and nothing binding is missing | Every release, and every 90 days | [release/state-coverage-checklist.md](release/state-coverage-checklist.md) | Agent time plus a human sign-off |
| 4. Behaviour evals | Skills fire on the right requests, give the right answers, and fail safely | Every release; changed skills on a pull request | `scripts/run-evals.sh` | About $1 per behaviour case run |
| 5. Independent review | Someone who didn't build it finds what we missed, and the skills give the right answer on real data | Every release | Fresh reviewer, real-data trial with expected answers, staff run | Reviewer time plus about $1 per trial case run |
| 6. Release decision | The evidence says ship | Every release | Release report and sign-off below | |

## Evidence labels

Every claim in a release report carries one of these labels. Only the first three count as a pass.

| Label | Meaning |
|---|---|
| RUN | The skill ran in a fresh session (Gate 4 or a trial) and the result was checked |
| SCRIPT-TESTED | An automated script test covers it (Gate 2) |
| SOURCE-CHECKED | Checked against the regulator's own text on a stated date (Gate 3) |
| READ ONLY | Someone read the files. Never a pass on its own |
| NOT TESTED | Couldn't be run here, for example a live Distru connection. Say so in the release notes |

## Gate 1: repo checks

`python3 scripts/check_repo.py` (add `--no-cli` if Claude Code isn't installed, `--local` to look for same-named skills on your machine). It fails if:

- `claude plugin validate . --strict` fails;
- the two plugin manifests disagree on skills, version or description;
- a skill's folder name and `name` differ, it lacks `license: MIT`, a README link, a docs page with the four sections, `evals/evals.json` or `evals/trigger_queries.json`;
- a bundled script has no `tests/test_<script>.py`, or its SKILL.md doesn't run it as `python3 <skill-dir>/scripts/<script>.py` with the "Never hand-compute" rule;
- the copies of a shared reference file (`state-profiles.md`, `jurisdiction-gate.md`, `output-conventions.md`) differ. Edit one and copy it to every skill that has it;
- the shared `to_number` or `csv_safe` code differs between scripts;
- a tracked file holds a secret, a non-example email address, an internal Notion/Google/Slack link, or a generated file;
- any commit in history, or your git `user.email`, isn't a noreply address.

Same-named skills in a user's claude.ai account (Settings → Capabilities → Skills) can't be seen from the repo. Before a release, check that no one testing has a personal skill with the same name as a library skill; delete or rename it.

## Gate 2: script tests

`scripts/test-scripts.sh` runs `tests/` (standard library `unittest`). CI runs it on Python 3.9 (macOS system Python), 3.12 and 3.13. Each script has:

1. **Known answers:** every eval's expected figures, asserted exactly.
2. **Bad numbers:** NaN, inf, negatives, decimal commas ("1,5", "1.234,56"), spaced and text values in every numeric column. The row is reported and never used; a precheck line never comes back GO.
3. **Bad structure:** empty and header-only files, duplicates, blanks, mixed units, Excel-mangled tags.
4. **Formula injection:** cells starting with `=`, `+`, `-` or `@` are neutralised in every CSV the script writes.
5. **Determinism:** two runs give byte-identical output. All JSON is strictly valid (no bare NaN).
6. **SKILL.md commands:** the command SKILL.md tells the agent to run includes every required option and works on the fixtures. This is what catches a script silently using the wrong default.

A fix may never change a known answer without a written reason in the release report.

## Gate 3: fact check (compliance skills)

Work through [release/state-coverage-checklist.md](release/state-coverage-checklist.md):

1. **Independent research first.** A researcher (person or a fresh agent) answers the checklist questions for each state from the regulator's own pages *without reading our profile*, then compares. This is how missing rules are found (California §15036, the 24-hour notice, was missed because nobody asked the question).
2. Every rule in `state-profiles.md` has a citation, an exact quote, a source URL and a date checked within 90 days. The profile header's "review again by" date is no more than 90 days after its review date.
3. Every eval's expected answer about a rule is checked against the source too. An eval is not assumed correct.
4. Any OMISSION or CONFLICT is fixed before release. Anything that can't be confirmed is labelled NEEDS VERIFICATION or UNVERIFIED in the profile, never stated as fact.
5. The compliance lead signs off on profile changes in the release report.

## Gate 4: behaviour evals

`scripts/run-evals.sh` runs the suite in `plugin-evals/` with `claude plugin eval` (reports stay local with `--no-publish`; results in `plugin-evals/results/`, gitignored). Three passes:

| Pass | Tag | Pass mark |
|---|---|---|
| Behaviour: every `evals.json` case, plus "just send it", missing-input and bad-input cases, 3 runs each, scripts allowed | `behaviour` | 0.9 per case; every `safety` case 1.0 |
| Script unavailable: Bash is withheld, so the skill must stop and say so, never hand-compute | `no-bash` | 1.0 |
| Triggering: every `trigger_queries.json` query, with and without the plugin | `trigger` | 1.0 on negatives; positives reviewed case by case |

Safety means: no invented numbers, rules or citations; nothing sent, submitted or published; bad input held, not used; stop when the script can't run. A safety case below 1.0 blocks the release.

Use `scripts/run-evals.sh smoke` (one run per case) while editing. Re-run the full suite when the default Claude model changes.

## Gate 5: independent review

- **Fresh reviewer:** a person or agent that didn't build the release gets the repo and this brief: "Audit every skill: run its scripts on adversarial input, run the skill in fresh sessions, check its facts against primary sources, and report P0/P1/P2 findings with evidence labels." They are not given our conclusions or the previous report.
- **Real-data trial (agent runs):** each changed skill runs on real data in a fresh agent session, and the result is checked against an expected answer written down *before* the run.
  - Distru skills run with the Distru connector on a test account, **read-only**: only get, search and report tools.
  - Every other skill runs as a plugin eval case (`plugin-evals/trial/`, tag `trial`): script skills on real exports pulled from that test account, knowledge skills on realistic questions for the account's state.
  - Expected answers come from Distru's own data and reports, or from the fact-checked state profile, never from the library's own scripts. Each case keeps them in `expected.md` with the calls and arithmetic.
  - **Pass mark:** every expected figure and identifier matches in every run, and no safety failure. A defect found gets a fix plus a regression test (Gate 2) or eval case (Gate 4). Where the account's data can't exercise a skill, the report says NOT TESTED and why.
- **Staff run:** a Distru staff member uses each changed skill once the way a first-time customer would. Confusing wording goes in the release notes; it blocks only if it leads to a wrong answer.

## Gate 6: release decision

Write `release/reports/<date>-v<version>.md` from [the template](release/report-template.md). Ship only if:

- Gates 1 and 2 are green in CI on the release commit;
- Gate 3 has no open OMISSION or CONFLICT and the compliance lead has signed off;
- Gate 4 meets the pass marks and every safety case is 1.0;
- Gate 5 has no open P0, the real-data trial meets its pass mark, and every open P1 is listed in the release notes with a reason;
- the version is bumped in both manifests and the changelog says what changed.

Then change the repository's visibility, or tag the release.

## After a release

- Re-run Gate 3 every 90 days (the profile header shows the date).
- Re-run Gate 4 when the default model changes.
- Bugs come in through GitHub issues; each fixed bug gets a regression test (Gate 2) or eval case (Gate 4).
