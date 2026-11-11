#!/usr/bin/env python3
"""Reconcile a traceability package export against an ERP export or physical count.

Standard library only. Deterministic: the same inputs always give the same output.

Usage:
  python3 reconcile.py --system SYSTEM.csv --count COUNT.csv [--out-dir DIR]
                       [--map-system field=Column ...] [--map-count field=Column ...]
                       [--tolerance-g 0] [--tolerance-each 0] [--detect-only]
                       [--default-count-unit UNIT] [--default-system-unit UNIT]

  --detect-only   print the detected column mapping for both files and exit
                  (run this first and confirm with the user).
  --default-count-unit / --default-system-unit
                  unit to use when that file's unit cell is blank or it has no unit
                  column. Only pass this when the operator states the unit. Every row
                  that uses it says so in its notes. Without it, a blank unit gives
                  status MISSING_UNIT and the quantities are not compared.

Outputs (in --out-dir, default ./recon_out):
  reconciliation.csv  one row per package, with status and difference
  summary.json        counts and totals by status, for the report

The script never drops, merges, or fills in a record without saying so. Anything it
can't resolve gets an explicit status and an entry in input_problems. A tag that Excel
turned into scientific notation ("1.23457E+23", "1.23457E23") is never matched or totalled:
status TAG_SCIENTIFIC_NOTATION. Identical duplicate rows are never summed (a possible
copy-paste duplicate): status DUPLICATE_CONFLICT. There is no automatic rounding allowance:
any nonzero difference is a variance unless it is within the operator's own --tolerance-*.
Text cells that a spreadsheet would run as a formula are written with a leading apostrophe.
"""
import argparse
import csv
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations

ALIASES = {
    "package_id": ["tag", "package tag", "label", "package label", "package id", "package #",
                   "package number", "metrc tag", "barcode", "global id", "biotrack id", "inventory id",
                   "packagelabel", "uid"],
    "item": ["item", "item name", "product", "product name", "sku name", "itemname"],
    "quantity": ["quantity", "qty", "on hand", "available", "current quantity", "remaining quantity",
                 "counted", "count", "counted qty", "physical count", "counted quantity"],
    "uom": ["uom", "unit", "unit of measure", "unitofmeasurename", "units", "unit of measure name"],
    "location": ["location", "room", "area", "bin"],
    "category": ["category", "item category", "product category", "type"],
}

GRAMS_PER = {"g": 1.0, "gram": 1.0, "grams": 1.0, "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
             "mg": 0.001, "milligram": 0.001, "milligrams": 0.001,
             "lb": 453.592, "lbs": 453.592, "pound": 453.592, "pounds": 453.592,
             "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495}
EACH = {"each", "ea", "unit", "units", "count", "ct", "pcs", "pc", "piece", "pieces"}
# Converted rows with a difference at or below this get a note that scale resolution or a
# rounded factor could explain it. The note never changes the status: only the operator's
# own --tolerance-g can do that.
SMALL_CONVERTED_DIFF_G = 0.05
# Output precision. Every comparison, total and threshold uses the unrounded values.
DP = 6


def r6(x):
    return round(x, DP) + 0.0


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " "))


def norm_tag(t):
    # Drop whitespace, hyphens and invisible format characters (zero-width space/joiners, word
    # joiner, byte-order mark, soft hyphen: Unicode category Cf) so a pasted tag still matches.
    t = "".join(ch for ch in (t or "") if unicodedata.category(ch) != "Cf")
    return re.sub(r"[\s\-]", "", t.strip().upper())


def ok(m, f):
    return f in m and not m[f].startswith("AMBIGUOUS:")


def detect(headers, overrides):
    found, nh = {}, {norm_header(h): h for h in headers}
    for field, alist in ALIASES.items():
        if field in overrides:
            found[field] = overrides[field]
            continue
        hits = [nh[a] for a in alist if a in nh]
        if len(hits) == 1:
            found[field] = hits[0]
        elif len(hits) > 1:
            found[field] = "AMBIGUOUS:" + "|".join(hits)
    return found


