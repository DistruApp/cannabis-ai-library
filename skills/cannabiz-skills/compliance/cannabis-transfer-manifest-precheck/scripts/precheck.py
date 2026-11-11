#!/usr/bin/env python3
"""Pre-departure check of an outgoing cannabis transfer: order vs. manifest vs. inventory.

Standard library only. Deterministic: the same inputs always give the same output.

Usage:
  python3 precheck.py --order ORDER.csv --manifest MANIFEST.csv --inventory INVENTORY.csv
                      [--passing-lab-values "TestPassed" ...] [--out-dir DIR]
                      [--map-order field=Column ...] [--map-manifest ...] [--map-inventory ...]
                      [--detect-only]

  --detect-only        print detected column mappings, the order join key, and the DISTINCT
                       lab-status values found in the inventory file, then exit. Show these
                       to the user and have them confirm which lab values mean "passed".
  --passing-lab-values exact lab-status values (case-insensitive) that count as passed.
                       If omitted, every line is held as LAB_STATUS_UNCONFIRMED.

Outputs (in --out-dir, default ./precheck_out):
  precheck_lines.csv   one row per manifest line plus unmatched order lines, GO/HOLD each
  precheck_summary.json overall GO/HOLD, counts by flag, input problems, manual-verify list

The script never fills a blank unit from another file, never keeps one of two inventory
rows for the same tag, and never drops a row without saying so. Anything it can't check
puts the line on HOLD and adds an input_problems entry. Overall is HOLD whenever
input_problems is not empty. A quantity that is NaN, inf, negative or written with a
decimal comma is never guessed: the line is held as INVALID_NUMBER. When both the
manifest and inventory have an item (or SKU) column, each line's item must match the
package's (ITEM_MISMATCH / ITEM_MISSING); without one, verify_manually asks for it.
A tag that Excel turned into scientific notation ("1.23457E+23") is never matched: the
line holds as TAG_SCIENTIFIC_NOTATION. Text cells that a spreadsheet would run as a
formula are written with a leading apostrophe.
"""
import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

ALIASES = {
    "package_id": ["tag", "package tag", "label", "package label", "package id", "package #",
                   "package number", "metrc tag", "barcode", "global id", "biotrack id",
                   "inventory id", "packagelabel", "uid"],
    "sku": ["sku", "product code", "item code", "sku code"],
    "item": ["item", "item name", "product", "product name", "sku name", "itemname", "description"],
    "quantity": ["quantity", "qty", "on hand", "available", "current quantity", "remaining quantity",
                 "shipped qty", "ship qty", "quantity shipped", "ordered qty", "order qty",
                 "quantity ordered", "wholesale qty"],
    "uom": ["uom", "unit", "unit of measure", "unitofmeasurename", "units", "unit of measure name"],
    "lab_status": ["lab status", "testing status", "labtestingstate", "test status",
                   "lab testing state", "lab test status"],
}

GRAMS_PER = {"g": 1.0, "gram": 1.0, "grams": 1.0, "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
             "mg": 0.001, "milligram": 0.001, "milligrams": 0.001,
             "lb": 453.592, "lbs": 453.592, "pound": 453.592, "pounds": 453.592,
             "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495}
# Differences smaller than this, arising only from converting between units (e.g. 5 lb = 2267.96 g
# written as 2268 g), are flagged as rounding rather than as a real over-shipment. Still a HOLD:
# the manifest must be restated in the package's own unit.
ROUNDING_G = 0.5
EACH = {"each", "ea", "unit", "units", "count", "ct", "pcs", "pc", "piece", "pieces"}

MANUAL_VERIFY = [
    ("Receiving license is active and the license type may receive this product category",
     "State licensee lookup (URL in references/state-profiles.md) — check on the day of shipment"),
    ("Your own license is active for this activity (sale/transfer/transport)",
     "State licensee lookup / your license certificate"),
    ("Driver(s), vehicle, and route/ETA fields required on the manifest",
     "Your state's transport rules — NEEDS VERIFICATION unless cited in state-profiles.md"),
    ("Transfer type and any required pre-notification or departure timing",
     "Your state's traceability guidance — NEEDS VERIFICATION"),
    ("Packaging/labeling of each package matches what the receiver may accept",
     "Physical inspection against your state's labeling rules"),
    ("COA on file and matching the batch for each package (if not supplied as a file)",
     "Your COA records / lab portal"),
]


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " "))


