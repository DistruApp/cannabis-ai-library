# Plugin behaviour evals (Gate 4)

Cases for `claude plugin eval` (Claude Code 2.1.322 or later) covering the 10 promoted skills in `.claude-plugin/plugin.json`.

- `behaviour/<skill>/<case>/`: 69 cases. Every case in each skill's `evals/evals.json` (prefix `eN-`), plus safety cases: `s1-` asks it to send, submit or publish now; `s2-` leaves out a key input; `s3-` has a bad number in a fixture (script skills only); `s4-script-unavailable` runs without Bash (script skills only).
- `triggers/<skill>/<nn-pos|nn-neg>/`: 100 cases, one per entry in each skill's `evals/trigger_queries.json`. Each has a single `tool_used: Skill` grader. Negatives use `max: 0` with `arm: both`.
- `tools/build_suite.py`: generates both trees. It deletes and rewrites `behaviour/` and `triggers/`, and copies fixtures from each skill's `evals/files/`. Re-run it after you change a fixture, `evals.json` or `trigger_queries.json`: `python3 plugin-evals/tools/build_suite.py`. Change graders and safety cases in the script, not in the generated files.

## Tags

| Tag | Meaning | Run with |
|---|---|---|
| `needs-bash` | Script-skill cases. The agent must run the bundled script | `--allow-tools Bash` |
| `no-bash` | `s4-script-unavailable` cases. They pass only if the agent says it can't run the script and doesn't hand-compute the figures | No Bash grant |
| `bash-free` | Skills that have no script | Either. Run without Bash |
| `safety` | Send/submit refusals, missing inputs, bad numbers, plus the `evals.json` cases about the same things | |
| `send`, `nofab`, `bad`, `nobash` | The kind of safety case | |
| `trigger`, `trigger-pos`, `trigger-neg` | Trigger cases | |
| `<skill-name>` | One skill | |

## Running

Fixtures are copied into `./resources` in each run's workspace by the case's `setup.sh`, so behaviour runs need `--scaffold`. Always pass `--no-publish`. Put the target `.` first.

```bash
# 1. Script skills, with Bash
claude plugin eval . --eval-dir plugin-evals --tag needs-bash --allow-tools Bash --scaffold \
  --model sonnet --judge-model sonnet --ablation none --no-publish --trust-plugin -j 4 --max-cost-usd 40

# 2. No-Bash cases and skills without scripts
claude plugin eval . --eval-dir plugin-evals --tag no-bash bash-free --scaffold \
  --model sonnet --judge-model sonnet --ablation none --no-publish --trust-plugin -j 4 --max-cost-usd 15

# 3. Triggers
claude plugin eval . --eval-dir plugin-evals --tag trigger \
  --model sonnet --ablation none --no-publish --trust-plugin -j 4 --max-cost-usd 10
```

Drop `--ablation none` to add the no-plugin baseline (`W/OUT` and `Δ` columns). That roughly doubles the cost, and the `skill-fired` graders then count only as indicators. Under `--ablation none` they are scored. `--threshold` defaults to 1.0, so a case passes only if every grader passes in every run. One `--case '<name>'` reruns a single case.

`results/` is written here on every run and must be gitignored.

## Running against other models through pi

`tools/run_pi.py` plays the same cases against a non-Claude model through the `pi` CLI (standard library only). The default model is GPT 6.1 Sol (`openai-codex/gpt-6.1-sol`, thinking `high`):

```bash
python3 plugin-evals/tools/run_pi.py 'behaviour/*/*' 'triggers/*/*' --runs 2 -j 6 \
  --out plugin-evals/results/pi/gpt-pass1.json
python3 plugin-evals/tools/gate4_summary.py plugin-evals/results/pi/gpt-pass1.json
```

- Positional arguments are case globs relative to `plugin-evals/` (or case folder names). `--tag` keeps cases that have any of the listed tags. `--exclude-tag` defaults to `needs-bash`.
- The pi agent gets only the `read` tool. All ten skills are loaded with `--skill`, and pi's own skill, extension, MCP and context-file discovery is turned off. Cases tagged `needs-bash` are skipped.
- At start the runner copies `skills/` and the matched case folders to a temp snapshot and runs everything from it, so edits made during a long run don't mix two versions into one result. The git HEAD and dirty paths at start are saved under `tree`.
- Each run gets a fresh temp directory, and the case's `setup.sh` copies `resources/` into it. `append_system_prompt` is passed through. `timeout_seconds` is enforced (x `--timeout-mult`, default 2). `max_turns` is not, because pi has no flag for it.
- Skill detection: pi has no Skill tool. A skill counts as fired once for each `read` of a path ending in `<skill-name>/SKILL.md`, and the `tool_used: Skill` grader's `input_match`, `min` and `max` are applied to those reads.
- `regex` graders check the final assistant message. `llm` graders use a pi judge (`--judge-model`, thinking `medium`, no tools) that must answer strict JSON. The judge votes 3 times, 2 of 3 must pass, and a malformed vote counts as a fail. `file_exists` and `baseline` graders are N/A and left out of the score.
- Score per case is the mean over completed runs of graders passed / graders scored. On a usage limit, pi calls back off and retry (`--retries`, `--backoff`). Runs that still fail are left out of the mean and mark the result `partial`.
- The JSON keeps each run's final text, tool calls, skills read and every grader's reason. Raw pi events go in `<out>-raw/`. `costUsd` is always 0.

## How the runs are set up

These points come from the 2026-11-11 pilot:

- The plugin loads in place from the repo. The Skill tool reports the base directory as the real skill folder, so runs exercise the working tree as it is.
- Sandboxed Bash can run the bundled scripts (`python3 <skill-dir>/scripts/*.py`) and write to `$TMPDIR` and the workspace.
- Sandboxed Bash cannot read `context.add_dirs` folders, because the case folder is under the home directory: `Operation not permitted`. The Read tool can read them. That is why fixtures are staged with `scaffold_script` instead of `add_dirs`.
- The Read and Grep tools can read the skill's `references/` and `assets/`.
- The last message is graded. `append_system_prompt` asks the agent to put its full reply in the final message rather than only in a file.
