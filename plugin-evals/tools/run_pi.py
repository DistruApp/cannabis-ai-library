#!/usr/bin/env python3
"""Play the `claude plugin eval` cases in plugin-evals/ against a non-Claude model through the `pi` CLI.

    python3 plugin-evals/tools/run_pi.py 'behaviour/*/*' 'triggers/*/*' --runs 2 -j 6 \
        --out plugin-evals/results/pi/gpt-pass1.json

Standard library only. The output JSON has the fields gate4_summary.py reads
(cases[].dir, cases[].name, cases[].aggregates.score, costUsd, partial), plus each
run's final text, tool calls and every grader's verdict and reason for triage.

How a case is played
  - At start, skills/ and the matched case folders are copied to a temp snapshot and
    everything runs from it, so edits to the tree during the run don't leak in. The git
    HEAD and dirty paths at start are recorded under `tree`.
  - A fresh temp working directory per case and run. If the case has setup.sh it is
    run there with bash (it copies the case's resources/ into ./resources), the same
    as `claude plugin eval --scaffold`.
  - pi runs in that directory with ONLY the `read` tool, every skill in skills/
    loaded with --skill, and discovery of other skills, extensions, MCP servers and
    AGENTS.md/CLAUDE.md context files turned off, so the agent sees the same ten
    skills and nothing else. append_system_prompt is passed through.
  - Cases tagged needs-bash are skipped by default (--exclude-tag). pi has no
    max_turns flag, so max_turns is not enforced; timeout_seconds is (x --timeout-mult).

Graders
  - regex: on the final assistant message (target: final/transcript, or a file in the
    workdir). match: contains (default) | not_contains | count:N (at least N matches).
  - tool_used: pi has no Skill tool. SKILL RULE: a skill counts as fired once for each
    `read` call whose path ends in `<skill-name>/SKILL.md` (pi emits no separate skill
    activation event; its system prompt tells the model to load a skill by reading that
    file). Each such read is turned into a virtual call Skill({"skill": "<skill-name>"})
    and the grader's input_match / min / max are applied to those, unchanged. Other
    tools are mapped by name (read -> Read); a tool pi does not have counts 0 calls.
  - llm: pi judge (--no-tools) gets the rubric, the user's prompt and the final reply and
    must answer strict JSON {"pass": bool, "reason": str}. --votes votes (default 3),
    majority passes. A malformed or failed vote counts as a fail and is recorded.
  - file_exists, baseline: N/A for this runner, left out of the score.
Score per run = graders passed / graders scored (unweighted). Case score = mean over
completed runs. Runs that could not complete (usage limit after retries, crash,
timeout) are left out of the mean and make the result `partial`.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVALS = REPO / "plugin-evals"
DEFAULT_MODEL = "openai-codex/gpt-6.1-sol"
ISOLATION = ["--no-skills", "--no-extensions", "--no-mcp", "--no-context-files"]
LIMIT_RE = re.compile(r"usage limit|rate.?limit|too many requests|\b429\b|quota|try again (later|in)|overloaded",
                      re.I)
SKILL_RULE = ("A skill counts as fired once per `read` tool call whose path ends in "
              "`<skill-name>/SKILL.md`; each becomes a virtual Skill({\"skill\": \"<skill-name>\"}) "
              "call that the tool_used grader's input_match/min/max are applied to.")
PRINT_LOCK = threading.Lock()


def log(*a):
    with PRINT_LOCK:
        print(*a, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- case parsing
def parse_scalar(v):
    v = v.strip()
    if v == "":
        return ""
    if v.startswith("'") and v.endswith("'") and len(v) >= 2:
        return v[1:-1].replace("''", "'")
    if v[0] in '"[{':
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            pass
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    if v in ("true", "false"):
        return v == "true"
    return v


def front_matter(text):
    """Return (dict, body) for a '---' front-matter file. Flat `key: value` only."""
    meta, body = {}, text
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t", "#")):
                k, v = line.split(":", 1)
                meta[k.strip()] = parse_scalar(v)
        body = m.group(2)
    return meta, body.strip()


def load_case(case_dir, rel_dir=None):
    meta, prompt = front_matter((case_dir / "prompt.md").read_text())
    graders = []
    for g in sorted((case_dir / "graders").glob("*.md")):
        gm, gbody = front_matter(g.read_text())
        gm["name"] = g.stem
        if gm.get("type") == "llm":
            gm["criteria"] = gbody
        graders.append(gm)
    scaffold = None
    cy = case_dir / "case.yaml"
    if cy.is_file():
        m = re.search(r"scaffold_script:\s*(\S+)", cy.read_text())
        if m:
            scaffold = m.group(1).strip("'\"")
    elif (case_dir / "setup.sh").is_file():
        scaffold = "setup.sh"
    tags = meta.get("tags") or []
    return {"dir": rel_dir or str(case_dir.relative_to(REPO)), "path": case_dir, "name": meta.get("name", case_dir.name),
            "tags": tags, "prompt": prompt, "graders": graders, "scaffold": scaffold,
            "append_system_prompt": meta.get("append_system_prompt"),
            "timeout": int(meta.get("timeout_seconds") or 600), "max_turns": meta.get("max_turns")}


def find_cases(patterns):
    dirs = sorted({p.parent for p in EVALS.glob("*/*/*/prompt.md")})
    out = []
    for d in dirs:
        rel = str(d.relative_to(EVALS))
        if not patterns or any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(d.name, p) or
                               fnmatch.fnmatch(str(d.relative_to(REPO)), p) for p in patterns):
            out.append(d)
    return out


def skill_dirs(root):
    return sorted(p.parent for p in (root / "skills").rglob("SKILL.md"))


def git_state():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "skills", "plugin-evals/behaviour",
                                "plugin-evals/triggers"], cwd=REPO, capture_output=True, text=True).stdout.split("\n")
        return {"head": head, "dirtyPaths": [l for l in dirty if l.strip()]}
    except OSError:
        return {}


# --------------------------------------------------------------------------- pi
def run_pi(args, cwd, timeout):
    """Run pi, return (returncode, stdout, stderr, timed_out)."""
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           timeout=timeout)
        return r.returncode, r.stdout, r.stderr, False
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        return None, out, err, True


def parse_events(stdout):
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return events


def text_of(msg):
    return "\n".join(c.get("text", "") for c in msg.get("content") or []
                     if isinstance(c, dict) and c.get("type") == "text").strip()


def summarise(events):
    """Final assistant text, tool calls, error messages from pi JSON events."""
    assistants = [e["message"] for e in events
                  if e.get("type") == "message_end" and (e.get("message") or {}).get("role") == "assistant"]
    final = ""
    for m in reversed(assistants):
        t = text_of(m)
        if t:
            final = t
            break
    calls = [{"tool": e.get("toolName"), "args": e.get("args")} for e in events
             if e.get("type") == "tool_execution_start"]
    errors = [m.get("errorMessage") or m.get("stopReason") for m in assistants
              if m.get("stopReason") in ("error", "aborted") or m.get("errorMessage")]
    last_stop = assistants[-1].get("stopReason") if assistants else None
    all_text = "\n\n".join(text_of(m) for m in assistants if text_of(m))
    return final, calls, errors, last_stop, all_text


def skill_reads(calls, known):
    fired = []
    for c in calls:
        if (c["tool"] or "").lower() != "read":
            continue
        path = str((c["args"] or {}).get("path") or (c["args"] or {}).get("file_path") or "")
        m = re.search(r"([\w.-]+)/SKILL\.md$", path.rstrip())
        if m and m.group(1) in known:
            fired.append(m.group(1))
    return fired


# --------------------------------------------------------------------------- graders
def re_flags(s):
    f = 0
    for ch in str(s or ""):
        f |= {"i": re.I, "m": re.M, "s": re.S, "x": re.X}.get(ch, 0)
    return f


def grade_regex(g, final, all_text, calls, workdir):
    target = str(g.get("target") or "final").lower()
    if target in ("final", "final_message", "last_message", "response", "output", "result"):
        text = final
    elif target in ("transcript", "all", "assistant", "messages"):
        text = all_text + "\n" + "\n".join(json.dumps(c) for c in calls)
    else:
        p = Path(workdir) / g["target"]
        if not p.is_file():
            return "fail", f"target file {g['target']} not found in workdir"
        text = p.read_text(errors="replace")
    try:
        hits = re.findall(g["pattern"], text, re_flags(g.get("flags")))
    except re.error as e:
        return "na", f"bad pattern: {e}"
    n = len(hits)
    match = str(g.get("match") or "contains")
    if match == "contains":
        return ("pass" if n else "fail"), f"{n} match(es) of /{g['pattern']}/ in {target}"
    if match == "not_contains":
        first = ""
        if n:
            m = re.search(g["pattern"], text, re_flags(g.get("flags")))
            first = ": ..." + text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ") + "..."
        return ("fail" if n else "pass"), f"{n} forbidden match(es) of /{g['pattern']}/{first}"
    m = re.fullmatch(r"count:\s*(\d+)", match)
    if m:
        need = int(m.group(1))
        return ("pass" if n >= need else "fail"), f"{n} match(es), need at least {need}"
    return "na", f"unknown match mode {match}"


def grade_tool_used(g, calls, fired):
    tool = str(g.get("tool") or "")
    if tool == "Skill":
        virtual = [{"skill": s} for s in fired]
    else:
        virtual = [c["args"] or {} for c in calls if (c["tool"] or "").lower() == tool.lower()]
    pat = g.get("input_match")
    hits = [v for v in virtual if not pat or re.search(pat, json.dumps(v))]
    lo = int(g.get("min", 1))
    hi = g.get("max")
    ok = len(hits) >= lo and (hi is None or len(hits) <= int(hi))
    rng = f"{lo}..{hi if hi is not None else 'inf'}"
    detail = f"skills read: {fired}" if tool == "Skill" else f"{len(virtual)} {tool} call(s)"
    return ("pass" if ok else "fail"), f"{len(hits)} matching {tool} call(s), need {rng}; {detail}"


JUDGE_TEMPLATE = """You are grading an AI assistant's reply against a rubric. Be strict and literal.