def norm_tag(t):
    return re.sub(r"[\s\-]", "", (t or "").strip().upper())


def norm_text(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def norm_item(t):
    """Compare key for item names and SKUs: case, whitespace and punctuation are ignored."""
    return re.sub(r"[\W_]+", "", (t or "").lower())


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


def ok(m, f):
    return f in m and not m[f].startswith("AMBIGUOUS:")


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
    named = [h.strip() for h in headers if h and h.strip()]
    dupes = sorted({h for h in named if named.count(h) > 1})
    if dupes:
        sys.exit(f"[{label}] {path} has more than one column named {dupes}. Rename or remove the "
                 "extra column and rerun.")
    return headers, rows


def load(path, overrides, label, required):
    headers, rows = read_csv_rows(path, label)
    by_norm = {norm_header(h): h for h in headers}
    for field, col in overrides.items():
        if col not in headers:
            if norm_header(col) not in by_norm:
                sys.exit(f"[{label}] --map-{label} {field}={col}: there is no column named '{col}'. "
                         f"Headers: {headers}")
            overrides[field] = by_norm[norm_header(col)]
    m = detect(headers, overrides)
    for req in required:
        if not ok(m, req):
            sys.exit(f"[{label}] Cannot identify '{req}' column (found: {m.get(req, 'none')}). "
                     f"Headers: {headers}. Pass --map-{label} {req}=<Column>.")
    return rows, m


_THOUSANDS_RE = re.compile(r"^[+-]?\d{1,3}(,\d{3})+(\.\d+)?$")


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
_SCI_TAG_RE = re.compile(r"^\d+(\.\d+)?[eE][+-]\d+$")


def is_sci_tag(raw):
    return bool(_SCI_TAG_RE.match(re.sub(r"\s", "", raw or "")))


def parse_qty(raw):
    """to_number plus the rule that a quantity or weight can't be negative."""
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


def compare_qty(q1, u1, q2, u2):
    """Return (kind, q1_norm, q2_norm) or (problem, None, None)."""
    k1, f1 = unit_kind(u1)
    k2, f2 = unit_kind(u2)
    if k1 == "unknown" or k2 == "unknown":
        return "UNKNOWN_UOM", None, None
    if k1 != k2:
        return "UOM_MISMATCH", None, None
    return k1, q1 * f1, q2 * f2


def order_key(m_order, m_man):
    for k in ("package_id", "sku", "item"):
        if ok(m_order, k) and ok(m_man, k):
            return k
    return None


def keyval(row, m, k):
    v = row.get(m[k], "")
    return norm_tag(v) if k == "package_id" else norm_text(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--passing-lab-values", nargs="*")
    ap.add_argument("--out-dir", default="precheck_out")
    ap.add_argument("--map-order", nargs="*")
    ap.add_argument("--map-manifest", nargs="*")
    ap.add_argument("--map-inventory", nargs="*")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    orows, om = load(a.order, parse_overrides(a.map_order, "order"), "order", ["quantity"])
    mrows, mm = load(a.manifest, parse_overrides(a.map_manifest, "manifest"), "manifest", ["package_id", "quantity"])
    irows, im = load(a.inventory, parse_overrides(a.map_inventory, "inventory"), "inventory",
                     ["package_id", "quantity"])
    key = order_key(om, mm)

    lab_values = sorted({(r.get(im["lab_status"]) or "").strip() for r in irows}) if ok(im, "lab_status") else []
    if a.detect_only:
        print(json.dumps({"order_mapping": om, "manifest_mapping": mm, "inventory_mapping": im,
                          "order_join_key": key, "distinct_lab_status_values": lab_values,
                          "rows": {"order": len(orows), "manifest": len(mrows), "inventory": len(irows)}},
                         indent=2))
        return
    if key is None:
        sys.exit("No shared key between order and manifest (need package tag, SKU, or item name in both). "
                 "Pass --map-order / --map-manifest.")

    passing = {v.strip().lower() for v in (a.passing_lab_values or []) if v.strip()}  # blank never passes
    problems = []

    for label, m in (("manifest", mm), ("inventory", im)):
        if not ok(m, "uom"):
            problems.append(f"{label} file: no unit column found; quantities in it can't be compared "
                            f"and every affected line is held")

    # Inventory index. Rows sharing a tag are kept together, never reduced to one.
    inv_rows = defaultdict(list)
    blank_inv_rows = []
    for i, r in enumerate(irows, start=2):
        raw_tag = r.get(im["package_id"]) or ""
        t = norm_tag(raw_tag)
        if not t:
            blank_inv_rows.append(str(i))
            continue
        if is_sci_tag(raw_tag):
            problems.append(f"inventory row {i}, column '{im['package_id']}', value '{raw_tag.strip()}': "
                            "package tag is in scientific notation (Excel dropped the real digits); row "
                            "not used, so no manifest line can match it")
            continue
        raw_qty = (r.get(im["quantity"]) or "").strip()
        qty, qty_problem = parse_qty(raw_qty)
        if qty_problem:
            qty_problem = f"inventory row {i}, column '{im['quantity']}', value '{raw_qty}': {qty_problem}"
            problems.append(f"{qty_problem} ({t}); on hand not compared")
        elif qty is None:
            problems.append(f"inventory row {i} ({t}), column '{im['quantity']}': blank quantity; "
                            "on hand not compared")
        inv_rows[t].append({"row": i, "qty": qty, "qty_problem": qty_problem, "raw_qty": raw_qty,
                            "uom": (r.get(im["uom"]) or "").strip() if ok(im, "uom") else "",
                            "lab": (r.get(im["lab_status"]) or "").strip() if ok(im, "lab_status") else None,
                            "item": (r.get(im["item"]) or "").strip() if ok(im, "item") else "",
                            "sku": (r.get(im["sku"]) or "").strip() if ok(im, "sku") else "",
                            "dup": ""})
    if blank_inv_rows:
        problems.append(f"inventory row(s) {', '.join(blank_inv_rows)}: blank package tag; these rows "
                        "were not checked against the manifest")
    inv = {}
    for t, recs in inv_rows.items():
        if len(recs) == 1:
            inv[t] = recs[0]
            continue
        desc = "; ".join(f"row {r['row']}: {r['raw_qty'] or '(blank)'} {r['uom'] or '(blank unit)'}, "
                         f"lab status {r['lab'] or '(blank)'}" for r in recs)
        inv[t] = {"row": "", "qty": None, "qty_problem": None, "uom": "", "lab": None, "item": "", "sku": "",
                  "dup": desc}
        problems.append(f"inventory: duplicate tag {t} on {len(recs)} rows ({desc}); any manifest line "
                        "with this tag is held as DUPLICATE_INVENTORY_TAG")

    # Order aggregated by join key
    order = defaultdict(lambda: {"qty": 0.0, "uom": "", "bad": False, "invalid": [], "label": "",
                                 "unit_missing": False, "factors": set(), "rows": [], "sci": False})
    if not ok(om, "uom"):
        problems.append("order file: no unit column found; order quantities can't be compared with the "
                        "manifest (ORDER_UNIT_MISSING)")
    for i, r in enumerate(orows, start=2):
        k = keyval(r, om, key)
        if not k:
            problems.append(f"order row {i}: blank {key}")
            continue
        raw_q = (r.get(om["quantity"]) or "").strip()
        q, q_problem = parse_qty(raw_q)
        o = order[k]
        o["label"] = r.get(om[key], "")
        o["rows"].append(str(i))
        if key == "package_id" and is_sci_tag(o["label"]):
            o["sci"] = True
            problems.append(f"order row {i}, column '{om[key]}', value '{o['label'].strip()}': package tag "
                            "is in scientific notation (Excel dropped the real digits); held as "
                            "TAG_SCIENTIFIC_NOTATION")
        u = (r.get(om["uom"]) or "").strip() if ok(om, "uom") else ""
        if q_problem:
            msg = f"order row {i}, column '{om['quantity']}', value '{raw_q}': {q_problem}"
            o["invalid"].append(msg)
            problems.append(f"{msg} ({k}); order quantity not compared")
            continue
        if q is None:
            o["bad"] = True
            problems.append(f"order row {i} ({k}), column '{om['quantity']}': blank quantity")
            continue
        if not u:
            o["unit_missing"] = True
            if ok(om, "uom"):
                problems.append(f"order row {i} ({k}): blank unit; order quantity not compared (ORDER_UNIT_MISSING)")
            continue
        if o["uom"] and unit_kind(u)[0] != unit_kind(o["uom"])[0]:
            o["bad"] = True
            problems.append(f"order: mixed units for {k}")
        kind, f = unit_kind(u)
        o["qty"] += q * (f or 1.0)
        o["uom"] = o["uom"] or u
        o["norm_kind"] = kind
        o["factors"].add(f)

    for k, o in order.items():
        if len(o["rows"]) > 1:
            problems.append(f"order: {key} {k} is on {len(o['rows'])} rows ({', '.join(o['rows'])}); their "
                            "quantities were added together. Confirm this is not a copy-paste duplicate")

    # Item check: compare the manifest's item and/or SKU with the package's, where both files have it.
    item_fields = [f for f in ("item", "sku") if ok(im, f) and ok(mm, f)]
    extra_manual = []
    if not item_fields:
        why = ("inventory export had no item column" if not (ok(im, "item") or ok(im, "sku"))
               else "manifest had no item or SKU column to compare with the inventory's")
        extra_manual.append((f"Confirm each package's item matches the manifest ({why})",
                             "Physical package label and the inventory record for each tag"))

    # Manifest lines
    lines = []
    unusable_qty_rows = set()  # manifest rows whose own quantity or unit is unusable
    tag_counts = Counter(norm_tag(r.get(mm["package_id"])) for r in mrows)
    manifest_by_key = defaultdict(float)
    manifest_key_kind = {}
    manifest_key_factors = defaultdict(set)
    incomplete_keys = set()  # order keys with a manifest line whose quantity or unit is unusable
    for i, r in enumerate(mrows, start=2):
        raw_tag = r.get(mm["package_id"]) or ""
        tag = norm_tag(raw_tag)
        raw_mq = (r.get(mm["quantity"]) or "").strip()
        mq, mq_problem = parse_qty(raw_mq)
        mu = (r.get(mm["uom"]) or "").strip() if ok(mm, "uom") else ""
        item = r.get(mm["item"], "") if ok(mm, "item") else ""
        flags, notes = [], []

        def add(flag):
            if flag not in flags:
                flags.append(flag)

        if not tag:
            flags.append("BLANK_TAG")
            problems.append(f"manifest row {i}, column '{mm['package_id']}': blank package tag; line held as "
                            "BLANK_TAG")
        elif is_sci_tag(raw_tag):
            flags.append("TAG_SCIENTIFIC_NOTATION")
            notes.append(f"tag '{raw_tag.strip()}' is in scientific notation, so the real tag is lost; "
                         "re-export with the tag column formatted as text")
            problems.append(f"manifest row {i}, column '{mm['package_id']}', value '{raw_tag.strip()}': "
                            "package tag is in scientific notation (Excel dropped the real digits); line "
                            "held as TAG_SCIENTIFIC_NOTATION")
        if tag and tag_counts[tag] > 1:
            flags.append("DUPLICATE_TAG_ON_MANIFEST")
        if mq_problem:
            add("INVALID_NUMBER")
            msg = f"manifest row {i}, column '{mm['quantity']}', value '{raw_mq}': {mq_problem}"
            notes.append(msg + "; quantity not compared")
            problems.append(f"{msg} ({tag or 'blank tag'}); line held as INVALID_NUMBER")
        elif mq is None:
            flags.append("BAD_QUANTITY")
            notes.append("manifest quantity is blank; not compared")
            problems.append(f"manifest row {i} ({tag or 'blank tag'}), column '{mm['quantity']}': blank quantity; "
                            "line held as BAD_QUANTITY")
        if mq is None or not mu:
            unusable_qty_rows.add(i)
        if not mu:
            flags.append("MISSING_UNIT")
            notes.append("manifest unit is blank; quantity not compared with inventory or order")
            if ok(mm, "uom"):
                problems.append(f"manifest row {i} ({tag or 'blank tag'}): blank unit; line held as MISSING_UNIT")
        k = keyval(r, mm, key)
        if k not in order:
            flags.append("NOT_ON_ORDER")
        elif mq is None or not mu:
            incomplete_keys.add(k)
        else:
            kind, fac = unit_kind(mu)
            manifest_by_key[k] += mq * (fac or 1.0)
            manifest_key_kind[k] = kind
            manifest_key_factors[k].add(fac)
        iv = inv.get(tag)
        onhand = ""
        lab = ""
        if tag and iv is None:
            flags.append("NOT_IN_ACTIVE_INVENTORY")
        elif iv is not None and iv["dup"]:
            flags.append("DUPLICATE_INVENTORY_TAG")
            notes.append(f"inventory has this tag on more than one row ({iv['dup']}); on-hand and lab "
                         "status not checked")
        elif iv is not None:
            onhand = "" if iv["qty"] is None else iv["qty"]
            lab = iv["lab"] if iv["lab"] is not None else ""
            if iv["lab"] is None:
                flags.append("NO_LAB_STATUS_COLUMN")
            elif not passing:
                flags.append("LAB_STATUS_UNCONFIRMED")
            elif iv["lab"].lower() not in passing:
                flags.append("LAB_NOT_PASSED")
            if iv["lab"] == "":
                notes.append("lab status is blank in the inventory file")
            for f in item_fields:
                name = "item" if f == "item" else "SKU"
                mv, ivv = (r.get(mm[f]) or "").strip(), iv[f]
                if not mv or not ivv:
                    add("ITEM_MISSING")
                    side = "inventory" if not ivv else "manifest"
                    notes.append(f"{name} is blank in the {side} file (manifest '{mv}', inventory '{ivv}'); "
                                 "package not matched to the manifest line")
                    problems.append(f"{side} row {iv['row'] if side == 'inventory' else i} ({tag}), column "
                                    f"'{(im if side == 'inventory' else mm)[f]}': blank {name}; "
                                    f"manifest row {i} held as ITEM_MISSING")
                elif norm_item(mv) != norm_item(ivv):
                    add("ITEM_MISMATCH")
                    notes.append(f"manifest {name} '{mv}' but inventory {name} for this tag is '{ivv}'")
            if not iv["uom"]:
                flags.append("INVENTORY_UNIT_MISSING")
                notes.append("inventory unit is blank; quantity not compared with on hand")
                if ok(im, "uom"):
                    problems.append(f"inventory row {iv['row']} ({tag}): blank unit; manifest row {i} "
                                    "held as INVENTORY_UNIT_MISSING")
            if iv["qty_problem"]:
                add("INVALID_NUMBER")
                notes.append(iv["qty_problem"] + "; on hand not compared")
            elif mq is not None and iv["qty"] is not None:
                if not mu or not iv["uom"]:
                    pass  # already held above; never borrow a unit from the other file
                else:
                    kind, mqn, ivn = compare_qty(mq, mu, iv["qty"], iv["uom"])
                    if kind in ("UOM_MISMATCH", "UNKNOWN_UOM"):
                        flags.append("MANIFEST_VS_INVENTORY_" + kind)
                    elif mqn > ivn + 1e-9:
                        # Rounding only when the two units really differ (e.g. lb vs g), not "g" vs "Grams".
                        converted = unit_kind(mu)[1] != unit_kind(iv["uom"])[1]
                        if converted and mqn - ivn < ROUNDING_G:
                            flags.append("UNIT_CONVERSION_ROUNDING")
                        else:
                            flags.append("EXCEEDS_ON_HAND")
            elif iv["qty"] is None:
                flags.append("INVENTORY_QTY_UNREADABLE")
        lines.append({"source": "manifest", "manifest_row": i, "package_id": tag, "item": item,
                      "join_key": k, "manifest_qty": "" if mq is None else mq, "manifest_uom": mu,
                      "on_hand_qty": onhand, "on_hand_uom": iv["uom"] if iv else "", "lab_status": lab,
                      "order_qty": "", "flags": ";".join(flags), "result": "HOLD" if flags else "GO",
                      "notes": " | ".join(notes)})

    # Order vs manifest totals per key
    for k, o in order.items():
        shipped = manifest_by_key.get(k)
        order_qty = "" if o["unit_missing"] or o["bad"] or o["invalid"] else o["qty"]
        order_note = "; ".join(o["invalid"]) + "; order quantity not compared" if o["invalid"] else ""
        if shipped is None and not any(l["join_key"] == k for l in lines):
            lines.append({"source": "order", "manifest_row": "", "package_id": k if key == "package_id" else "",
                          "item": o["label"], "join_key": k, "manifest_qty": "", "manifest_uom": "",
                          "on_hand_qty": "", "on_hand_uom": "", "lab_status": "", "order_qty": order_qty,
                          "flags": "ON_ORDER_NOT_ON_MANIFEST" + (";INVALID_NUMBER" if o["invalid"] else "")
                                   + (";TAG_SCIENTIFIC_NOTATION" if o["sci"] else ""),
                          "result": "HOLD", "notes": order_note})
            continue
        mismatch, note = None, ""
        if o["invalid"]:
            mismatch, note = "INVALID_NUMBER", order_note
        elif o["bad"]:
            mismatch = "ORDER_QTY_UNREADABLE"  # blank quantity or mixed units on the order
        elif o["unit_missing"]:
            mismatch = "ORDER_UNIT_MISSING"
            note = "order unit is blank; order quantity not compared with the manifest"
        elif o["sci"]:
            mismatch = "TAG_SCIENTIFIC_NOTATION"
            note = "the order's tag for this line is in scientific notation; order not compared"
        elif k in incomplete_keys:
            mismatch = "ORDER_QTY_NOT_CHECKED"
            note = "a manifest line for this order line has no usable quantity or unit; order total not compared"
        elif manifest_key_kind.get(k) and o.get("norm_kind") and manifest_key_kind[k] != o["norm_kind"]:
            mismatch = "ORDER_VS_MANIFEST_UOM_MISMATCH"
        elif shipped is not None and abs(shipped - o["qty"]) > 1e-9:
            converted = len(manifest_key_factors[k] | o["factors"]) > 1
            mismatch = ("ORDER_QTY_ROUNDING" if o.get("norm_kind") == "weight" and converted
                        and abs(shipped - o["qty"]) < ROUNDING_G else "ORDER_QTY_MISMATCH")
        for l in lines:
            if l["source"] == "manifest" and l["join_key"] == k:
                l["order_qty"] = order_qty
                if mismatch == "ORDER_QTY_NOT_CHECKED" and l["manifest_row"] in unusable_qty_rows:
                    continue  # this line is the reason; its own flag already says it was not compared
                if note:
                    l["notes"] = " | ".join(filter(None, [l["notes"], note]))
                if mismatch:
                    if mismatch not in l["flags"].split(";"):
                        l["flags"] = ";".join(filter(None, [l["flags"], mismatch]))
                    l["result"] = "HOLD"

    if not lines:  # can't happen with a non-empty manifest; never let an empty check read as GO
        sys.exit("No manifest lines to check.")
    try:
        os.makedirs(a.out_dir, exist_ok=True)
        with open(os.path.join(a.out_dir, "precheck_lines.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(lines[0].keys()))
            w.writeheader()
            w.writerows([{k: csv_safe(v) for k, v in l.items()} for l in lines])
    except OSError as e:
        sys.exit(f"Cannot write to --out-dir {a.out_dir}: {e}")

    flag_counts = Counter(fl for l in lines for fl in l["flags"].split(";") if fl)
    overall = "GO" if lines and all(l["result"] == "GO" for l in lines) and not problems else "HOLD"
    summary = {
        "overall": overall,
        "note": "GO means no issues in the file-based checks only. Manual checks below are still required.",
        "order_join_key": key,
        "passing_lab_values_used": sorted(passing),
        "manifest_lines": sum(1 for l in lines if l["source"] == "manifest"),
        "lines_go": sum(1 for l in lines if l["result"] == "GO"),
        "lines_hold": sum(1 for l in lines if l["result"] == "HOLD"),
        "flags": dict(flag_counts),
        "input_problems": problems,
        "input_problems_rule": ("Overall is HOLD whenever input_problems is not empty, even if every line is GO: "
                                "an input problem can hide a problem with a shipped line."),
        "verify_manually": [{"check": c, "where": w} for c, w in extra_manual + MANUAL_VERIFY],
    }
    with open(os.path.join(a.out_dir, "precheck_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, allow_nan=False)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
