#!/usr/bin/env python3
"""Harvest yield analysis for cannabis cultivation batches.

Standard library only. Deterministic.

Usage:
  python3 yield.py --harvests HARVESTS.csv [--out-dir DIR] [--map field=Column ...]
                   [--weight-unit g|lb|kg|oz] [--detect-only]

  --weight-unit   unit for weight columns when the file has no unit column (no default:
                  required unless a 'uom' column is detected or mapped). If the file has a unit
                  column, it is only used for blank unit cells, and each such row is listed in
                  input_problems and flagged UNIT_FROM_WEIGHT_UNIT_ARG.

Data rules (nothing is dropped, merged or invented silently):
  - A row is left out of a ratio when it lacks that ratio's inputs: dry-down needs wet and dry;
    per plant / sq ft / light needs dry plus that count. It is left out of the matching aggregate
    numerator AND denominator, and the aggregate says how many batches it covers ("coverage").
  - Zero or negative weights and counts are reported, never divided by.
  - Duplicate harvest IDs are kept (not merged), flagged DUPLICATE_ID and reported.
  - A blank breakdown part shows blank, not 0%.
  - Fully blank rows are skipped and counted in input_problems.

One row per harvest batch. Required: harvest_id (or strain+room+date), wet_weight, dry_weight.
Optional: strain, room, harvest_date, plant_count, canopy_sqft, lights, flower_a, flower_b
(smalls), trim, waste, uom, cycle_cost.

Outputs (in --out-dir, default ./yield_out):
  yield_by_batch.csv   metrics per batch with anomaly flags
  summary.json         totals, rankings by strain and room, anomaly rule used
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys

ALIASES = {
    "harvest_id": ["harvest", "harvest id", "harvest name", "harvest batch", "batch", "batch id", "harvest batch name"],
    "strain": ["strain", "cultivar", "genetics", "item strain"],
    "room": ["room", "location", "grow room", "flower room"],
    "harvest_date": ["harvest date", "date", "harvested", "harvested date"],
    "plant_count": ["plant count", "plants", "plants harvested", "# plants", "number of plants"],
    "canopy_sqft": ["canopy sq ft", "canopy sqft", "canopy", "sq ft", "sqft", "canopy (sq ft)", "square feet"],
    "lights": ["lights", "fixtures", "light count", "# lights", "number of lights"],
    "wet_weight": ["wet weight", "wet", "wet wt", "total wet weight", "fresh weight"],
    "dry_weight": ["dry weight", "dry", "dry wt", "total dry weight", "cured weight"],
    "flower_a": ["a flower", "a-grade", "a grade", "flower a", "bigs", "top flower", "a flower weight"],
    "flower_b": ["b flower", "smalls", "b grade", "b-grade", "flower b", "popcorn"],
    "trim": ["trim", "shake", "trim weight", "shake/trim"],
    "waste": ["waste", "waste weight", "stems", "plant waste"],
    "uom": ["uom", "unit", "units", "unit of measure", "weight unit"],
    "cycle_cost": ["cycle cost", "room cost", "cost", "total cost", "cultivation cost", "direct cost"],
}
WEIGHT_FIELDS = ["wet_weight", "dry_weight", "flower_a", "flower_b", "trim", "waste"]
GRAMS_PER = {"g": 1.0, "gram": 1.0, "grams": 1.0, "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
             "lb": 453.592, "lbs": 453.592, "pound": 453.592, "pounds": 453.592,
             "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495}


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " "))


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


def num(s):
    s = (s or "").strip().replace(",", "").replace("$", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return "BAD"


def iqr_flags(values):
    """Return (low_fence, high_fence) using 1.5x IQR on the operator's own data; None if <4 points."""
    v = sorted(x for x in values if x is not None)
    if len(v) < 4:
        return None
    q = statistics.quantiles(v, n=4, method="inclusive")
    iqr = q[2] - q[0]
    return q[0] - 1.5 * iqr, q[2] + 1.5 * iqr


def is_blank(row):
    for v in row.values():
        vals = v if isinstance(v, list) else [v]
        if any((x or "").strip() for x in vals):
            return False
    return True


