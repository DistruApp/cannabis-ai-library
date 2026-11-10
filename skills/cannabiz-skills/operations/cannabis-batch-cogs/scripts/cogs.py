#!/usr/bin/env python3
"""Roll up cost per batch and per finished unit for a cannabis manufacturing batch.

Standard library only. Deterministic. Refuses to silently default any rate.

Usage:
  python3 cogs.py --bom BOM.csv --units-produced N --labor-hours H --labor-rate R
                  (--overhead-per-batch X | --overhead-per-labor-hour X | --overhead-pct-materials P)
                  --testing-cost T [--expected-units N] [--batch-name NAME]
                  [--map field=Column ...] [--assume key=value ...] [--out-dir DIR] [--detect-only]

BOM CSV (one row per component consumed in this batch):
  component, qty, uom, unit_cost, [cost_uom]   cost_uom = unit the price is quoted in (e.g. $/lb)
  Line cost = qty (converted to cost_uom) x unit_cost.
  If the cost unit is blank (or there is no cost unit column), weight and volume lines are BLOCKED
  ("price per what unit?"). Count lines (each, ct, pcs...) are read as price per each and noted.
  Fully blank rows (e.g. trailing ",,,," from Excel) are skipped and counted in input_problems.

--assume key=value  supply a value the operator did NOT provide; it is used but tagged ASSUMPTION
  keys: units_produced, labor_hours, labor_rate, overhead_per_batch, overhead_per_labor_hour,
        overhead_pct_materials, testing_cost, expected_units, cost:<component>, cost_uom:<component>
  Pass 0 explicitly (not via --assume) when the operator confirms a cost is truly zero.

Outputs (in --out-dir, default ./cogs_out): cogs_lines.csv, summary.json
"""
import argparse
import csv
import json
import os
import re
import sys

ALIASES = {
    "component": ["component", "item", "input", "material", "ingredient", "description", "component name"],
    "qty": ["qty", "quantity", "qty per batch", "quantity used", "amount", "qty used"],
    "uom": ["uom", "unit", "units", "unit of measure", "qty uom"],
    "unit_cost": ["unit cost", "cost", "price", "cost per unit", "unit price", "cost/unit"],
    "cost_uom": ["cost uom", "cost unit", "price unit", "price uom", "per", "cost per"],
}
CONV = {  # to base: g for weight, ml for volume, each for count
    "g": ("w", 1.0), "gram": ("w", 1.0), "grams": ("w", 1.0), "mg": ("w", 0.001),
    "kg": ("w", 1000.0), "lb": ("w", 453.592), "lbs": ("w", 453.592), "pound": ("w", 453.592),
    "oz": ("w", 28.3495), "ml": ("v", 1.0), "l": ("v", 1000.0), "liter": ("v", 1000.0),
    "each": ("e", 1.0), "ea": ("e", 1.0), "unit": ("e", 1.0), "units": ("e", 1.0), "pc": ("e", 1.0),
    "pcs": ("e", 1.0), "ct": ("e", 1.0), "count": ("e", 1.0),
}
PARAMS = ["units_produced", "labor_hours", "labor_rate", "testing_cost"]
OH = ["overhead_per_batch", "overhead_per_labor_hour", "overhead_pct_materials"]


def nh(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " ").replace("$", "").strip())


def detect(headers, overrides):
    found, m = {}, {nh(h): h for h in headers}
    for f, al in ALIASES.items():
        if f in overrides:
            found[f] = overrides[f]
            continue
        hits = [m[a] for a in al if a in m]
        if len(hits) == 1:
            found[f] = hits[0]
        elif len(hits) > 1:
            found[f] = "AMBIGUOUS:" + "|".join(hits)
    return found


