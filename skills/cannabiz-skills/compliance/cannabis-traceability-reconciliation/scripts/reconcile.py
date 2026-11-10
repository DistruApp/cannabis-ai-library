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
can't resolve gets an explicit status and an entry in input_problems.
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

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
GRAMS_PER_LB = 453.592
# Unit-conversion rounding rule. When the two sides record a package in different weight
# units (for example 1 lb in the system and 453.6 g on the count sheet), a difference of up
# to 0.05 g per pound of package weight (minimum 0.05 g) is treated as rounding and the row
# is a MATCH with a note. 0.05 g is half of the last digit when grams are written to one
# decimal place; it scales per pound because a rounded per-pound factor compounds.
ROUNDING_G_PER_LB = 0.05


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " "))


def norm_tag(t):
    return re.sub(r"[\s\-]", "", (t or "").strip().upper())


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


def parse_overrides(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"Bad mapping '{p}'. Use field=Column Name")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def load(path, overrides, label):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        headers = rows[0].keys() if rows else []
    m = detect(headers, overrides)
    for req in ("package_id", "quantity"):
        if req not in m or m[req].startswith("AMBIGUOUS:"):
            sys.exit(f"[{label}] Cannot identify '{req}' column (found: {m.get(req, 'none')}). "
                     f"Headers: {list(headers)}. Pass --map-{label} {req}=<Column>.")
    return rows, m


def to_number(s):
    s = (s or "").strip().replace(",", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


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
    if abs(len(a) - len(b)) > k:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1] <= k


def describe_rows(recs):
    parts = []
    for r in recs:
        if r["qty"] is not None:
            q = fmt_num(r["qty"])
        else:
            q = f"'{r['raw_qty'].strip()}' (not a number)" if r["raw_qty"].strip() else "(blank quantity)"
        parts.append(f"row {r['row']}: {q} {r['uom'] or '(blank unit)'}")
    return "; ".join(parts)


def merge_duplicates(tag, recs, label, problems):
    """Combine rows that share a tag, or mark the tag DUPLICATE_CONFLICT. Never drops a row silently."""
    first = recs[0]
    merged = {"tag": tag, "item": first["item"], "location": first["location"], "conflict": False}
    n, desc = len(recs), describe_rows(recs)
    identical = len({(r["qty"], r["uom"].lower()) for r in recs}) < n
    copy_paste = " Some rows are identical, so this may be a copy-paste duplicate: check the file." if identical else ""
    if any(r["qty"] is None for r in recs):
        reason = "a quantity is blank or not a number"
    else:
        units = {r["uom"].lower() for r in recs}
        if len(units) == 1:
            total = sum(r["qty"] for r in recs)
            merged.update(qty=total, uom=first["uom"])
            merged["note"] = f"{n} rows with this tag summed ({desc}){'.' + copy_paste if copy_paste else ''}"
            problems.append(f"{label}: duplicate tag {tag}: {n} rows summed to {fmt_num(total)} "
                            f"{first['uom'] or '(blank unit)'} ({desc}).{copy_paste}")
            return merged
        kinds = {unit_kind(r["uom"])[0] for r in recs}
        if len(kinds) == 1 and kinds <= {"weight", "each"}:
            base = "g" if "weight" in kinds else "each"
            total = sum(r["qty"] * unit_kind(r["uom"])[1] for r in recs)
            merged.update(qty=total, uom=base)
            merged["note"] = f"{n} rows with this tag summed (converted to {base}) ({desc}){'.' + copy_paste if copy_paste else ''}"
            problems.append(f"{label}: duplicate tag {tag}: {n} rows summed (converted to {base}) "
                            f"to {fmt_num(round(total, 4))} {base} ({desc}).{copy_paste}")
            return merged
        reason = "the units can't be converted to one another (weight vs. each, or a blank or unknown unit)"
    merged.update(qty=None, uom="", conflict=True)
    merged["note"] = f"duplicate rows not summed because {reason} ({desc})"
    problems.append(f"{label}: duplicate tag {tag}: {n} rows NOT summed because {reason} ({desc}). "
                    f"Status DUPLICATE_CONFLICT; quantities not compared.{copy_paste}")
    return merged


