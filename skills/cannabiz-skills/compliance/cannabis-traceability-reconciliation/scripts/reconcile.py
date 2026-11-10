#!/usr/bin/env python3
"""Reconcile a traceability package export against an ERP export or physical count.

Standard library only. Deterministic: the same inputs always give the same output.

Usage:
  python3 reconcile.py --system SYSTEM.csv --count COUNT.csv [--out-dir DIR]
                       [--map-system field=Column ...] [--map-count field=Column ...]
                       [--tolerance-g 0] [--tolerance-each 0] [--detect-only]

  --detect-only   print the detected column mapping for both files and exit
                  (run this first and confirm with the user).

Outputs (in --out-dir, default ./recon_out):
  reconciliation.csv  one row per package, with status and difference
  summary.json        counts and totals by status, for the report
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


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " "))


def norm_tag(t):
    return re.sub(r"[\s\-]", "", (t or "").strip().upper())


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


def index(rows, m, label, problems):
    idx = {}
    for i, r in enumerate(rows, start=2):
        tag = norm_tag(r.get(m["package_id"]))
        if not tag:
            problems.append(f"{label} row {i}: blank package tag")
            continue
        qty = to_number(r.get(m["quantity"]))
        uom = r.get(m["uom"], "") if "uom" in m and not m["uom"].startswith("AMBIGUOUS:") else ""
        rec = {"tag": tag, "qty": qty, "uom": uom.strip(),
               "item": r.get(m.get("item", ""), "") if "item" in m else "",
               "location": r.get(m.get("location", ""), "") if "location" in m else ""}
        if qty is None:
            problems.append(f"{label} row {i} ({tag}): non-numeric quantity '{r.get(m['quantity'])}'")
        if tag in idx:
            problems.append(f"{label}: duplicate tag {tag} (rows summed)")
            if qty is not None and idx[tag]["qty"] is not None and idx[tag]["uom"].lower() == rec["uom"].lower():
                idx[tag]["qty"] += qty
            continue
        idx[tag] = rec
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
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    srows, sm = load(a.system, parse_overrides(a.map_system), "system")
    crows, cm = load(a.count, parse_overrides(a.map_count), "count")
    if a.detect_only:
        print(json.dumps({"system_mapping": sm, "count_mapping": cm,
                          "system_rows": len(srows), "count_rows": len(crows)}, indent=2))
        return

    problems = []
    S = index(srows, sm, "system", problems)
    C = index(crows, cm, "count", problems)
    out = []

    only_s = sorted(set(S) - set(C))
    only_c = sorted(set(C) - set(S))
    near = {}
    for c in only_c:
        cands = [s for s in only_s if edit_distance_le(c, s, 2)]
        if len(cands) == 1:
            near[c] = cands[0]

    for tag in sorted(set(S) | set(C)):
        s, c = S.get(tag), C.get(tag)
        row = {"package_id": tag, "item": (s or c)["item"], "location_system": s["location"] if s else "",
               "location_count": c["location"] if c else "",
               "system_qty": s["qty"] if s else "", "system_uom": s["uom"] if s else "",
               "count_qty": c["qty"] if c else "", "count_uom": c["uom"] if c else "",
               "difference": "", "difference_unit": "", "pct_of_system": "", "status": "", "notes": ""}
        if s and not c:
            hit = [k for k, v in near.items() if v == tag]
            row["status"] = "POSSIBLE_TAG_TYPO" if hit else "IN_SYSTEM_NOT_COUNTED"
            if hit:
                row["notes"] = f"count has near-match tag {hit[0]}"
        elif c and not s:
            row["status"] = "POSSIBLE_TAG_TYPO" if tag in near else "COUNTED_NOT_IN_SYSTEM"
            if tag in near:
                row["notes"] = f"system has near-match tag {near[tag]}"
        elif s["qty"] is None or c["qty"] is None:
            row["status"] = "BAD_QUANTITY"
        else:
            ks, fs = unit_kind(s["uom"] or c["uom"])
            kc, fc = unit_kind(c["uom"] or s["uom"])
            if ks == "unknown" or kc == "unknown":
                row["status"] = "UNKNOWN_UOM"
                row["notes"] = f"unrecognized unit(s): '{s['uom']}' / '{c['uom']}'"
            elif ks != kc:
                row["status"] = "UOM_MISMATCH"
                row["notes"] = "weight vs. each — needs per-unit net weight from operator; not converted"
            else:
                diff = c["qty"] * fc - s["qty"] * fs  # positive = more counted than in system
                unit = "g" if ks == "weight" else "each"
                tol = a.tolerance_g if ks == "weight" else a.tolerance_each
                row["difference"] = round(diff, 4)
                row["difference_unit"] = unit
                base = s["qty"] * fs
                row["pct_of_system"] = round(100.0 * diff / base, 3) if base else ""
                if abs(diff) <= tol + 1e-9:
                    row["status"] = "MATCH" if abs(diff) < 1e-9 else "WITHIN_TOLERANCE"
                else:
                    row["status"] = "OVER_IN_COUNT" if diff > 0 else "SHORT_IN_COUNT"
                    if fs != fc:
                        row["notes"] = f"units converted {c['uom']}->{s['uom']}"
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
    # Totals by unit for package-level vs. total-inventory percentage readings.
    sys_total = defaultdict(float)
    for t, rec in S.items():
        k, f = unit_kind(rec["uom"])
        if k != "unknown" and rec["qty"] is not None:
            sys_total["g" if k == "weight" else "each"] += rec["qty"] * f
    pct_total = {k: round(100.0 * net[k] / sys_total[k], 3) for k in net if sys_total.get(k)}
    summary = {
        "system_file": a.system, "count_file": a.count,
        "system_mapping": sm, "count_mapping": cm,
        "packages_in_system": len(S), "packages_in_count": len(C),
        "packages_compared": len(out), "by_status": dict(by_status),
        "net_difference": {k: round(v, 4) for k, v in net.items()},
        "gross_variance_outside_tolerance": {k: round(v, 4) for k, v in gross.items()},
        "system_total": {k: round(v, 4) for k, v in sys_total.items()},
        "net_difference_pct_of_system_total": pct_total,
        "packages_over_5pct_abs": sum(1 for r in out if r["pct_of_system"] != "" and abs(r["pct_of_system"]) >= 5),
        "note_pct": "Percentages computed on compared packages only; missing/typo/UoM rows excluded from net. Do not interpret against any state threshold without the jurisdiction gate.",
        "tolerance": {"g": a.tolerance_g, "each": a.tolerance_each},
        "input_problems": problems,
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