def num(s):
    s = str(s if s is not None else "").strip().replace(",", "").replace("$", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return "BAD"


def is_blank(row):
    for v in row.values():
        vals = v if isinstance(v, list) else [v]
        if any((x or "").strip() for x in vals):
            return False
    return True


def kv(pairs, what):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"Bad {what} '{p}'. Use key=value")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bom", required=True)
    ap.add_argument("--batch-name", default="")
    for p in PARAMS + OH + ["expected_units"]:
        ap.add_argument("--" + p.replace("_", "-"), type=float)
    ap.add_argument("--map", nargs="*")
    ap.add_argument("--assume", nargs="*")
    ap.add_argument("--out-dir", default="cogs_out")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    with open(a.bom, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    headers = list(rows[0].keys()) if rows else []
    m = detect(headers, kv(a.map, "mapping"))
    if a.detect_only:
        print(json.dumps({"mapping": m, "rows": len(rows), "headers": headers}, indent=2))
        return
    for req in ("component", "qty", "uom", "unit_cost"):
        if req not in m or m[req].startswith("AMBIGUOUS:"):
            sys.exit(f"Cannot identify BOM column '{req}' (found: {m.get(req, 'none')}). Headers: {headers}. "
                     f"Pass --map {req}=<Column>.")

    assume = kv(a.assume, "assumption")
    assumptions, missing = [], []
    vals = {}
    for p in PARAMS + OH + ["expected_units"]:
        v = getattr(a, p)
        if v is None and p in assume:
            v = float(assume[p])
            assumptions.append(f"{p} = {v} [ASSUMPTION]")
        vals[p] = v
    for p in PARAMS:
        if vals[p] is None:
            missing.append(p)
    oh_given = [p for p in OH if vals[p] is not None]
    if len(oh_given) == 0:
        missing.append("one of " + "/".join(OH) + " (pass 0 if the operator confirms no overhead)")
    elif len(oh_given) > 1:
        sys.exit(f"Give exactly one overhead method; got {oh_given}")

    lines, problems, notes = [], [], []  # problems block the run; notes are reported but do not block
    for p in ("units_produced", "expected_units"):
        if vals[p] is not None and vals[p] <= 0:
            problems.append(f"{p} must be greater than 0 (got {vals[p]:g}). "
                            + ("Leave --expected-units out if there is no expected count." if p == "expected_units"
                               else "Give the number of sellable finished units."))
    cu_col = m.get("cost_uom")
    if cu_col and cu_col.startswith("AMBIGUOUS:"):
        problems.append(f"More than one column could be the cost unit ({cu_col[len('AMBIGUOUS:'):].replace('|', ', ')}). "
                        f"Pass --map cost_uom=<Column>.")
        cu_col = None
    elif not cu_col:
        notes.append("No cost unit column found (the unit each price is quoted in, e.g. $/lb). Weight and volume "
                     "lines need it; count lines are read as price per each.")
    blank_rows, each_read = 0, []
    for i, r in enumerate(rows, start=2):
        if is_blank(r):
            blank_rows += 1
            continue
        comp = (r.get(m["component"]) or "").strip() or f"row{i}"
        qty = num(r.get(m["qty"]))
        uom = (r.get(m["uom"]) or "").strip().lower()
        cost = num(r.get(m["unit_cost"]))
        cuom = (r.get(cu_col) or "").strip().lower() if cu_col else ""
        cuom = re.sub(r"^(\$\s*/\s*|/\s*|per\s+)", "", cuom)  # "$/kg", "/kg", "per kg" all mean kg
        tag, note = "DATA", ""
        if not cuom:
            if f"cost_uom:{comp}" in assume:
                cuom = assume[f"cost_uom:{comp}"].strip().lower()
                tag = "ASSUMPTION"
                assumptions.append(f"cost unit of {comp} = per {cuom} [ASSUMPTION]")
            elif uom in CONV and CONV[uom][0] == "e":
                cuom = uom
                note = "cost unit blank; price read as per each"
                each_read.append(f"row {i} ({comp})")
            elif uom in CONV:
                missing.append(f"cost_uom:{comp} (row {i}): price per what unit? Quantity is in '{uom}' but the "
                               f"cost unit is blank. Add it to the BOM (e.g. g, lb, kg, ml).")
                cuom = None
        if cost is None and f"cost:{comp}" in assume:
            cost = float(assume[f"cost:{comp}"])
            tag = "ASSUMPTION"
            assumptions.append(f"unit cost of {comp} = {cost} per {cuom or uom or '?'} [ASSUMPTION]")
        if qty in (None, "BAD"):
            problems.append(f"row {i} ({comp}): quantity missing or non-numeric")
            continue
        if cost is None:
            missing.append(f"cost:{comp}")
            continue
        if cost == "BAD":
            problems.append(f"row {i} ({comp}): non-numeric unit cost")
            continue
        if cuom is None:
            continue
        if uom not in CONV or cuom not in CONV:
            problems.append(f"row {i} ({comp}): unknown unit '{uom}' or cost unit '{cuom or 'blank'}'")
            continue
        (k1, f1), (k2, f2) = CONV[uom], CONV[cuom]
        if k1 != k2:
            problems.append(f"row {i} ({comp}): qty unit '{uom}' and cost unit '{cuom}' are different kinds "
                            f"(weight/volume/each); give the conversion")
            continue
        if qty < 0:
            notes.append(f"row {i} ({comp}): negative quantity {qty:g} {uom}; it lowers the batch cost. "
                         f"Confirm it is a return or correction, not a typo.")
        if cost < 0:
            notes.append(f"row {i} ({comp}): negative unit cost {cost:g}; confirm it is intended.")
        qty_in_cost_uom = qty * f1 / f2
        lines.append({"line": comp, "type": "material", "qty": qty, "uom": uom,
                      "unit_cost": cost, "cost_uom": cuom, "qty_in_cost_uom": round(qty_in_cost_uom, 6),
                      "line_cost": round(qty_in_cost_uom * cost, 4), "source": tag, "note": note})
    if blank_rows:
        notes.append(f"Skipped {blank_rows} fully blank row(s) in the BOM.")
    if each_read:
        notes.append(f"Cost unit blank on {len(each_read)} count line(s), so the price was read as per each: "
                     f"{', '.join(each_read)}. Check none is priced per case or pack.")

    if missing or problems:
        out = {"status": "BLOCKED", "missing_inputs": missing, "input_problems": problems + notes,
               "how_to_fix": "Ask the operator for each missing value. If they want to proceed anyway, pass "
                             "--assume key=value so it is tagged ASSUMPTION. Pass 0 only if they confirm zero."}
        print(json.dumps(out, indent=2))
        sys.exit(2)

    materials = sum(x["line_cost"] for x in lines)
    labor = vals["labor_hours"] * vals["labor_rate"]
    if vals["overhead_per_batch"] is not None:
        overhead, oh_basis = vals["overhead_per_batch"], "per batch"
    elif vals["overhead_per_labor_hour"] is not None:
        overhead, oh_basis = vals["overhead_per_labor_hour"] * vals["labor_hours"], \
            f"{vals['overhead_per_labor_hour']}/labor hour x {vals['labor_hours']} h"
    else:
        overhead, oh_basis = materials * vals["overhead_pct_materials"] / 100.0, \
            f"{vals['overhead_pct_materials']}% of materials"

    def tagof(p):
        return "ASSUMPTION" if any(s.startswith(p + " ") for s in assumptions) else "DATA"

    lines.append({"line": "Direct labor", "type": "labor", "qty": vals["labor_hours"], "uom": "hour",
                  "unit_cost": vals["labor_rate"], "cost_uom": "hour", "qty_in_cost_uom": vals["labor_hours"],
                  "line_cost": round(labor, 4),
                  "source": "ASSUMPTION" if "ASSUMPTION" in (tagof("labor_hours"), tagof("labor_rate")) else "DATA",
                  "note": ""})
    oh_key = [p for p in OH if vals[p] is not None][0]
    oh_src, oh_note = tagof(oh_key), ""
    # Overhead built on an assumed base is itself an assumption.
    if oh_key == "overhead_pct_materials":
        assumed_mats = [x["line"] for x in lines if x["type"] == "material" and x["source"] == "ASSUMPTION"]
        if assumed_mats:
            oh_src, oh_note = "ASSUMPTION", "% of materials that include assumed values: " + "; ".join(assumed_mats)
    elif oh_key == "overhead_per_labor_hour" and tagof("labor_hours") == "ASSUMPTION":
        oh_src, oh_note = "ASSUMPTION", "per labor hour, and labor hours are assumed"
    if oh_note and oh_src != tagof(oh_key):
        assumptions.append(f"overhead line is an ASSUMPTION because it is {oh_note}")
    lines.append({"line": "Overhead (" + oh_basis + ")", "type": "overhead", "qty": "", "uom": "",
                  "unit_cost": "", "cost_uom": "", "qty_in_cost_uom": "", "line_cost": round(overhead, 4),
                  "source": oh_src, "note": oh_note})
    lines.append({"line": "Testing", "type": "testing", "qty": "", "uom": "", "unit_cost": "", "cost_uom": "",
                  "qty_in_cost_uom": "", "line_cost": round(vals["testing_cost"], 4), "source": tagof("testing_cost"),
                  "note": ""})

    total = sum(x["line_cost"] for x in lines)
    units = vals["units_produced"]
    for x in lines:
        x["cost_per_unit"] = round(x["line_cost"] / units, 4)
        x["pct_of_total"] = round(x["line_cost"] / total * 100, 2) if total else 0

    yv = None
    if vals["expected_units"] is not None:
        exp = vals["expected_units"]
        yv = {"expected_units": exp, "actual_units": units, "variance_units": units - exp,
              "variance_pct": round((units - exp) / exp * 100, 2),
              "cost_per_unit_at_expected": round(total / exp, 4),
              "cost_of_shortfall_per_unit": round(total / units - total / exp, 4)}

    # Sensitivity on top 3 cost drivers. Overhead tied to materials or labor moves with them.
    drivers = sorted(lines, key=lambda x: -x["line_cost"])[:3]
    sens = []
    for d in drivers:
        row = {"driver": d["line"], "base_line_cost": d["line_cost"]}
        for pct in (-20, -10, 10, 20):
            delta = d["line_cost"] * pct / 100.0
            extra = 0.0
            if d["type"] == "material" and vals["overhead_pct_materials"] is not None:
                extra = delta * vals["overhead_pct_materials"] / 100.0
            row[f"cost_per_unit_{pct:+d}%"] = round((total + delta + extra) / units, 4)
        sens.append(row)

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "cogs_lines.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lines[0].keys()))
        w.writeheader()
        w.writerows(lines)
    summary = {
        "status": "OK", "batch": a.batch_name, "bom_file": a.bom, "mapping": m,
        "units_produced": units, "materials": round(materials, 2), "labor": round(labor, 2),
        "overhead": round(overhead, 2), "overhead_basis": oh_basis, "testing": round(vals["testing_cost"], 2),
        "total_batch_cost": round(total, 2), "cost_per_unit": round(total / units, 4),
        "yield_variance": yv,
        "sensitivity_note": "Each driver varied alone; labor varied as a rate (overhead per labor hour unchanged); "
                            "when overhead is % of materials it moves with material drivers.",
        "sensitivity": sens, "assumptions": assumptions, "input_problems": notes,
        "lines_tagged_assumption": [x["line"] for x in lines if x["source"] == "ASSUMPTION"],
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
