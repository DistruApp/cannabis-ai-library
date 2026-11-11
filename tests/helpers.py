"""Shared helpers for the script tests (Gate 2).

Standard library only. Run everything with:  scripts/test-scripts.sh
"""
import csv
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"

SCRIPTS = {
    "reconcile": SKILLS / "cannabiz-skills/compliance/cannabis-traceability-reconciliation",
    "precheck": SKILLS / "cannabiz-skills/compliance/cannabis-transfer-manifest-precheck",
    "cogs": SKILLS / "cannabiz-skills/operations/cannabis-batch-cogs",
    "yield": SKILLS / "cannabiz-skills/operations/cannabis-harvest-yield-analysis",
    "replenish": SKILLS / "cannabiz-skills/operations/cannabis-replenishment-planner",
}

# Cells that a spreadsheet would run as a formula if written verbatim.
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

# The standard bad-number pack every numeric column must survive.
BAD_NUMBERS = {
    "nan": "NaN",
    "inf": "inf",
    "neg_inf": "-inf",
    "negative": "-10",
    "decimal_comma": "1,5",
    "european": "1.234,56",
    "spaced": "1 5",
    "text": "ten",
    "underscore": "1_000",
    "huge": "1e308",
    "huge_plain": "9999999999999",
    "leading_zero_group": "0,125",
}

FORMULA_CELLS = ['=HYPERLINK("http://example.com","x")', "+cmd|' /C calc'!A0", "@SUM(1+1)"]


def skill_dir(name):
    return SCRIPTS[name]


def script_path(name):
    return SCRIPTS[name] / "scripts" / f"{name}.py"


def fixture(name, filename):
    return SCRIPTS[name] / "evals" / "files" / filename


def run(name, args, cwd=None):
    """Run a bundled script exactly as an agent would: python3 <skill-dir>/scripts/<name>.py ...

    Returns CompletedProcess with text stdout/stderr. Uses -I so nothing in the
    current directory can shadow stdlib modules.
    """
    cmd = [sys.executable, "-I", str(script_path(name))] + [str(a) for a in args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=120)


def strict_json_load(path_or_text, is_text=False):
    """json.load that rejects bare NaN / Infinity (which Python would otherwise accept)."""
    def bad_constant(c):
        raise ValueError(f"invalid JSON constant {c}")
    text = path_or_text if is_text else Path(path_or_text).read_text()
    return json.loads(text, parse_constant=bad_constant)


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def mutate_csv(src, dst, row_index, column, value):
    """Copy a CSV fixture and replace one cell (row_index is 0-based over data rows)."""
    with open(src, newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    col = header.index(column)
    rows[row_index + 1][col] = value
    write_csv(dst, header, rows[1:])
    return dst


def csv_cells(path):
    with open(path, newline="") as f:
        for row in csv.reader(f):
            for cell in row:
                yield cell


def assert_no_live_formulas(testcase, out_dir):
    """Every CSV the script wrote must have no cell a spreadsheet would execute.

    Plain numbers (including negative numbers such as -5.69) are allowed.
    """
    for p in Path(out_dir).glob("**/*.csv"):
        for cell in csv_cells(p):
            if cell.startswith(FORMULA_PREFIXES):
                try:
                    float(cell)
                    continue
                except ValueError:
                    testcase.fail(f"{p.name}: live formula cell {cell!r}")


def skill_md_run_commands(name):
    """Return the `python3 <skill-dir>/scripts/<name>.py ...` command lines in SKILL.md."""
    text = (SCRIPTS[name] / "SKILL.md").read_text()
    seg = r"(?:[^`\n\\]|\\(?!\n))*"  # text up to a newline, backtick or line-continuation backslash
    pat = re.compile(r"python3 <skill-dir>/scripts/" + re.escape(name) + r"\.py" + seg + r"(?:\\\n" + seg + r")*")
    return [m.group(0).replace("\\\n", " ") for m in pat.finditer(text)]


def required_options(name):
    """Options argparse marks as required, read from --help usage."""
    out = run(name, ["--help"]).stdout
    usage = re.split(r"\n\s*\n", out, maxsplit=1)[0]  # the usage block ends at the first blank line
    # Required options appear in usage without surrounding [ ].
    usage_flat = re.sub(r"\[[^\[\]]*(\[[^\[\]]*\][^\[\]]*)*\]", "", usage)
    return sorted(set(re.findall(r"(--[a-z][a-z0-9-]*)", usage_flat)))


class TempDir:
    def __enter__(self):
        self._d = tempfile.TemporaryDirectory(prefix="cal-test-")
        return Path(self._d.name)

    def __exit__(self, *a):
        self._d.cleanup()
