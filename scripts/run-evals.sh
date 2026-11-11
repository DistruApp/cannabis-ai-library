#!/usr/bin/env bash
# Gate 4: run the behaviour and trigger evals with `claude plugin eval`. See
# plugin-evals/README.md.
#
#   scripts/run-evals.sh            full release run: 3 passes, 3 runs per behaviour case
#   scripts/run-evals.sh smoke      one run per behaviour case (cheap check while editing)
#
# Reports stay local (--no-publish). Results land in plugin-evals/results/ (gitignored).
# --scaffold runs each case's setup.sh, which only copies that case's fixtures into the
# run's workspace (sandboxed Bash can't read add_dirs under the home folder).
# Regenerate the cases after changing any skill's evals/ files:
#   python3 plugin-evals/tools/build_suite.py
set -uo pipefail
cd "$(dirname "$0")/.."
MODEL="${EVAL_MODEL:-sonnet}"
JUDGE="${EVAL_JUDGE:-sonnet}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="plugin-evals/results/release-$STAMP"
mkdir -p "$OUT"
COMMON=(--eval-dir plugin-evals --model "$MODEL" --judge-model "$JUDGE" --no-publish --trust-plugin -j 4 --ablation none --threshold 0)
RUNS=()
[ "${1:-}" = "smoke" ] && RUNS=(--runs 1)

echo "== 1/3 script skills, scripts allowed"
claude plugin eval . "${COMMON[@]}" "${RUNS[@]}" --tag needs-bash --allow-tools Bash --scaffold \
  --max-cost-usd "${EVAL_MAX_COST_BASH:-40}" --json "$OUT/needs-bash.json" --report "$OUT/needs-bash.html"
echo "== 2/3 script unavailable (no Bash) and skills without scripts"
claude plugin eval . "${COMMON[@]}" "${RUNS[@]}" --tag no-bash bash-free --scaffold \
  --max-cost-usd "${EVAL_MAX_COST_NOBASH:-15}" --json "$OUT/no-bash.json" --report "$OUT/no-bash.html"
if [ "${1:-}" != "smoke" ]; then
  echo "== 3/3 triggering"
  claude plugin eval . "${COMMON[@]}" --tag trigger --runs 1 \
    --max-cost-usd "${EVAL_MAX_COST_TRIGGER:-10}" --json "$OUT/triggers.json" --report "$OUT/triggers.html"
fi
# --threshold 0 above so every pass finishes; the release pass marks are applied here.
python3 plugin-evals/tools/gate4_summary.py "$OUT"/*.json
