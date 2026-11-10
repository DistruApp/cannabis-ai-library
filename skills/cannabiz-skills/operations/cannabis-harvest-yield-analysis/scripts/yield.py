#!/usr/bin/env python3
"""Harvest yield analysis for cannabis cultivation batches.

Standard library only. Deterministic.

Usage:
  python3 yield.py --harvests HARVESTS.csv [--out-dir DIR] [--map field=Column ...]
                   [--weight-unit g|lb|kg|oz] [--detect-only]

  --weight-unit   unit for weight columns when the file has no unit column (no default:
                  required unless a 'uom' column is detected or mapped)

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
    for i, row in enumerate(rows, start=2):
        get = lambda f: row.get(m[f], "") if f in m else ""
        unit = (get("uom") if has_uom else "").strip().lower() or (a.weight_unit or "").lower()
        if unit not in GRAMS_PER:
            problems.append(f"row {i}: unknown or missing unit '{unit}' — row skipped")
            continue
        g = GRAMS_PER[unit]
        hid = get("harvest_id") or "|".join(x for x in (get("strain"), get("room"), get("harvest_date")) if x) or f"row{i}"
        vals = {}
        for f in WEIGHT_FIELDS + ["plant_count", "canopy_sqft", "lights", "cycle_cost"]:
            v = num(get(f)) if f in m else None
            if v == "BAD":
                problems.append(f"row {i} ({hid}): non-numeric {f} '{get(f)}'")
                v = None
            if v is not None and f in WEIGHT_FIELDS:
                v *= g
            vals[f] = v
        wet, dry = vals["wet_weight"], vals["dry_weight"]
        rec = {"harvest_id": hid, "strain": get("strain"), "room": get("room"), "harvest_date": get("harvest_date"),
               "source_unit": unit, "wet_g": r(wet, 2), "dry_g": r(dry, 2)}
        dd = (1 - dry / wet) if wet and dry is not None else None
        if wet is None or dry is None:
            problems.append(f"row {i} ({hid}): missing wet or dry weight")
        elif dry > wet:
            problems.append(f"row {i} ({hid}): dry weight exceeds wet weight — check units/entry")
        rec["dry_down_pct"] = r(dd * 100 if dd is not None else None, 2)
        pc, sq, lt = vals["plant_count"], vals["canopy_sqft"], vals["lights"]
        rec["dry_g_per_plant"] = r(dry / pc if dry is not None and pc else None, 2)
        rec["dry_g_per_sqft"] = r(dry / sq if dry is not None and sq else None, 2)
        rec["dry_g_per_light"] = r(dry / lt if dry is not None and lt else None, 2)
        parts = [vals[k] for k in ("flower_a", "flower_b", "trim", "waste")]
        if any(p is not None for p in parts) and dry is not None:
            fa, fb, tr, ws = [p or 0.0 for p in parts]
            total = fa + fb + tr + ws
            gap = dry - total
            rec["flower_a_pct"] = r(fa / dry * 100 if dry else None, 2)
            rec["flower_b_pct"] = r(fb / dry * 100 if dry else None, 2)
            rec["trim_pct"] = r(tr / dry * 100 if dry else None, 2)
            rec["waste_pct"] = r(ws / dry * 100 if dry else None, 2)
            rec["breakdown_total_g"] = r(total, 2)
            rec["unaccounted_g"] = r(gap, 2)
            rec["sum_check"] = "OK" if abs(gap) < 0.005 else ("UNACCOUNTED" if gap > 0 else "PARTS_EXCEED_DRY")
            sellable = fa + fb
        else:
            for k in ("flower_a_pct", "flower_b_pct", "trim_pct", "waste_pct", "breakdown_total_g", "unaccounted_g"):
                rec[k] = ""
            rec["sum_check"] = "NO_BREAKDOWN"
            sellable = None
        cost = vals["cycle_cost"]
        rec["cost_per_dry_g"] = r(cost / dry if cost is not None and dry else None, 4)
        rec["cost_per_flower_g"] = r(cost / sellable if cost is not None and sellable else None, 4)
        rec["flags"] = ""
        out.append(rec)

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
        if x["sum_check"] in ("UNACCOUNTED", "PARTS_EXCEED_DRY"):
            x["flags"] += f"{x['sum_check']}:{x['unaccounted_g']}g;"

    def group(key):
        agg = {}
        for x in out:
            k = x[key] or "(blank)"
            g = agg.setdefault(k, {"batches": 0, "wet_g": 0.0, "dry_g": 0.0, "plants": 0.0, "sqft": 0.0,
                                   "_plants_ok": True, "_sqft_ok": True})
            g["batches"] += 1
            g["wet_g"] += x["wet_g"] or 0
            g["dry_g"] += x["dry_g"] or 0
            pc = x["dry_g_per_plant"]
            sq = x["dry_g_per_sqft"]
            if pc == "":
                g["_plants_ok"] = False
            else:
                g["plants"] += x["dry_g"] / pc
            if sq == "":
                g["_sqft_ok"] = False
            else:
                g["sqft"] += x["dry_g"] / sq
        res = []
        for k, g in agg.items():
            res.append({key: k, "batches": g["batches"], "dry_g": round(g["dry_g"], 2),
                        "dry_down_pct": round((1 - g["dry_g"] / g["wet_g"]) * 100, 2) if g["wet_g"] else None,
                        "dry_g_per_plant": round(g["dry_g"] / g["plants"], 2) if g["_plants_ok"] and g["plants"] else None,
                        "dry_g_per_sqft": round(g["dry_g"] / g["sqft"], 2) if g["_sqft_ok"] and g["sqft"] else None})
        res.sort(key=lambda z: (z["dry_g_per_sqft"] is None, -(z["dry_g_per_sqft"] or 0)))
        return res

    os.makedirs(a.out_dir, exist_ok=True)
    if out:
        with open(os.path.join(a.out_dir, "yield_by_batch.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader()
            w.writerows(out)
    tw = sum(x["wet_g"] or 0 for x in out)
    td = sum(x["dry_g"] or 0 for x in out)
    summary = {
        "file": a.harvests, "mapping": m, "batches": len(out),
        "total_wet_g": round(tw, 2), "total_dry_g": round(td, 2),
        "total_dry_lb": round(td / 453.592, 3),
        "overall_dry_down_pct": round((1 - td / tw) * 100, 2) if tw else None,
        "by_strain_ranked_by_g_per_sqft": group("strain"),
        "by_room_ranked_by_g_per_sqft": group("room"),
        "anomaly_rule": rule, "anomaly_fences": fences,
        "flagged_batches": [{"harvest_id": x["harvest_id"], "flags": x["flags"]} for x in out if x["flags"]],
        "input_problems": problems,
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
