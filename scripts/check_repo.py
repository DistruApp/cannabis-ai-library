#!/usr/bin/env python3
"""Gate 1: repo checks.

Standard library only. Exits 1 if any check fails, 0 otherwise.

    python3 scripts/check_repo.py            # all checks
    python3 scripts/check_repo.py --no-cli   # skip `claude plugin validate` (no Claude Code installed)
    python3 scripts/check_repo.py --local    # also warn about same-named skills installed on this machine
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Reference files copied into several skills. Every copy must be byte-identical:
# edit one, then copy it to the others.
SHARED_REFERENCES = ["state-profiles.md", "jurisdiction-gate.md", "output-conventions.md"]

# Code blocks every bundled script must carry word for word.
SHARED_CODE = {
    "to_number": (r"^_THOUSANDS_RE = ", r"^    return v, None\n"),
    "csv_safe": (r"^_FORMULA_START = ", r"^    return v\n"),
}

ALLOWED_AUTHOR_EMAILS = re.compile(r"(@users\.noreply\.github\.com|^noreply@anthropic\.com)$")
ALLOWED_EMAIL_DOMAINS = re.compile(r"@(example\.(com|org|net)|[a-z0-9-]+\.example|users\.noreply\.github\.com|anthropic\.com|distru\.com)$", re.I)
SECRET_PATTERNS = {
    "Anthropic/OpenAI key": r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{30,}",
    "AWS key": r"\bAKIA[0-9A-Z]{16}\b",
    "Slack token": r"\bxox[abpr]-[A-Za-z0-9-]{10,}",
    "Private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}
INTERNAL_LINKS = r"(notion\.so/|notion\.site/|docs\.google\.com/|drive\.google\.com/|slack\.com/archives)"
DOC_SECTIONS = ["## What it does", "## When to use it", "## How to use it", "## Example"]
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".csv", ".sh", ".txt", ".html", ".toml"}


class Checks:
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.passed = 0

    def ok(self, cond, msg):
        if cond:
            self.passed += 1
        else:
            self.failures.append(msg)
        return cond

    def warn(self, msg):
        self.warnings.append(msg)


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, text=True, check=True).stdout
    return [REPO / p for p in out.split("\0") if p]


def frontmatter(skill_md):
    text = skill_md.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip().strip('"')
    return fm


def check_plugin_validate(c):
    if not shutil.which("claude"):
        c.ok(False, "claude CLI not found: install Claude Code or pass --no-cli")
        return
    r = subprocess.run(["claude", "plugin", "validate", ".", "--strict"], cwd=REPO, capture_output=True, text=True)
    c.ok(r.returncode == 0 and "Validation passed" in r.stdout,
         "claude plugin validate . --strict failed:\n" + (r.stdout + r.stderr)[-1500:])


def check_manifests(c):
    cl = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
    cx = json.loads((REPO / ".codex-plugin/plugin.json").read_text())
    c.ok(cl.get("skills") == cx.get("skills"), "skills arrays differ between .claude-plugin and .codex-plugin")
    c.ok(cl.get("version") == cx.get("version"), "version differs between the two plugin manifests")
    c.ok(cl.get("description") == cx.get("description"), "description differs between the two plugin manifests")
    readme = (REPO / "README.md").read_text()
    skills = []
    for rel in cl.get("skills", []):
        d = (REPO / rel).resolve()
        skills.append(d)
        smd = d / "SKILL.md"
        if not c.ok(smd.is_file(), f"{rel}: SKILL.md missing"):
            continue
        fm = frontmatter(smd) or {}
        name = fm.get("name")
        c.ok(name == d.name, f"{rel}: folder name '{d.name}' != SKILL.md name '{name}'")
        c.ok(bool(fm.get("description")), f"{rel}: SKILL.md has no description")
        c.ok(fm.get("license") == "MIT", f"{rel}: SKILL.md frontmatter needs `license: MIT`")
        rel_md = smd.relative_to(REPO).as_posix()
        c.ok(f"]({rel_md})" in readme or f"](./{rel_md})" in readme, f"{rel}: README.md doesn't link {rel_md}")
        doc = REPO / "docs" / d.relative_to(REPO / "skills").parent / f"{d.name}.md"
        if c.ok(doc.is_file(), f"{rel}: docs page missing ({doc.relative_to(REPO)})"):
            text = doc.read_text()
            for s in DOC_SECTIONS:
                c.ok(s in text, f"{doc.relative_to(REPO)}: missing section '{s}'")
        ev = d / "evals"
        c.ok((ev / "evals.json").is_file(), f"{rel}: evals/evals.json missing")
        c.ok((ev / "trigger_queries.json").is_file(), f"{rel}: evals/trigger_queries.json missing")
        for f in ("evals.json", "trigger_queries.json"):
            p = ev / f
            if p.is_file():
                try:
                    json.loads(p.read_text())
                    c.passed += 1
                except ValueError as e:
                    c.ok(False, f"{p.relative_to(REPO)}: invalid JSON ({e})")
        for script in sorted((d / "scripts").glob("*.py")):
            c.ok((REPO / "tests" / f"test_{script.stem}.py").is_file(),
                 f"{script.relative_to(REPO)}: no tests/test_{script.stem}.py")
            src = script.read_text()
            c.ok(f"<skill-dir>/scripts/{script.name}" in smd.read_text(),
                 f"{rel}: SKILL.md must run the script as `python3 <skill-dir>/scripts/{script.name}`")
            c.ok("Never hand-compute" in smd.read_text(),
                 f"{rel}: SKILL.md lacks the 'Never hand-compute the figures the script produces' rule")
            del src
    # Every SKILL.md under skills/ must be a promoted skill listed in the manifest.
    listed = {s.resolve() for s in skills}
    for smd in (REPO / "skills").glob("**/SKILL.md"):
        c.ok(smd.parent.resolve() in listed, f"{smd.parent.relative_to(REPO)} has a SKILL.md but isn't in plugin.json")
    return skills


def check_shared_references(c):
    groups = {}
    for name in SHARED_REFERENCES:
        for p in sorted((REPO / "skills").glob(f"**/references/{name}")):
            groups.setdefault(name, []).append(p)
    for name, paths in groups.items():
        hashes = {hashlib.md5(p.read_bytes()).hexdigest(): p for p in paths}
        c.ok(len(hashes) == 1, f"{name}: the {len(paths)} copies differ: "
             + ", ".join(str(p.relative_to(REPO)) for p in hashes.values())
             + f". Edit one and copy it to all ({len(paths)}) skills.")


def extract_block(text, start, end):
    m = re.search(start + r".*?" + end, text, re.S | re.M)
    return m.group(0) if m else None


def check_shared_code(c):
    scripts = sorted((REPO / "skills").glob("**/scripts/*.py"))
    for label, (start, end) in SHARED_CODE.items():
        blocks = {}
        for s in scripts:
            b = extract_block(s.read_text(), start, end)
            if not c.ok(b is not None, f"{s.relative_to(REPO)}: shared `{label}` block missing"):
                continue
            blocks.setdefault(b, []).append(s)
        c.ok(len(blocks) <= 1, f"shared `{label}` block differs between scripts: "
             + " | ".join(",".join(p.name for p in v) for v in blocks.values()))


def check_content(c, files):
    for p in files:
        rel = p.relative_to(REPO).as_posix()
        if rel.startswith("tests/") or rel == "scripts/check_repo.py":
            continue
        c.ok("__pycache__" not in rel and not rel.endswith((".pyc", ".DS_Store")), f"{rel}: generated file is tracked")
        if p.suffix.lower() not in TEXT_SUFFIXES or not p.is_file():
            continue
        if p.stat().st_size > 2_000_000:
            c.warn(f"{rel}: {p.stat().st_size // 1024} KB; not content-scanned")
            continue
        text = p.read_text(errors="replace")
        for label, pat in SECRET_PATTERNS.items():
            c.ok(not re.search(pat, text), f"{rel}: looks like a {label}")
        for m in re.finditer(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
            email = m.group(0)
            c.ok(bool(ALLOWED_EMAIL_DOMAINS.search(email)),
                 f"{rel}: email address {email!r} is not an example/noreply domain")
        c.ok(not re.search(INTERNAL_LINKS, text), f"{rel}: internal link (Notion/Google/Slack)")


def check_history(c):
    out = subprocess.run(["git", "log", "--format=%ae%n%ce"], cwd=REPO, capture_output=True, text=True).stdout
    for email in sorted(set(filter(None, out.splitlines()))):
        c.ok(bool(ALLOWED_AUTHOR_EMAILS.search(email)), f"commit history contains author/committer email {email!r}")
    local = subprocess.run(["git", "config", "user.email"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    if local and not ALLOWED_AUTHOR_EMAILS.search(local):
        c.ok(False, f"git user.email is {local!r}: new commits would publish it. Use your GitHub noreply address.")


def check_local_collisions(c, skills):
    names = {d.name for d in skills}
    home = Path.home()
    roots = [home / ".claude/skills", home / ".agents/skills"]
    found = []
    for r in roots:
        if r.is_dir():
            for d in r.iterdir():
                if d.name in names and (d / "SKILL.md").exists() and REPO not in d.resolve().parents:
                    found.append(str(d))
    for p in home.glob("Library/Application Support/Claude/**/skills/*/SKILL.md"):
        if p.parent.name in names:
            found.append(str(p.parent))
    for f in found:
        c.warn(f"a different skill with the same name is installed here: {f} (agents may load the wrong one)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-cli", action="store_true", help="skip `claude plugin validate --strict`")
    ap.add_argument("--local", action="store_true", help="also check this machine for same-named skills")
    a = ap.parse_args()
    c = Checks()
    if not a.no_cli:
        check_plugin_validate(c)
    skills = check_manifests(c)
    check_shared_references(c)
    check_shared_code(c)
    check_content(c, tracked_files())
    check_history(c)
    if a.local:
        check_local_collisions(c, skills)
    for w in c.warnings:
        print(f"WARN  {w}")
    for f in c.failures:
        print(f"FAIL  {f}")
    print(f"\nGate 1: {c.passed} checks passed, {len(c.failures)} failed, {len(c.warnings)} warnings.")
    sys.exit(1 if c.failures else 0)


if __name__ == "__main__":
    main()
