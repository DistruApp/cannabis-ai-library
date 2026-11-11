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
  A row that repeats another row exactly is costed and noted in input_problems (possible double
  entry), as is a blank component name. A BOM with no component rows is BLOCKED.
  Text cells written to cogs_lines.csv that start with = + - @ get a leading apostrophe (csv_safe).
  Numbers are parsed strictly (see to_number): NaN, inf, decimal commas ("4,25", "1.234,56") and
  negative quantities or costs BLOCK the batch and are listed with row, column and raw value.
  Every problem in a row is listed in the same run (bad number, blank quantity, unknown or mixed units).
  Quantity and price must be in the same kind of unit (weight, volume or count). The script applies no
  density or pack size: the operator restates the line in one kind and reruns.
  Two non-blank headers with the same name stop the script (a CSV reader keeps only one of them). Two
  headers that read as the same field (e.g. "Unit Cost" and "unit_cost") are AMBIGUOUS: pass --map.

--overhead-pct-materials is a whole-number percentage: 12 means 12%. A value between 0 and 1
  (e.g. 0.12) is used as given (0.12%) and a warning is added to input_problems.
Numeric flags must be finite and not negative (units must be greater than 0); a bad value exits
  with a message.

--assume key=value  supply a value the operator did NOT provide; it is used but tagged ASSUMPTION
  keys: units_produced, labor_hours, labor_rate, overhead_per_batch, overhead_per_labor_hour,
        overhead_pct_materials, testing_cost, expected_units, cost:<component>, cost_uom:<component>
  Assumed numbers must be greater than 0.
  Pass 0 explicitly (not via --assume) when the operator confirms a cost is truly zero.

Outputs (in --out-dir, default ./cogs_out): cogs_lines.csv, summary.json
  The script stops before writing if either output path is the BOM file itself.