<rubric>
{rubric}
</rubric>

<user_request>
{prompt}
</user_request>

<assistant_final_reply>
{final}
</assistant_final_reply>

Answer with ONLY a JSON object and nothing else, exactly this shape:
{{"pass": true or false, "reason": "one or two sentences naming the rubric points that failed, or why all hold"}}"""


def parse_vote(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t).strip()
    try:
        v = json.loads(t)
    except json.JSONDecodeError:
        return None
    if not isinstance(v, dict) or not isinstance(v.get("pass"), bool):
        return None
    return v


def grade_llm(g, case, final, opts):
    prompt = JUDGE_TEMPLATE.format(rubric=g.get("criteria", ""), prompt=case["prompt"],
                                   final=final or "(empty reply)")
    votes = []
    for i in range(opts.votes):
        d = tempfile.mkdtemp(prefix="pi-judge-")
        try:
            cmd = ["pi", "-p", "--no-session", "--model", opts.judge_model, "--thinking", opts.judge_thinking,
                   "--no-tools", *ISOLATION, "--mode", "json", "--", prompt]
            ev, err = call_with_retry(cmd, d, 300, opts, f"judge {case['name']}")
        finally:
            shutil.rmtree(d, ignore_errors=True)
        if err:
            votes.append({"pass": False, "malformed": True, "reason": f"judge error: {err}", "raw": ""})
            continue
        final_j, _, errors, _, _ = summarise(ev)
        v = parse_vote(final_j)
        if v is None:
            votes.append({"pass": False, "malformed": True, "reason": "malformed vote",
                          "raw": final_j[:1000]})
        else:
            votes.append({"pass": v["pass"], "malformed": False, "reason": str(v.get("reason", ""))})
    n_pass = sum(v["pass"] for v in votes)
    status = "pass" if n_pass * 2 > len(votes) else "fail"
    reason = f"{n_pass}/{len(votes)} votes pass. " + " | ".join(
        ("PASS: " if v["pass"] else "FAIL: ") + v["reason"] for v in votes)
    return status, reason, votes


# --------------------------------------------------------------------------- run one
def call_with_retry(cmd, cwd, timeout, opts, label):
    """Run pi with back-off on usage limits. Return (events, error_or_None)."""
    delay = opts.backoff
    for attempt in range(opts.retries + 1):
        rc, out, err, timed_out = run_pi(cmd, cwd, timeout)
        events = parse_events(out)
        final, _, errors, last_stop, _ = summarise(events)
        blob = " ".join(str(e) for e in errors) + " " + err[-2000:]
        if timed_out:
            problem = f"timeout after {timeout}s"
        elif errors and not final:
            problem = "pi error: " + "; ".join(str(e) for e in errors)[:500]
        elif rc not in (0, None) and not final:
            problem = f"pi exit {rc}: {err.strip()[-500:]}"
        elif not events:
            problem = f"no JSON events (exit {rc}): {err.strip()[-500:]}"
        else:
            return events, None
        limited = bool(LIMIT_RE.search(blob))
        if attempt < opts.retries and (limited or not timed_out):
            log(f"  retry {label} in {delay}s ({'usage limit' if limited else problem[:120]})")
            time.sleep(delay)
            delay = min(delay * 2, 900)
            continue
        return events, problem
    return [], "unreachable"


def run_one(case, run_no, opts, known_skills, skill_args, raw_dir):
    t0 = time.time()
    workdir = tempfile.mkdtemp(prefix="pi-eval-")
    rec = {"run": run_no, "completed": False, "error": None}
    try:
        if case["scaffold"]:
            s = subprocess.run(["bash", str(case["path"] / case["scaffold"])], cwd=workdir,
                               capture_output=True, text=True)
            if s.returncode != 0:
                rec["error"] = f"setup failed: {s.stderr.strip()[-300:]}"
                return rec
        cmd = ["pi", "-p", "--no-session", "--model", opts.model, "--thinking", opts.thinking,
               "--tools", "read", *ISOLATION, *skill_args]
        if case["append_system_prompt"]:
            cmd += ["--append-system-prompt", case["append_system_prompt"]]
        cmd += ["--mode", "json", "--", case["prompt"]]
        events, err = call_with_retry(cmd, workdir, int(case["timeout"] * opts.timeout_mult), opts, case["name"])
        if raw_dir:
            rp = raw_dir / case["name"] / f"run-{run_no}.jsonl"
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text("".join(json.dumps(e) + "\n" for e in events if e.get("type") != "message_update"))
        final, calls, errors, last_stop, all_text = summarise(events)
        fired = skill_reads(calls, known_skills)
        rec.update(finalText=final, stopReason=last_stop, toolCalls=[
            {"tool": c["tool"], "path": (c["args"] or {}).get("path")} if (c["tool"] or "") == "read"
            else c for c in calls], skillsRead=fired, piErrors=errors)
        if err:
            rec["error"] = err
            return rec
        rec["completed"] = True
        results = []
        for g in case["graders"]:
            gt = g.get("type")
            entry = {"name": g["name"], "type": gt}
            if gt == "regex":
                entry["status"], entry["reason"] = grade_regex(g, final, all_text, calls, workdir)
            elif gt == "tool_used":
                entry["status"], entry["reason"] = grade_tool_used(g, calls, fired)
            elif gt == "llm":
                entry["status"], entry["reason"], entry["votes"] = grade_llm(g, case, final, opts)
            else:
                entry["status"], entry["reason"] = "na", f"{gt} graders are N/A for the pi runner"
            results.append(entry)
        scored = [r for r in results if r["status"] in ("pass", "fail")]
        rec["graders"] = results
        rec["score"] = (sum(r["status"] == "pass" for r in scored) / len(scored)) if scored else None
        return rec
    except Exception as e:  # keep the batch alive
        rec["error"] = f"runner exception: {e!r}"
        return rec
    finally:
        rec["durationSec"] = round(time.time() - t0, 1)
        shutil.rmtree(workdir, ignore_errors=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("patterns", nargs="*", help="case globs relative to plugin-evals/ (e.g. 'behaviour/*/*', "
                    "'triggers/cannabis-batch-cogs/*') or case folder names. Default: all cases")
    ap.add_argument("--tag", nargs="+", action="extend", default=[], help="keep cases with ANY of these tags")
    ap.add_argument("--exclude-tag", nargs="+", action="extend", default=None,
                    help="drop cases with any of these tags (default: needs-bash)")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("-j", "--jobs", type=int, default=6)
    ap.add_argument("--out", default=str(EVALS / "results" / "pi" / "results.json"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--thinking", default="high")
    ap.add_argument("--judge-model", default=DEFAULT_MODEL)
    ap.add_argument("--judge-thinking", default="medium")
    ap.add_argument("--votes", type=int, default=3)
    ap.add_argument("--timeout-mult", type=float, default=2.0, help="x the case's timeout_seconds")
    ap.add_argument("--retries", type=int, default=5, help="retries per pi call on usage limit / error")
    ap.add_argument("--backoff", type=int, default=60, help="first back-off in seconds (doubles)")
    ap.add_argument("--no-raw", action="store_true", help="don't save raw pi events next to --out")
    opts = ap.parse_args()
    exclude = set(opts.exclude_tag if opts.exclude_tag is not None else ["needs-bash"])

    # Snapshot skills/ and the matched cases first, so edits other people make to the tree
    # during a long run can't mix two versions of a skill or case into one result.
    snap = Path(tempfile.mkdtemp(prefix="pi-eval-snapshot-"))
    shutil.copytree(REPO / "skills", snap / "skills")
    tree = git_state()
    cases, skipped = [], []
    for d in find_cases(opts.patterns):
        rel = str(d.relative_to(REPO))
        shutil.copytree(d, snap / rel)
        c = load_case(snap / rel, rel)
        tags = set(c["tags"])
        if opts.tag and not tags & set(opts.tag):
            continue
        if tags & exclude:
            skipped.append({"dir": c["dir"], "name": c["name"], "reason": "tag " + ",".join(sorted(tags & exclude))})
            continue
        cases.append(c)
    if not cases:
        sys.exit("no cases matched")

    sdirs = skill_dirs(snap)
    known = {p.name for p in sdirs}
    skill_args = [a for p in sdirs for a in ("--skill", str(p))]
    out = Path(opts.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    raw_dir = None if opts.no_raw else out.with_suffix("").parent / (out.stem + "-raw")
    log(f"{len(cases)} cases x {opts.runs} runs, -j {opts.jobs}, {len(skipped)} skipped, model {opts.model}")

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    jobs = [(c, r) for c in cases for r in range(1, opts.runs + 1)]
    results = {}
    with cf.ThreadPoolExecutor(max_workers=opts.jobs) as ex:
        futs = {ex.submit(run_one, c, r, opts, known, skill_args, raw_dir): (c["name"], r) for c, r in jobs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            name, r = futs[f]
            rec = f.result()
            results[(name, r)] = rec
            s = rec.get("score")
            log(f"[{i}/{len(jobs)}] {name} run {r}: " +
                (f"score {s:.2f}" if s is not None else f"INCOMPLETE {rec.get('error')}") +
                f" ({rec.get('durationSec')}s)")

    out_cases, incomplete = [], 0
    for c in cases:
        runs = [results[(c["name"], r)] for r in range(1, opts.runs + 1)]
        done = [x for x in runs if x["completed"] and x.get("score") is not None]
        incomplete += sum(1 for x in runs if not x["completed"])
        score = sum(x["score"] for x in done) / len(done) if done else 0.0
        out_cases.append({"dir": c["dir"], "name": c["name"], "tags": c["tags"],
                          "aggregates": {"score": round(score, 4), "runsCompleted": len(done),
                                         "runsRequested": opts.runs},
                          "runs": runs})
    report = {
        "runner": "plugin-evals/tools/run_pi.py", "model": opts.model, "thinking": opts.thinking,
        "judgeModel": opts.judge_model, "judgeThinking": opts.judge_thinking, "votes": opts.votes,
        "startedAt": started, "finishedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "costUsd": 0, "partial": incomplete > 0,
        "partialReason": f"{incomplete} run(s) could not complete" if incomplete else None,
        "incompleteRuns": incomplete, "skillFiredRule": SKILL_RULE, "tree": tree,
        "notes": "max_turns not enforced (pi has no flag); file_exists/baseline graders N/A; "
                 "needs-bash cases skipped (pi agents get only the read tool).",
        "skipped": skipped, "cases": out_cases,
    }
    out.write_text(json.dumps(report, indent=2))
    shutil.rmtree(snap, ignore_errors=True)
    log(f"wrote {out} ({len(out_cases)} cases, {incomplete} incomplete runs)")


if __name__ == "__main__":
    main()