def parse_overrides(pairs, label):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"Bad mapping '{p}'. Use field=Column Name")
        k, v = p.split("=", 1)
        k = k.strip()
        if k not in ALIASES:
            sys.exit(f"Bad mapping '{p}' for --map-{label}: unknown field '{k}'. "
                     f"Fields: {', '.join(ALIASES)}")
        out[k] = v.strip()
    return out


def read_csv_rows(path, label):
    """Read a CSV into (headers, rows). An unreadable file is a clean exit, never a traceback."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = list(reader.fieldnames or [])
            rows = list(reader)
    except UnicodeDecodeError:
        sys.exit(f"[{label}] {path} is not UTF-8 text. Save it as 'CSV UTF-8' and rerun.")
    except (OSError, csv.Error) as e:
        sys.exit(f"[{label}] Cannot read {path}: {e}")
    if not any(h and h.strip() for h in headers):
        sys.exit(f"[{label}] {path} is empty (no header row).")
    if not rows:
        sys.exit(f"[{label}] {path} has a header row but no data rows. Check that the right file "
                 "was exported.")
    by_norm = defaultdict(list)
    for h in headers:
        if h and h.strip():
            by_norm[norm_header(h)].append(h.strip())
    dupes = sorted(v for v in by_norm.values() if len(v) > 1)
    if dupes:
        sys.exit(f"[{label}] {path} has more than one column named {dupes} (names are compared "
                 "ignoring case, spaces and underscores). Rename or remove the extra column and rerun.")
    return headers, rows


def load(path, overrides, label):
    headers, rows = read_csv_rows(path, label)
    by_norm = {norm_header(h): h for h in headers}
    for field, col in overrides.items():
        if col not in headers:
            if norm_header(col) not in by_norm:
                sys.exit(f"[{label}] --map-{label} {field}={col}: there is no column named '{col}'. "
                         f"Headers: {headers}")
            overrides[field] = by_norm[norm_header(col)]
    m = detect(headers, overrides)
    for req in ("package_id", "quantity"):
        if req not in m or m[req].startswith("AMBIGUOUS:"):
            sys.exit(f"[{label}] Cannot identify '{req}' column (found: {m.get(req, 'none')}). "
                     f"Headers: {list(headers)}. Pass --map-{label} {req}=<Column>.")
    return rows, m


_THOUSANDS_RE = re.compile(r"^[+-]?[1-9]\d{0,2}(,\d{3})+(\.\d+)?$")
# No real quantity, weight or cost is this large; bigger values overflow later sums.
_MAX_ABS = 1e12


def to_number(s):
    """Strict numeric parse. Returns (value, problem).

    value is a finite float or None; problem is None or a short reason.
    Blank -> (None, None). Accepts plain numbers and US thousands
    separators ("1,234.5"). Rejects NaN/inf and decimal commas
    ("1,5", "1.234,56"): a wrong guess there changes the number by 10x
    or more, so the row is reported instead of guessed.
    Callers decide whether a negative value is allowed.
    """
    s = (s or "").strip().replace("$", "").strip()
    if s == "":
        return None, None
    if any(c.isspace() or c == "_" for c in s):
        return None, f"not a number: '{s}'"
    if "," in s:
        if not _THOUSANDS_RE.match(s):
            return None, f"ambiguous comma in '{s}' (decimal comma or bad thousands separator)"
        s = s.replace(",", "")
    try:
        v = float(s)
    except ValueError:
        return None, f"not a number: '{s}'"
    if not math.isfinite(v):
        return None, f"not a finite number: '{s}'"
    if abs(v) > _MAX_ABS:
        return None, f"out of range: '{s}'"
    return v, None


_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(v):
    """Stop a spreadsheet from running a cell as a formula.

    Text that starts with = + - @ or a tab/return gets a leading
    apostrophe. Real numbers (including negatives like -5.69) are left alone.
    """
    if isinstance(v, str) and v.startswith(_FORMULA_START):
        try:
            float(v)
        except ValueError:
            return "'" + v
    return v


# A numeric tag that Excel turned into scientific notation ("1.23457E+23"). The real digits
# are gone, so the tag can't be matched, and two packages can collapse to the same value.
_SCI_TAG_RE = re.compile(r"^\d+(\.\d+)?[eE][+-]?\d+$")


def is_sci_tag(raw):
    return bool(_SCI_TAG_RE.match(re.sub(r"\s", "", raw or "")))


def tolerance_arg(raw):
    """argparse type for --tolerance-*: the same strict parse as quantities, 0 or more."""
    v, problem = parse_qty(raw)
    if problem or v is None:
        raise argparse.ArgumentTypeError(
            f"'{raw}' is not a usable tolerance: give a plain number of 0 or more, such as 0.5")
    return v


# One comma group and no decimal point: "1,234" is 1234 in US format but 1.234 in European
# format. Held, not guessed. "1,234.5" and "1,234,567" can only be US thousands.
_ONE_COMMA_GROUP_RE = re.compile(r"^[+-]?\d{1,3},\d{3}$")


def parse_qty(raw):
    """to_number plus the quantity rules: no negative, no currency symbol, no '1,234' guess."""
    s = (raw or "").strip()
    if "$" in s:
        return None, f"currency symbol in a quantity: '{s}'"
    if _ONE_COMMA_GROUP_RE.match(s):
        return None, (f"ambiguous comma in '{s}' (US thousands {s.replace(',', '')} or European decimal "
                      f"{s.replace(',', '.')}); remove the separator in the file and rerun")
    v, problem = to_number(raw)
    if v is not None and v < 0:
        return None, f"negative quantity '{(raw or '').strip()}'"
    return v, problem


def unit_kind(u):
    u = (u or "").strip().lower()
    if u in GRAMS_PER:
        return "weight", GRAMS_PER[u]
    if u in EACH:
        return "each", 1.0
    return "unknown", None


def fmt_num(x):
    return f"{x:g}" if isinstance(x, float) else str(x)


def edit_distance_le(a, b, k=2):
    """True when the edit distance between a and b is at most k.

    Only the diagonal band |i - j| <= k can hold a value <= k, so only that band is filled, values
    are capped at k + 1, and the scan stops once a whole row is over k.
    """
    la, lb = len(a), len(b)
    if abs(la - lb) > k:
        return False
    over = k + 1
    prev = [j if j <= k else over for j in range(lb + 1)]
    for i in range(1, la + 1):
        cur = [over] * (lb + 1)
        if i <= k:
            cur[0] = i
        ca = a[i - 1]
        for j in range(max(1, i - k), min(lb, i + k) + 1):
            v = prev[j - 1] + (ca != b[j - 1])
            if prev[j] + 1 < v:
                v = prev[j] + 1
            if cur[j - 1] + 1 < v:
                v = cur[j - 1] + 1
            cur[j] = v if v < over else over
        if min(cur) > k:
            return False
        prev = cur
    return prev[lb] <= k


def _deletion_keys(t):
    """Hashes of every string made by deleting 0, 1 or 2 characters from t.

    If two tags are within 2 edits, deleting the substituted or extra characters from each leaves
    the same string, so they share at least one key. The reverse isn't always true, so every
    shared key is only a candidate and is checked with edit_distance_le.
    """
    keys = {hash(t[:i] + t[i + 1:j] + t[j + 1:]) for i, j in combinations(range(len(t)), 2)}
    keys.update(hash(t[:i] + t[i + 1:]) for i in range(len(t)))
    keys.add(hash(t))
    return keys


def single_near_matches(only_c, only_s, block=5000):
    """Count tags that have exactly one system tag within 2 edits: {count_tag: [system_tag]}.

    Same answer as comparing every pair, without the all-pairs cost. System tags are indexed in
    blocks by their deletion keys (bounded memory); each count tag only checks the system tags
    that share a key, in sorted order, and stops at the second match because only a single
    match becomes a hint.
    """
    found = {c: [] for c in only_c}
    for start in range(0, len(only_s), block):
        chunk = only_s[start:start + block]
        index = {}  # key -> one position, or a list when several tags share the key (saves memory)
        for n, s in enumerate(chunk):
            for key in _deletion_keys(s):
                held = index.get(key)
                if held is None:
                    index[key] = n
                elif type(held) is int:
                    index[key] = [held, n]
                else:
                    held.append(n)
        for c in only_c:
            hits = found[c]
            if len(hits) > 1:
                continue
            cands = set()
            for key in _deletion_keys(c):
                held = index.get(key)
                if held is None:
                    continue
                if type(held) is int:
                    cands.add(held)
                else:
                    cands.update(held)
            for n in sorted(cands):
                if edit_distance_le(c, chunk[n], 2):
                    hits.append(chunk[n])
                    if len(hits) > 1:
                        break
    return {c: hits for c, hits in found.items() if len(hits) == 1}


def describe_rows(recs):
    parts = []
    for r in recs:
        if r["qty"] is not None:
            q = fmt_num(r["qty"])
        else:
            q = f"'{r['raw_qty'].strip()}' (not a valid quantity)" if r["raw_qty"].strip() else "(blank quantity)"
        parts.append(f"row {r['row']}: {q} {r['uom'] or '(blank unit)'}")
    return "; ".join(parts)


def merge_duplicates(tag, recs, label, problems):
    """Combine rows that share a tag, or mark the tag DUPLICATE_CONFLICT. Never drops a row silently."""
    first = recs[0]
    merged = {"tag": tag, "item": first["item"], "location": first["location"], "conflict": False,
              "qty_problem": None, "rows": [r["row"] for r in recs],
              "defaulted": sum(r["defaulted"] for r in recs)}
    n, desc = len(recs), describe_rows(recs)
    identical = len({(r["qty"], r["uom"].lower()) for r in recs}) < n
    if any(r["qty"] is None for r in recs):
        reason = "a quantity is blank or not a valid number"
    elif identical:
        # Summing a double entry would hide a shortage (50 + 50 "matches" 100 when 50 is on hand).
        reason = ("some rows are identical, so this may be a copy-paste duplicate rather than separate "
                  "counts: confirm with the counter, correct the file and rerun")
    else:
        units = {r["uom"].lower() for r in recs}
        if len(units) == 1:
            total = sum(r["qty"] for r in recs)
            merged.update(qty=total, uom=first["uom"])
            merged["note"] = f"{n} rows with this tag summed ({desc})"
            problems.append(f"{label}: duplicate tag {tag}: {n} rows summed to {fmt_num(total)} "
                            f"{first['uom'] or '(blank unit)'} ({desc}).")
            return merged
        kinds = {unit_kind(r["uom"])[0] for r in recs}
        if len(kinds) == 1 and kinds <= {"weight", "each"}:
            base = "g" if "weight" in kinds else "each"
            total = sum(r["qty"] * unit_kind(r["uom"])[1] for r in recs)
            merged.update(qty=total, uom=base)
            merged["note"] = f"{n} rows with this tag summed (converted to {base}) ({desc})"
            problems.append(f"{label}: duplicate tag {tag}: {n} rows summed (converted to {base}) "
                            f"to {fmt_num(round(total, 4))} {base} ({desc}).")
            return merged
        reason = "the units can't be converted to one another (weight vs. each, or a blank or unknown unit)"
    merged.update(qty=None, uom="", conflict=True)
    merged["note"] = f"duplicate rows not summed because {reason} ({desc})"
    problems.append(f"{label}: duplicate tag {tag}: {n} rows NOT summed because {reason} ({desc}). "
                    "Status DUPLICATE_CONFLICT; quantities not compared.")
    return merged


def index(rows, m, label, problems, sci_rows, default_unit):
    groups = defaultdict(list)
    for i, r in enumerate(rows, start=2):
        raw_tag = r.get(m["package_id"]) or ""
        tag = norm_tag(raw_tag)
        if not tag:
            problems.append(f"{label} row {i}, column '{m['package_id']}': blank package tag; row not used")
            continue
        raw_qty = r.get(m["quantity"]) or ""
        if is_sci_tag(raw_tag):
            problems.append(f"{label} row {i}, column '{m['package_id']}', value '{raw_tag.strip()}': "
                            "package tag is in scientific notation (Excel dropped the real digits); "
                            "row not matched or totalled (status TAG_SCIENTIFIC_NOTATION)")
            qty, qty_problem = parse_qty(raw_qty)
            sci_rows.append({"label": label, "row": i, "tag": raw_tag.strip(),
                             "qty": qty, "qty_problem": qty_problem, "uom": (r.get(m["uom"]) or "").strip() if ok(m, "uom") else "",
                             "item": r.get(m["item"], "") if ok(m, "item") else "",
                             "location": r.get(m["location"], "") if ok(m, "location") else ""})
            continue
        qty, qty_problem = parse_qty(raw_qty)
        uom = ((r.get(m["uom"]) or "") if ok(m, "uom") else "").strip()
        # An operator-stated default unit fills a blank cell before any rows are combined.
        defaulted = not uom and bool(default_unit)
        uom = uom or default_unit
        if qty_problem:
            qty_problem = f"row {i}, column '{m['quantity']}', value '{raw_qty.strip()}': {qty_problem}"
            problems.append(f"{label} {qty_problem} ({tag}); quantity not compared or totalled")
        elif qty is None:
            problems.append(f"{label} row {i} ({tag}), column '{m['quantity']}': blank quantity")
        groups[tag].append({"row": i, "qty": qty, "raw_qty": raw_qty, "uom": uom,
                            "qty_problem": qty_problem, "defaulted": int(defaulted),
                            "item": r.get(m["item"], "") if ok(m, "item") else "",
                            "location": r.get(m["location"], "") if ok(m, "location") else ""})
    idx = {}
    for tag, recs in groups.items():
        if len(recs) == 1:
            r = recs[0]
            idx[tag] = {"tag": tag, "qty": r["qty"], "uom": r["uom"], "item": r["item"],
                        "location": r["location"], "conflict": False, "qty_problem": r["qty_problem"],
                        "rows": [r["row"]], "defaulted": r["defaulted"],
                        "note": f"invalid quantity ({r['qty_problem']})" if r["qty_problem"] else ""}
        else:
            idx[tag] = merge_duplicates(tag, recs, label, problems)
    if not idx and not any(b["label"] == label for b in sci_rows):
        sys.exit(f"[{label}] no row has a package tag in column '{m['package_id']}'. Check the file "
                 "and the column mapping, then rerun.")
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, help="Traceability export (Metrc/BioTrack/etc.)")
    ap.add_argument("--count", required=True, help="ERP export or physical count")
    ap.add_argument("--out-dir", default="recon_out")
    ap.add_argument("--map-system", nargs="*")
    ap.add_argument("--map-count", nargs="*")
    ap.add_argument("--tolerance-g", type=tolerance_arg, default=0.0,
                    help="Ignore weight differences at or below this many grams (operator's own threshold)")
    ap.add_argument("--tolerance-each", type=tolerance_arg, default=0.0)
    ap.add_argument("--default-count-unit", default="",
                    help="Unit for count rows whose unit is blank. Only when the operator states it.")
    ap.add_argument("--default-system-unit", default="",
                    help="Unit for system rows whose unit is blank. Only when the operator states it.")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    for flag, val in (("--default-count-unit", a.default_count_unit),
                      ("--default-system-unit", a.default_system_unit)):
        if val and unit_kind(val)[0] == "unknown":
            sys.exit(f"{flag} '{val}' is not a recognized unit (use g, lb, oz, kg, mg, or each).")

    srows, sm = load(a.system, parse_overrides(a.map_system, "system"), "system")
    crows, cm = load(a.count, parse_overrides(a.map_count, "count"), "count")
    if a.detect_only:
        print(json.dumps({"system_mapping": sm, "count_mapping": cm,
                          "system_rows": len(srows), "count_rows": len(crows)}, indent=2))
        return

    problems = []
    has_unit_col = {"system": ok(sm, "uom"), "count": ok(cm, "uom")}
    for label, default in (("system", a.default_system_unit), ("count", a.default_count_unit)):
        if not has_unit_col[label]:
            how = (f"--default-{label}-unit {default} was applied to every row" if default else
                   "every package on both lists gets MISSING_UNIT unless the operator states the unit "
                   f"(--default-{label}-unit)")
            problems.append(f"{label} file: no unit column found; {how}")
    sci_rows = []
    S = index(srows, sm, "system", problems, sci_rows, a.default_system_unit)
    C = index(crows, cm, "count", problems, sci_rows, a.default_count_unit)
    out = []
    zero_qty_not_counted = []
    compared_base = {}
    defaults_used = {label: n for label, n in (("system", sum(r["defaulted"] for r in S.values())),
                                               ("count", sum(r["defaulted"] for r in C.values()))) if n}

    only_s = sorted(set(S) - set(C))
    only_c = sorted(set(C) - set(S))
    # Near-match hint only when a count tag has exactly one similar system tag. It goes in the
    # notes; both rows keep their own status so nothing gets downgraded.
    near_c = single_near_matches(only_c, only_s)
    near_s = defaultdict(list)
    for c, cands in near_c.items():
        near_s[cands[0]].append(c)
    typo_hint = ("possible tag typo: the {other} file has a similar tag {tags} (within 2 characters). "
                 "Check the physical label. Sequential tags look like this too, so this stays a "
                 "separate variance until confirmed.")

    for tag in sorted(set(S) | set(C)):
        s, c = S.get(tag), C.get(tag)
        row = {"package_id": tag, "item": (s or c)["item"], "location_system": s["location"] if s else "",
               "location_count": c["location"] if c else "",
               "system_qty": s["qty"] if s and s["qty"] is not None else "",
               "system_uom": s["uom"] if s else "",
               "count_qty": c["qty"] if c and c["qty"] is not None else "",
               "count_uom": c["uom"] if c else "",
               "difference": "", "difference_unit": "", "pct_of_system": "", "status": "", "notes": "",
               "_diff": None, "_pct": None}
        notes = []
        for side, rec, default in (("system", s, a.default_system_unit), ("count", c, a.default_count_unit)):
            if rec and rec["note"]:
                notes.append(f"{side}: {rec['note']}")
            if rec and rec["defaulted"]:
                notes.append(f"{side} unit blank on {rec['defaulted']} row(s); used --default-{side}-unit "
                             f"{default} as stated by the operator")
        for side, rec in (("system", s), ("count", c)):
            if rec and not (s and c) and not rec["uom"] and not rec["conflict"]:
                notes.append(f"unit is blank in the {side} file")
        if s and not c:
            row["status"] = "IN_SYSTEM_NOT_COUNTED"
            if s["qty"] is not None and not s["qty_problem"] and abs(s["qty"]) < 1e-9:
                notes.append("zero quantity in the system: likely an emptied package not finished in the "
                             "system; list it, but it isn't missing inventory")
                zero_qty_not_counted.append(tag)
            if near_s.get(tag):
                notes.append(typo_hint.format(other="count", tags=" / ".join(near_s[tag])))
        elif c and not s:
            row["status"] = "COUNTED_NOT_IN_SYSTEM"
            if near_c.get(tag):
                notes.append(typo_hint.format(other="system", tags=" / ".join(near_c[tag])))
        elif s["conflict"] or c["conflict"]:
            row["status"] = "DUPLICATE_CONFLICT"
        elif s["qty_problem"] or c["qty_problem"]:
            row["status"] = "INVALID_NUMBER"  # NaN, inf, negative, decimal comma or text: never compared
        elif s["qty"] is None or c["qty"] is None:
            row["status"] = "BAD_QUANTITY"
        else:
            su, cu = s["uom"], c["uom"]
            missing = [side for side, val in (("system", su), ("count", cu)) if not val]
            if missing:
                row["status"] = "MISSING_UNIT"
                sides = " and ".join(missing)
                notes.append(f"unit is blank in the {sides} file; quantities not compared")
                # One problem per package when a unit cell is blank; a missing column is reported once above.
                where = [f"{x} row(s) {', '.join(map(str, rec['rows']))}, column '{mp['uom']}'"
                         for x, rec, mp in (("system", s, sm), ("count", c, cm)) if x in missing and has_unit_col[x]]
                if where:
                    problems.append(f"{tag}: unit is blank in the {sides} file; quantities not compared "
                                    f"(status MISSING_UNIT; {'; '.join(where)})")
            else:
                ks, fs = unit_kind(su)
                kc, fc = unit_kind(cu)
                if ks == "unknown" or kc == "unknown":
                    row["status"] = "UNKNOWN_UOM"
                    notes.append(f"unrecognized unit(s): '{su}' / '{cu}'")
                elif ks != kc:
                    row["status"] = "UOM_MISMATCH"
                    notes.append("weight vs. each: needs per-unit net weight from operator; not converted")
                else:
                    diff = c["qty"] * fc - s["qty"] * fs  # positive = more counted than in system
                    unit = "g" if ks == "weight" else "each"
                    tol = a.tolerance_g if ks == "weight" else a.tolerance_each
                    base = s["qty"] * fs
                    converted = fs != fc
                    # Display is rounded; status, totals and thresholds use the unrounded values.
                    row["_diff"] = diff
                    row["_pct"] = 100.0 * diff / base if base else None
                    row["difference"] = r6(diff)
                    row["difference_unit"] = unit
                    row["pct_of_system"] = round(row["_pct"], 3) + 0.0 if base else ""
                    compared_base[tag] = (unit, base)
                    if converted:
                        notes.append(f"units converted: count '{cu}' and system '{su}' both expressed in {unit}")
                        if unit == "g" and 1e-9 <= abs(diff) <= SMALL_CONVERTED_DIFF_G:
                            notes.append(f"small difference ({fmt_num(r6(diff))} g) after converting units: scale "
                                         "resolution or a rounded conversion factor could explain it, but it stays "
                                         "a variance unless the operator sets --tolerance-g")
                    if abs(diff) < 1e-9:
                        row["status"] = "MATCH"
                    elif abs(diff) <= tol + 1e-9:
                        row["status"] = "WITHIN_TOLERANCE"
                    else:
                        row["status"] = "OVER_IN_COUNT" if diff > 0 else "SHORT_IN_COUNT"
        row["notes"] = " | ".join(notes)
        out.append(row)

    # Rows whose tag Excel turned into scientific notation: listed, never matched or totalled.
    for b in sci_rows:
        side = b["label"]
        out.append({"package_id": b["tag"], "item": b["item"],
                    "location_system": b["location"] if side == "system" else "",
                    "location_count": b["location"] if side == "count" else "",
                    "system_qty": b["qty"] if side == "system" and b["qty"] is not None else "",
                    "system_uom": b["uom"] if side == "system" else "",
                    "count_qty": b["qty"] if side == "count" and b["qty"] is not None else "",
                    "count_uom": b["uom"] if side == "count" else "",
                    "difference": "", "difference_unit": "", "pct_of_system": "",
                    "status": "TAG_SCIENTIFIC_NOTATION",
                    "notes": (f"{side} row {b['row']}: tag '{b['tag']}' is in scientific notation, so the "
                              "real tag is lost; not matched or totalled. Re-export with the tag column "
                              "formatted as text."
                              + (f" The quantity is also invalid ({b['qty_problem']})." if b["qty_problem"] else "")),
                    "_diff": None, "_pct": None})

    by_status = Counter(r["status"] for r in out)
    net = defaultdict(float)
    gross = defaultdict(float)
    gross_all = defaultdict(float)
    for r in out:
        if r["_diff"] is not None:
            net[r["difference_unit"]] += r["_diff"]
            gross_all[r["difference_unit"]] += abs(r["_diff"])
            if r["status"] in ("OVER_IN_COUNT", "SHORT_IN_COUNT"):
                gross[r["difference_unit"]] += abs(r["_diff"])
    # Totals by unit. The total percentage uses the same quantity-compared set as the net difference.
    compared_total = defaultdict(float)
    for unit, base in compared_base.values():
        compared_total[unit] += base
    all_total = defaultdict(float)
    for rec in S.values():
        k, f = unit_kind(rec["uom"] or a.default_system_unit)
        if k != "unknown" and rec["qty"] is not None and not rec["conflict"]:
            all_total["g" if k == "weight" else "each"] += rec["qty"] * f
    pct_total = {k: round(100.0 * net[k] / compared_total[k], 3) + 0.0 for k in net if compared_total.get(k)}
    summary = {
        "system_file": a.system, "count_file": a.count,
        "system_mapping": sm, "count_mapping": cm,
        "packages_in_system": len(S), "packages_in_count": len(C),
        "packages_compared": len(out),
        "packages_quantity_compared": len(compared_base),
        "by_status": dict(by_status),
        "in_system_not_counted_zero_qty": sorted(zero_qty_not_counted),
        "net_difference": {k: r6(v) for k, v in net.items()},
        "gross_variance_all_compared": {k: r6(v) for k, v in gross_all.items()},
        "gross_variance_outside_tolerance": {k: r6(v) for k, v in gross.items()},
        "system_total_compared": {k: r6(v) for k, v in compared_total.items()},
        "system_total_all_packages": {k: r6(v) for k, v in all_total.items()},
        "net_difference_pct_of_compared_total": pct_total,
        "packages_over_5pct_abs": sum(1 for r in out if r["_pct"] is not None and abs(r["_pct"]) >= 5),
        "note_pct": ("net_difference and net_difference_pct_of_compared_total cover quantity-compared packages "
                     "only (on both lists, numeric quantities, convertible units); system_total_compared is "
                     "their system quantity. Packages in only one file and DUPLICATE_CONFLICT, MISSING_UNIT, "
                     "UNKNOWN_UOM, UOM_MISMATCH, BAD_QUANTITY, INVALID_NUMBER and TAG_SCIENTIFIC_NOTATION rows are not in the net, so a "
                     "total-inventory reading must list them separately. system_total_all_packages is every "
                     "system package with a recognized unit, for context. Do not interpret against any state "
                     "threshold without the jurisdiction gate."),
        "rounding_rule": ("No automatic rounding allowance: any nonzero difference, including after a unit "
                          "conversion, is a variance unless it is within the operator's own --tolerance-g / "
                          "--tolerance-each. Displayed numbers are rounded; statuses, totals and "
                          "packages_over_5pct_abs use unrounded values. gross_variance_all_compared covers every "
                          "quantity-compared package; gross_variance_outside_tolerance only SHORT/OVER rows."),
        "tolerance": {"g": a.tolerance_g, "each": a.tolerance_each},
        "default_units": {"system": a.default_system_unit or None, "count": a.default_count_unit or None,
                          "rows_using_default": dict(defaults_used)},
        "input_problems": problems,
    }
    # Build and validate both outputs before writing either, so a bad value never leaves half a result.
    try:
        summary_text = json.dumps(summary, indent=2, allow_nan=False)
    except ValueError as e:
        sys.exit(f"Result contains a non-finite number ({e}); nothing was written. Check the input values.")
    fields = [k for k in out[0] if not k.startswith("_")] if out else ["package_id"]
    try:
        os.makedirs(a.out_dir, exist_ok=True)
        with open(os.path.join(a.out_dir, "reconciliation.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows([{k: csv_safe(r[k]) for k in fields} for r in out])
        with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
            f.write(summary_text + "\n")
    except OSError as e:
        sys.exit(f"Cannot write to --out-dir {a.out_dir}: {e}")
    print(summary_text)


if __name__ == "__main__":
    main()