def r(x, n=4):
    return "" if x is None else round(x, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvests", required=True)
    ap.add_argument("--out-dir", default="yield_out")
    ap.add_argument("--map", nargs="*")
    ap.add_argument("--weight-unit")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    overrides = {}
    for p in a.map or []:
        if "=" not in p:
            sys.exit(f"Bad mapping '{p}'. Use field=Column Name")
        k, v = p.split("=", 1)
        overrides[k.strip()] = v.strip()

    with open(a.harvests, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    headers = list(rows[0].keys()) if rows else []
    m = detect(headers, overrides)
    if a.detect_only:
        print(json.dumps({"mapping": m, "rows": len(rows), "headers": headers}, indent=2))
        return

    for req in ("wet_weight", "dry_weight"):
        if req not in m or m[req].startswith("AMBIGUOUS:"):
            sys.exit(f"Cannot identify '{req}' column (found: {m.get(req, 'none')}). Headers: {headers}. "
                     f"Pass --map {req}=<Column>.")
    for k, v in m.items():
        if v.startswith("AMBIGUOUS:"):
            sys.exit(f"Ambiguous column for '{k}': {v[10:]}. Pass --map {k}=<Column>.")
    has_uom = "uom" in m
    if not has_uom and not a.weight_unit:
        sys.exit("No unit column found. State the weight unit explicitly with --weight-unit g|lb|kg|oz "
                 "(no default is assumed).")
    if a.weight_unit and a.weight_unit.lower() not in GRAMS_PER:
        sys.exit(f"Unknown --weight-unit '{a.weight_unit}'")

    problems, out = [], []
    blank_rows = 0
    PARTS = (("flower_a", "flower_a_pct"), ("flower_b", "flower_b_pct"), ("trim", "trim_pct"), ("waste", "waste_pct"))
    RATIOS = (("dry_g_per_plant", "plant_count", "plant count"), ("dry_g_per_sqft", "canopy_sqft", "canopy sq ft"),
              ("dry_g_per_light", "lights", "light count"))
    for i, row in enumerate(rows, start=2):
        if is_blank(row):
            blank_rows += 1
            continue
        get = lambda f: (row.get(m[f]) or "") if f in m else ""
        hid = get("harvest_id").strip() or "|".join(
            x.strip() for x in (get("strain"), get("room"), get("harvest_date")) if x.strip()) or f"row{i}"
        flags = []
        cell_unit = get("uom").strip().lower() if has_uom else ""
        if has_uom and not cell_unit:
            if not a.weight_unit:
                problems.append(f"row {i} ({hid}): unit cell is blank and no --weight-unit was given; row skipped. "
                                f"Ask which unit this batch was weighed in.")
                continue
            unit = a.weight_unit.lower()
            flags.append("UNIT_FROM_WEIGHT_UNIT_ARG")
            problems.append(f"row {i} ({hid}): unit cell is blank; filled from --weight-unit {unit}. "
                            f"Confirm this batch was weighed in {unit}.")
        else:
            unit = cell_unit or (a.weight_unit or "").lower()
        if unit not in GRAMS_PER:
            problems.append(f"row {i} ({hid}): unknown unit '{unit}'; row skipped")
            continue
        g = GRAMS_PER[unit]
        vals = {}
        for f in WEIGHT_FIELDS + ["plant_count", "canopy_sqft", "lights", "cycle_cost"]:
            v = num(get(f)) if f in m else None
            if v == "BAD":
                problems.append(f"row {i} ({hid}): non-numeric {f} '{get(f)}'; treated as blank")
                v = None
            if v is not None and f in WEIGHT_FIELDS:
                v *= g
            vals[f] = v
        wet, dry = vals["wet_weight"], vals["dry_weight"]
        use, why = {}, {}  # which aggregates this row can feed, and why not

        def bad(metric, reason):
            use[metric], why[metric] = False, reason

        wet_ok = wet is not None and wet > 0
        dry_ok = dry is not None and dry > 0
        wet_why = "no wet weight" if wet is None else f"wet weight {wet:g} g"
        dry_why = "no dry weight" if dry is None else f"dry weight {dry:g} g"
        if wet is None:
            flags.append("MISSING_WET")
            problems.append(f"row {i} ({hid}): wet weight is blank; left out of dry-down")
        elif wet <= 0:
            flags.append("BAD_WET")
            problems.append(f"row {i} ({hid}): wet weight is {wet:g}; left out of dry-down. Check the entry.")
        if dry is None:
            flags.append("MISSING_DRY")
            problems.append(f"row {i} ({hid}): dry weight is blank (still curing?); left out of dry-down, "
                            f"dry totals and every per-plant / sq ft / light figure")
        elif dry <= 0:
            flags.append("ZERO_DRY" if dry == 0 else "BAD_DRY")
            problems.append(f"row {i} ({hid}): dry weight is {dry:g}; treated as a data problem and left out of "
                            f"dry-down, dry totals and every per-plant / sq ft / light figure")
        use["wet_g"] = wet_ok
        if not wet_ok:
            why["wet_g"] = wet_why
        use["dry_g"] = dry_ok
        if not dry_ok:
            why["dry_g"] = dry_why
        use["dry_down_pct"] = wet_ok and dry_ok
        if not dry_ok:
            bad("dry_down_pct", dry_why)
        elif not wet_ok:
            bad("dry_down_pct", wet_why)
        elif dry > wet:
            flags.append("DRY_EXCEEDS_WET")
            problems.append(f"row {i} ({hid}): dry weight exceeds wet weight; check units/entry. Left out of dry-down.")
            bad("dry_down_pct", "dry exceeds wet")
        rec = {"harvest_id": hid, "strain": get("strain"), "room": get("room"), "harvest_date": get("harvest_date"),
               "source_unit": unit, "wet_g": r(wet, 2), "dry_g": r(dry, 2),
               "dry_down_pct": r((1 - dry / wet) * 100 if use["dry_down_pct"] else None, 2)}
        for metric, field, label in RATIOS:
            d = vals[field]
            use[metric] = False
            if field not in m:
                why[metric] = f"no {label} column"
            elif not dry_ok:
                why[metric] = dry_why
            elif d is None:
                why[metric] = f"no {label}"
            elif d <= 0:
                why[metric] = f"{label} is {d:g}"
                problems.append(f"row {i} ({hid}): {label} is {d:g}; {metric} left blank")
            else:
                use[metric] = True
            rec[metric] = r(dry / d if use[metric] else None, 2)
        parts = {k: vals[k] for k, _ in PARTS}
        present = [k for k in parts if parts[k] is not None]
        sellable = None
        if present and dry_ok:
            for k, col in PARTS:
                rec[col] = r(parts[k] / dry * 100 if parts[k] is not None else None, 2)
            total = sum(parts[k] for k in present)
            gap = dry - total
            rec["breakdown_total_g"] = r(total, 2)
            rec["unaccounted_g"] = r(gap, 2)
            blank_parts = [k for k, _ in PARTS if k in m and parts[k] is None]
            if blank_parts:
                rec["sum_check"] = "INCOMPLETE_BREAKDOWN"
                problems.append(f"row {i} ({hid}): breakdown cell(s) blank: {', '.join(blank_parts)}. Shown blank, "
                                f"not 0%; unaccounted_g ({gap:g} g) includes whatever they weigh.")
            else:
                rec["sum_check"] = "OK" if abs(gap) < 0.005 else ("UNACCOUNTED" if gap > 0 else "PARTS_EXCEED_DRY")
            if parts["flower_a"] is not None and parts["flower_b"] is not None:
                sellable = parts["flower_a"] + parts["flower_b"]
        else:
            for k, col in PARTS:
                rec[col] = ""
            rec["breakdown_total_g"] = rec["unaccounted_g"] = ""
            rec["sum_check"] = "NO_DRY_WEIGHT" if present else "NO_BREAKDOWN"
        cost = vals["cycle_cost"]
        rec["cost_per_dry_g"] = r(cost / dry if cost is not None and dry_ok else None, 4)
        rec["cost_per_flower_g"] = r(cost / sellable if cost is not None and sellable else None, 4)
        if cost is not None and dry_ok and present and sellable is None:
            problems.append(f"row {i} ({hid}): cost_per_flower_g left blank because A or B flower weight is blank")
        rec["flags"] = "".join(f + ";" for f in flags)
        # metrics this row is left out of (a column missing from the whole file is not a row problem)
        rec["excluded_from"] = ", ".join(k for k in ("dry_down_pct",) + tuple(x[0] for x in RATIOS)
                                         if not use[k] and not why[k].endswith(" column"))
        rec["_row"], rec["_wet"], rec["_dry"], rec["_use"], rec["_why"] = i, wet, dry, use, why
        rec["_counts"] = {metric: vals[field] for metric, field, _ in RATIOS}
        rec["_raw"] = tuple(sorted((k or "", str(v)) for k, v in row.items()))
        out.append(rec)
    if blank_rows:
        problems.append(f"Skipped {blank_rows} fully blank row(s).")

    # duplicate harvest IDs: keep every row, flag them, report
    seen = {}
    for x in out:
        seen.setdefault(x["harvest_id"], []).append(x)
    dup_ids = []
    for hid, xs in seen.items():
        if len(xs) > 1:
            dup_ids.append(hid)
            same = len({x["_raw"] for x in xs}) == 1
            for x in xs:
                x["flags"] += "DUPLICATE_ID;"
            problems.append(f"harvest ID {hid} appears on rows {', '.join(str(x['_row']) for x in xs)}"
                            f"{' (identical rows)' if same else ''}. All rows were kept and counted in totals and "
                            f"aggregates. If one is a re-entry, remove it and rerun.")

    # anomaly flags vs operator's own data (1.5x IQR)
    rule = "Flag when a batch falls outside Q1-1.5*IQR .. Q3+1.5*IQR of this file's own batches (needs >=4 batches)"
    fences = {}
    for metric in ("dry_down_pct", "dry_g_per_plant", "dry_g_per_sqft", "dry_g_per_light", "trim_pct", "cost_per_dry_g"):
        vals = [x[metric] for x in out if x[metric] != ""]
        fn = iqr_flags(vals)
        fences[metric] = None if fn is None else [round(fn[0], 4), round(fn[1], 4)]
        if fn:
            for x in out:
                if x[metric] != "" and (x[metric] < fn[0] or x[metric] > fn[1]):
                    x["flags"] += f"{metric}:{'LOW' if x[metric] < fn[0] else 'HIGH'};"
    for x in out:
        if x["sum_check"] in ("UNACCOUNTED", "PARTS_EXCEED_DRY", "INCOMPLETE_BREAKDOWN"):
            x["flags"] += f"{x['sum_check']}:{x['unaccounted_g']}g;"

    def coverage(xs, metric, field=None):
        if field and field not in m:
            return f"not computed: no {field} column"
        used = [x for x in xs if x["_use"][metric]]
        txt = f"{len(used)} of {len(xs)} batches"
        left = [x for x in xs if not x["_use"][metric]]
        if left:
            txt += f"; {len(left)} excluded: " + "; ".join(f"{x['harvest_id']} ({x['_why'][metric]})" for x in left)
        return txt

    def agg(xs):
        res = {"batches": len(xs)}
        dry_rows = [x for x in xs if x["_use"]["dry_g"]]
        res["dry_g"] = round(sum(x["_dry"] for x in dry_rows), 2)
        dd = [x for x in xs if x["_use"]["dry_down_pct"]]
        w, d = sum(x["_wet"] for x in dd), sum(x["_dry"] for x in dd)
        res["dry_down_pct"] = round((1 - d / w) * 100, 2) if dd and w else None
        for metric, field, _ in RATIOS:
            used = [x for x in xs if x["_use"][metric]]
            den = sum(x["_counts"][metric] for x in used)
            res[metric] = round(sum(x["_dry"] for x in used) / den, 2) if used and den else None
        res["coverage"] = {"dry_g": coverage(xs, "dry_g"), "dry_down_pct": coverage(xs, "dry_down_pct")}
        for metric, field, _ in RATIOS:
            res["coverage"][metric] = coverage(xs, metric, field)
        return res

    def group(key):
        buckets = {}
        for x in out:
            buckets.setdefault(x[key] or "(blank)", []).append(x)
        res = [dict({key: k}, **agg(xs)) for k, xs in buckets.items()]
        res.sort(key=lambda z: (z["dry_g_per_sqft"] is None, -(z["dry_g_per_sqft"] or 0)))
        return res

    public = [{k: v for k, v in x.items() if not k.startswith("_")} for x in out]
    os.makedirs(a.out_dir, exist_ok=True)
    if public:
        with open(os.path.join(a.out_dir, "yield_by_batch.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(public[0].keys()))
            w.writeheader()
            w.writerows(public)
    tw = sum(x["_wet"] for x in out if x["_use"]["wet_g"])
    td = sum(x["_dry"] for x in out if x["_use"]["dry_g"])
    dd_rows = [x for x in out if x["_use"]["dry_down_pct"]]
    dw, ddry = sum(x["_wet"] for x in dd_rows), sum(x["_dry"] for x in dd_rows)
    summary = {
        "file": a.harvests, "mapping": m, "batches": len(out),
        "total_wet_g": round(tw, 2), "total_dry_g": round(td, 2),
        "total_dry_lb": round(td / 453.592, 3),
        "overall_dry_down_pct": round((1 - ddry / dw) * 100, 2) if dw else None,
        "totals_coverage": {"total_wet_g": coverage(out, "wet_g"), "total_dry_g": coverage(out, "dry_g"),
                            "overall_dry_down_pct": coverage(out, "dry_down_pct")},
        "by_strain_ranked_by_g_per_sqft": group("strain"),
        "by_room_ranked_by_g_per_sqft": group("room"),
        "anomaly_rule": rule, "anomaly_fences": fences,
        "duplicate_harvest_ids": dup_ids,
        "flagged_batches": [{"harvest_id": x["harvest_id"], "flags": x["flags"]} for x in out if x["flags"]],
        "input_problems": problems,
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