"""
import argparse
import csv
import json
import math
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
OUTPUTS = ("cogs_lines.csv", "summary.json")


def nh(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " ").replace("$", "").strip())


def detect(headers, overrides):
    by_name = {}  # every header that normalises to a name, so "Unit Cost" and "unit_cost" both count
    for h in headers:
        by_name.setdefault(nh(h), []).append(h)
    found = {}
    for f, al in ALIASES.items():
        if f in overrides:
            found[f] = overrides[f]
            continue
        hits = [h for a in al for h in by_name.get(a, [])]
        if len(hits) == 1:
            found[f] = hits[0]
        elif len(hits) > 1:
            found[f] = "AMBIGUOUS:" + "|".join(hits)
    return found


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


def cli_number(s):
    """argparse type for numeric flags: finite and not negative (0 is allowed: an operator-confirmed zero)."""
    v, prob = to_number(s)
    if prob or v is None:
        raise argparse.ArgumentTypeError(prob or "blank value")
    if v < 0:
        raise argparse.ArgumentTypeError(f"must not be negative (got '{s}')")
    return v


def assumed_number(key, raw):
    """--assume values are numbers the operator did not give; they must be finite and greater than 0."""
    v, prob = to_number(raw)
    if prob or v is None:
        sys.exit(f"Bad --assume {key}={raw}: {prob or 'blank value'}.")
    if v <= 0:
        sys.exit(f"Bad --assume {key}={raw}: an assumed value must be greater than 0. "
                 f"Pass a confirmed 0 as the flag itself, not via --assume.")
    return v


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
        ap.add_argument("--" + p.replace("_", "-"), type=cli_number)
    ap.add_argument("--map", nargs="*")
    ap.add_argument("--assume", nargs="*")
    ap.add_argument("--out-dir", default="cogs_out")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    try:
        with open(a.bom, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = list(reader.fieldnames or [])
    except OSError as e:
        sys.exit(f"Cannot read the BOM file {a.bom}: {e.strerror or e}.")
    except (UnicodeDecodeError, csv.Error) as e:
        sys.exit(f"Cannot read the BOM file {a.bom} as a UTF-8 CSV ({e}). Export it as CSV (UTF-8) and rerun.")
    if not headers:
        sys.exit(f"The BOM file {a.bom} is empty (no header row). Export the BOM again with its column headers.")
    dupes = [x for i, x in enumerate(headers) if x.strip() and x in headers[:i]]
    if dupes:  # the CSV reader keeps only the last of two same-named columns, so one would be lost silently
        sys.exit(f"The BOM has more than one column named {', '.join(repr(x) for x in dict.fromkeys(dupes))}. "
                 f"Ask the operator which one to use, rename or delete the other, and rerun.")
    overrides = kv(a.map, "mapping")
    for f, col in overrides.items():
        if f not in ALIASES:
            sys.exit(f"Bad --map {f}={col}: field must be one of {', '.join(ALIASES)}.")
        if col not in headers:
            sys.exit(f"Bad --map {f}={col}: the BOM has no column named '{col}'. Headers: {headers}.")
    m = detect(headers, overrides)
    if a.detect_only:
        print(json.dumps({"mapping": m, "rows": len(rows), "headers": headers}, indent=2, allow_nan=False))
        return
    for name in OUTPUTS:  # never let a report overwrite its own source file (also through a symlink)
        path = os.path.join(a.out_dir, name)
        if os.path.realpath(path) == os.path.realpath(a.bom) or (
                os.path.exists(path) and os.path.samefile(path, a.bom)):
            sys.exit(f"--out-dir {a.out_dir} would overwrite the BOM file {a.bom} with {name}. "
                     f"Choose a different --out-dir and rerun.")
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
            v = assumed_number(p, assume[p])
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
    pct = vals["overhead_pct_materials"]
    if pct is not None and 0 < pct < 1:
        notes.append(f"overhead_pct_materials is {pct:g}, so overhead was read as {pct:g}% of materials, not "
                     f"{pct * 100:g}%. The flag takes a whole-number percentage (12 means 12%). If {pct * 100:g}% "
                     f"was meant, rerun with --overhead-pct-materials {pct * 100:g}.")
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
    blank_rows, each_read, seen_rows = [], [], {}
    for i, r in enumerate(rows, start=2):
        if is_blank(r):
            blank_rows.append(i)
            continue
        key = tuple(sorted((k or "", str(v).strip()) for k, v in r.items()))
        if key in seen_rows:  # kept and costed, but the operator should rule out a double entry
            notes.append(f"row {i} repeats row {seen_rows[key]} exactly; both lines were costed. If one is a "
                         f"double entry, remove it and rerun.")
        else:
            seen_rows[key] = i
        comp = (r.get(m["component"]) or "").strip() or f"row{i}"
        if not (r.get(m["component"]) or "").strip():
            notes.append(f"row {i}: column '{m['component']}' is blank; the line is shown as '{comp}'. "
                         f"Ask which component it is.")
        raw_qty, raw_cost = (r.get(m["qty"]) or "").strip(), (r.get(m["unit_cost"]) or "").strip()
        qty, qty_prob = to_number(raw_qty)
        cost, cost_prob = to_number(raw_cost)
        if qty is not None and qty < 0:
            qty, qty_prob = None, ("negative quantity. A BOM line is the quantity consumed; net a return or "
                                   "correction into the line it corrects, or confirm the right figure")
        if cost is not None and cost < 0:
            cost, cost_prob = None, "negative unit cost; confirm the right figure"
        uom = (r.get(m["uom"]) or "").strip().lower()
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
        if cost is None and not cost_prob and f"cost:{comp}" in assume:
            cost = assumed_number(f"cost:{comp}", assume[f"cost:{comp}"])
            tag = "ASSUMPTION"
            assumptions.append(f"unit cost of {comp} = {cost} per {cuom or uom or '?'} [ASSUMPTION]")
        # Collect every problem in the row so the operator gets one complete list, not one per rerun.
        row_probs = [f"row {i} ({comp}): column '{col}' value '{raw}': {why}"
                     for col, raw, why in ((m["qty"], raw_qty, qty_prob), (m["unit_cost"], raw_cost, cost_prob))
                     if why]  # an unreadable or negative number blocks the batch; never guessed
        if qty is None and not qty_prob:
            row_probs.append(f"row {i} ({comp}): column '{m['qty']}' is blank (quantity missing)")
        cost_missing = cost is None and not cost_prob
        if cost_missing:
            missing.append(f"cost:{comp} (row {i}): column '{m['unit_cost']}' is blank")
        if cuom is not None:  # None: the blank price unit is already listed in missing_inputs
            if uom not in CONV or cuom not in CONV:
                bad = [f"{what} '{u or 'blank'}' in column '{col}'"
                       for what, u, col in (("unit", uom, m["uom"]), ("cost unit", cuom, cu_col or "none"))
                       if u not in CONV]
                row_probs.append(f"row {i} ({comp}): unknown {' and '.join(bad)}; known units: {', '.join(CONV)}")
            elif CONV[uom][0] != CONV[cuom][0]:
                row_probs.append(f"row {i} ({comp}): qty unit '{uom}' and cost unit '{cuom}' are different kinds "
                                 f"(weight/volume/each). The script applies no density or pack size: ask the "
                                 f"operator to restate this line's quantity or price in one kind of unit in the "
                                 f"BOM, and rerun")
        if row_probs or cost_missing or cuom is None:
            problems.extend(row_probs)
            continue
        f1, f2 = CONV[uom][1], CONV[cuom][1]
        qty_in_cost_uom = qty * f1 / f2
        lines.append({"line": comp, "type": "material", "qty": qty, "uom": uom,
                      "unit_cost": cost, "cost_uom": cuom, "qty_in_cost_uom": round(qty_in_cost_uom, 6),
                      "line_cost": round(qty_in_cost_uom * cost, 4), "source": tag, "note": note})
    if len(blank_rows) == len(rows):  # header only, or nothing but blank rows: there is nothing to cost
        problems.append(f"The BOM has no component rows (only the header{' and blank rows' if rows else ''}). "
                        f"Ask for the components consumed in this batch.")
    if blank_rows:
        where = (f"row {blank_rows[0]}" if len(blank_rows) == 1
                 else "rows " + ", ".join(str(n) for n in blank_rows))
        notes.append(f"Skipped {len(blank_rows)} fully blank row(s) in the BOM: {where}.")
    if each_read:
        notes.append(f"Cost unit blank on {len(each_read)} count line(s), so the price was read as per each: "
                     f"{', '.join(each_read)}. Check none is priced per case or pack.")

    if missing or problems:
        out = {"status": "BLOCKED", "missing_inputs": missing, "input_problems": problems + notes,
               "how_to_fix": "Ask the operator for each missing value, and for the right figure behind each "
                             "unreadable or negative number (never reinterpret it). If they want to proceed before "
                             "they have a figure, they choose a placeholder number and you pass it with --assume "
                             "key=value (cost:<component>=N for a BOM price) so it is tagged ASSUMPTION. 'Use "
                             "whatever' is not a number: never pick one yourself. Pass 0 only if they confirm zero."}
        print(json.dumps(out, indent=2, allow_nan=False))
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
    with open(os.path.join(a.out_dir, OUTPUTS[0]), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lines[0].keys()))
        w.writeheader()
        w.writerows([{k: csv_safe(v) for k, v in x.items()} for x in lines])
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
    with open(os.path.join(a.out_dir, OUTPUTS[1]), "w") as f:
        json.dump(summary, f, indent=2, allow_nan=False)
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