def index(rows, m, label, problems):
    groups = defaultdict(list)
    for i, r in enumerate(rows, start=2):
        tag = norm_tag(r.get(m["package_id"]))
        if not tag:
            problems.append(f"{label} row {i}: blank package tag")
            continue
        raw_qty = r.get(m["quantity"]) or ""
        qty = to_number(raw_qty)
        uom = r.get(m["uom"], "") if ok(m, "uom") else ""
        if qty is None:
            problems.append(f"{label} row {i} ({tag}): non-numeric quantity '{raw_qty}'")
        groups[tag].append({"row": i, "qty": qty, "raw_qty": raw_qty, "uom": (uom or "").strip(),
                            "item": r.get(m["item"], "") if ok(m, "item") else "",
                            "location": r.get(m["location"], "") if ok(m, "location") else ""})
    idx = {}
    for tag, recs in groups.items():
        if len(recs) == 1:
            r = recs[0]
            idx[tag] = {"tag": tag, "qty": r["qty"], "uom": r["uom"], "item": r["item"],
                        "location": r["location"], "conflict": False, "note": ""}
        else:
            idx[tag] = merge_duplicates(tag, recs, label, problems)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", required=True, help="Traceability export (Metrc/BioTrack/etc.)")
    ap.add_argument("--count", required=True, help="ERP export or physical count")
    ap.add_argument("--out-dir", default="recon_out")
    ap.add_argument("--map-system", nargs="*")
    ap.add_argument("--map-count", nargs="*")
    ap.add_argument("--tolerance-g", type=float, default=0.0,
                    help="Ignore weight differences at or below this many grams (operator's own threshold)")
    ap.add_argument("--tolerance-each", type=float, default=0.0)
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

    srows, sm = load(a.system, parse_overrides(a.map_system), "system")
    crows, cm = load(a.count, parse_overrides(a.map_count), "count")
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
    S = index(srows, sm, "system", problems)
    C = index(crows, cm, "count", problems)
    out = []
    compared_base = {}
    defaults_used = Counter()

    only_s = sorted(set(S) - set(C))
    only_c = sorted(set(C) - set(S))
    # Near-match hint only when a count tag has exactly one similar system tag. It goes in the
    # notes; both rows keep their own status so nothing gets downgraded.
    near_c = {}
    for c in only_c:
        cands = [s for s in only_s if edit_distance_le(c, s, 2)]
        if len(cands) == 1:
            near_c[c] = cands
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
               "difference": "", "difference_unit": "", "pct_of_system": "", "status": "", "notes": ""}
        notes = []
        if s and s["note"]:
            notes.append("system: " + s["note"])
        if c and c["note"]:
            notes.append("count: " + c["note"])
        if s and not c:
            row["status"] = "IN_SYSTEM_NOT_COUNTED"
            if near_s.get(tag):
                notes.append(typo_hint.format(other="count", tags=" / ".join(near_s[tag])))
        elif c and not s:
            row["status"] = "COUNTED_NOT_IN_SYSTEM"
            if near_c.get(tag):
                notes.append(typo_hint.format(other="system", tags=" / ".join(near_c[tag])))
        elif s["conflict"] or c["conflict"]:
            row["status"] = "DUPLICATE_CONFLICT"
        elif s["qty"] is None or c["qty"] is None:
            row["status"] = "BAD_QUANTITY"
        else:
            su, cu, missing = s["uom"], c["uom"], []
            for side, val, default in (("system", su, a.default_system_unit),
                                       ("count", cu, a.default_count_unit)):
                if not val:
                    if default:
                        notes.append(f"{side} unit blank; used --default-{side}-unit {default} "
                                     "as stated by the operator")
                        defaults_used[side] += 1
                    else:
                        missing.append(side)
            su, cu = su or a.default_system_unit, cu or a.default_count_unit
            row["system_uom"], row["count_uom"] = su, cu
            if missing:
                row["status"] = "MISSING_UNIT"
                sides = " and ".join(missing)
                notes.append(f"unit is blank in the {sides} file; quantities not compared")
                # One problem per package when a unit cell is blank; a missing column is reported once above.
                if any(has_unit_col[x] for x in missing):
                    problems.append(f"{tag}: unit is blank in the {sides} file; quantities not compared "
                                    "(status MISSING_UNIT)")
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
                    allowance = ROUNDING_G_PER_LB * max(1.0, abs(base) / GRAMS_PER_LB)
                    row["difference"] = round(diff, 4)
                    row["difference_unit"] = unit
                    row["pct_of_system"] = round(100.0 * diff / base, 3) + 0.0 if base else ""
                    compared_base[tag] = (unit, base)
                    if converted:
                        notes.append(f"units converted: count '{cu}' and system '{su}' both expressed in {unit}")
                    if abs(diff) < 1e-9:
                        row["status"] = "MATCH"
                    elif unit == "g" and converted and abs(diff) <= allowance + 1e-9:
                        row["status"] = "MATCH"
                        notes.append(f"within unit-conversion rounding ({fmt_num(round(diff, 4))} g; "
                                     f"allowance {fmt_num(round(allowance, 4))} g)")
                    elif abs(diff) <= tol + 1e-9:
                        row["status"] = "WITHIN_TOLERANCE"
                    else:
                        row["status"] = "OVER_IN_COUNT" if diff > 0 else "SHORT_IN_COUNT"
        row["notes"] = " | ".join(notes)
        out.append(row)

    os.makedirs(a.out_dir, exist_ok=True)
    fields = list(out[0].keys()) if out else ["package_id"]
    with open(os.path.join(a.out_dir, "reconciliation.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    by_status = Counter(r["status"] for r in out)
    net = defaultdict(float)
    gross = defaultdict(float)
    for r in out:
        if r["difference"] != "":
            net[r["difference_unit"]] += r["difference"]
            if r["status"] in ("OVER_IN_COUNT", "SHORT_IN_COUNT"):
                gross[r["difference_unit"]] += abs(r["difference"])
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
        "net_difference": {k: round(v, 4) for k, v in net.items()},
        "gross_variance_outside_tolerance": {k: round(v, 4) for k, v in gross.items()},
        "system_total_compared": {k: round(v, 4) for k, v in compared_total.items()},
        "system_total_all_packages": {k: round(v, 4) for k, v in all_total.items()},
        "net_difference_pct_of_compared_total": pct_total,
        "packages_over_5pct_abs": sum(1 for r in out if r["pct_of_system"] != "" and abs(r["pct_of_system"]) >= 5),
        "note_pct": ("net_difference and net_difference_pct_of_compared_total cover quantity-compared packages "
                     "only (on both lists, numeric quantities, convertible units); system_total_compared is "
                     "their system quantity. Packages in only one file and DUPLICATE_CONFLICT, MISSING_UNIT, "
                     "UNKNOWN_UOM, UOM_MISMATCH and BAD_QUANTITY rows are not in the net, so a "
                     "total-inventory reading must list them separately. system_total_all_packages is every "
                     "system package with a recognized unit, for context. Do not interpret against any state "
                     "threshold without the jurisdiction gate."),
        "rounding_rule": (f"Rows whose weight units were converted (e.g. lb vs g) are MATCH when the difference "
                          f"is at most {ROUNDING_G_PER_LB} g per pound of package weight (minimum "
                          f"{ROUNDING_G_PER_LB} g); the note says so and the difference is still shown."),
        "tolerance": {"g": a.tolerance_g, "each": a.tolerance_each},
        "default_units": {"system": a.default_system_unit or None, "count": a.default_count_unit or None,
                          "rows_using_default": dict(defaults_used)},
        "input_problems": problems,
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
