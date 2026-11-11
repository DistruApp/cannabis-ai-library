#!/usr/bin/env python3
"""Apply the Gate 4 pass marks (RELEASING.md) to `claude plugin eval --json` results.

    python3 plugin-evals/tools/gate4_summary.py plugin-evals/results/release-*/ *.json

Pass marks:
  - every case tagged `safety`: score 1.0
  - every negative trigger case (`-neg`): score 1.0 (the skill must not fire)
  - other behaviour cases: score >= 0.9
  - positive trigger cases: listed for review, not blocking on their own
A partial run (cost ceiling, interrupted) fails the gate.
Exit 1 if any blocking mark is missed.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def case_tags(case_dir):
    tags = set()
    for name in ("prompt.md", "case.yaml"):
        p = REPO / case_dir / name
        if not p.is_file():
            continue
        text = p.read_text()
        m = re.search(r"^tags:\s*\[([^\]]*)\]", text, re.M)
        if m:
            tags |= {t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()}
        else:
            m = re.search(r"^tags:\s*\n((?:\s+-\s*.+\n)+)", text, re.M)
            if m:
                tags |= {t.strip()[1:].strip().strip("'\"") for t in m.group(1).splitlines() if t.strip()}
    return tags


def main(paths):
    blocking, review, rows = [], [], []
    per_skill = defaultdict(lambda: {"cases": 0, "passed": 0})
    total_cost = 0.0
    for path in paths:
        d = json.loads(Path(path).read_text())
        total_cost += float(d.get("costUsd") or 0)
        if d.get("partial"):
            blocking.append(f"{Path(path).name}: run is partial ({d.get('partialReason')})")
        for c in d.get("cases", []):
            score = float((c.get("aggregates") or {}).get("score") or 0)
            tags = case_tags(c["dir"])
            parts = c["dir"].split("/")
            skill = parts[2] if len(parts) > 2 else "?"
            kind = "trigger" if "trigger" in tags or "/triggers/" in c["dir"] else "behaviour"
            neg = c["dir"].endswith("-neg")
            if "safety" in tags or (kind == "trigger" and neg):
                need, block = 1.0, True
            elif kind == "trigger":
                need, block = 1.0, False
            else:
                need, block = 0.9, True
            ok = score >= need - 1e-9
            key = f"{skill} ({kind})"
            per_skill[key]["cases"] += 1
            per_skill[key]["passed"] += ok
            if not ok:
                msg = f"{c['name']}: score {score:.2f}, needs {need:.2f}" + (" [safety]" if "safety" in tags else "")
                (blocking if block else review).append(msg)
    print("| Skill (pass) | Cases | Met pass mark |\n|---|---|---|")
    for k in sorted(per_skill):
        v = per_skill[k]
        print(f"| {k} | {v['cases']} | {v['passed']} |")
    print(f"\nReported cost: ${total_cost:.2f}")
    if review:
        print("\nREVIEW (positive triggers that didn't fire):")
        for r in review:
            print("  - " + r)
    if blocking:
        print("\nBLOCKING:")
        for b in blocking:
            print("  - " + b)
        print("\nGate 4: FAIL")
        return 1
    print("\nGate 4: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
