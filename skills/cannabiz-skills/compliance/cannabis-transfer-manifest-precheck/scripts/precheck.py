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
  precheck_summary.json overall GO/HOLD, counts by flag, manual-verify list
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


def parse_overrides(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"Bad mapping '{p}'. Use field=Column Name")
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def load(path, overrides, label, required):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        headers = list(rows[0].keys()) if rows else []
    m = detect(headers, overrides)
    for req in required:
        if not ok(m, req):
            sys.exit(f"[{label}] Cannot identify '{req}' column (found: {m.get(req, 'none')}). "
                     f"Headers: {headers}. Pass --map-{label} {req}=<Column>.")
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

    orows, om = load(a.order, parse_overrides(a.map_order), "order", ["quantity"])
    mrows, mm = load(a.manifest, parse_overrides(a.map_manifest), "manifest", ["package_id", "quantity"])
    irows, im = load(a.inventory, parse_overrides(a.map_inventory), "inventory", ["package_id", "quantity"])
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

    passing = {v.strip().lower() for v in (a.passing_lab_values or [])}
    problems = []

    # Inventory index
    inv = {}
    for i, r in enumerate(irows, start=2):
        t = norm_tag(r.get(im["package_id"]))
        if not t:
            continue
        if t in inv:
            problems.append(f"inventory: duplicate tag {t} (row {i})")
            continue
        inv[t] = {"qty": to_number(r.get(im["quantity"])),
                  "uom": (r.get(im["uom"]) or "").strip() if ok(im, "uom") else "",
                  "lab": (r.get(im["lab_status"]) or "").strip() if ok(im, "lab_status") else None}

    # Order aggregated by join key
    order = defaultdict(lambda: {"qty": 0.0, "uom": "", "bad": False, "label": ""})
    for i, r in enumerate(orows, start=2):
        k = keyval(r, om, key)
        if not k:
            problems.append(f"order row {i}: blank {key}")
            continue
        q = to_number(r.get(om["quantity"]))
        o = order[k]
        o["label"] = r.get(om[key], "")
        u = (r.get(om["uom"]) or "").strip() if ok(om, "uom") else ""
        if q is None:
            o["bad"] = True
            problems.append(f"order row {i} ({k}): non-numeric quantity")
            continue
        if o["uom"] and u and unit_kind(u)[0] != unit_kind(o["uom"])[0]:
            o["bad"] = True
            problems.append(f"order: mixed units for {k}")
        kind, f = unit_kind(u or o["uom"])
        o["qty"] += q * (f or 1.0)
        o["uom"] = o["uom"] or u
        o["norm_kind"] = kind

    # Manifest lines
    lines = []
    tag_counts = Counter(norm_tag(r.get(mm["package_id"])) for r in mrows)
    manifest_by_key = defaultdict(float)
    manifest_key_kind = {}
    for i, r in enumerate(mrows, start=2):
        tag = norm_tag(r.get(mm["package_id"]))
        mq = to_number(r.get(mm["quantity"]))
        mu = (r.get(mm["uom"]) or "").strip() if ok(mm, "uom") else ""
        item = r.get(mm["item"], "") if ok(mm, "item") else ""
        flags = []
        if not tag:
            flags.append("BLANK_TAG")
        if tag and tag_counts[tag] > 1:
            flags.append("DUPLICATE_TAG_ON_MANIFEST")
        if mq is None:
            flags.append("BAD_QUANTITY")
        k = keyval(r, mm, key)
        if k not in order:
            flags.append("NOT_ON_ORDER")
        elif mq is not None:
            kind, fac = unit_kind(mu or order[k]["uom"])
            manifest_by_key[k] += mq * (fac or 1.0)
            manifest_key_kind[k] = kind
        iv = inv.get(tag)
        onhand = ""
        lab = ""
        if tag and iv is None:
            flags.append("NOT_IN_ACTIVE_INVENTORY")
        elif iv is not None:
            onhand = iv["qty"]
            lab = iv["lab"] if iv["lab"] is not None else ""
            if iv["lab"] is None:
                flags.append("NO_LAB_STATUS_COLUMN")
            elif not passing:
                flags.append("LAB_STATUS_UNCONFIRMED")
            elif iv["lab"].lower() not in passing:
                flags.append("LAB_NOT_PASSED")
            if mq is not None and iv["qty"] is not None:
                kind, mqn, ivn = compare_qty(mq, mu or iv["uom"], iv["qty"], iv["uom"] or mu)
                if kind in ("UOM_MISMATCH", "UNKNOWN_UOM"):
                    flags.append("MANIFEST_VS_INVENTORY_" + kind)
                elif mqn > ivn + 1e-9:
                    converted = (mu or "").lower() != (iv["uom"] or "").lower()
                    if converted and mqn - ivn < ROUNDING_G:
                        flags.append("UNIT_CONVERSION_ROUNDING")
                    else:
                        flags.append("EXCEEDS_ON_HAND")
            elif iv["qty"] is None:
                flags.append("INVENTORY_QTY_UNREADABLE")
        lines.append({"source": "manifest", "manifest_row": i, "package_id": tag, "item": item,
                      "join_key": k, "manifest_qty": "" if mq is None else mq, "manifest_uom": mu,
                      "on_hand_qty": onhand, "on_hand_uom": iv["uom"] if iv else "", "lab_status": lab,
                      "order_qty": "", "flags": ";".join(flags), "result": "HOLD" if flags else "GO"})

    # Order vs manifest totals per key
    for k, o in order.items():
        shipped = manifest_by_key.get(k)
        if shipped is None and not any(l["join_key"] == k for l in lines):
            lines.append({"source": "order", "manifest_row": "", "package_id": k if key == "package_id" else "",
                          "item": o["label"], "join_key": k, "manifest_qty": "", "manifest_uom": "",
                          "on_hand_qty": "", "on_hand_uom": "", "lab_status": "",
                          "order_qty": o["qty"], "flags": "ON_ORDER_NOT_ON_MANIFEST", "result": "HOLD"})
            continue
        mismatch = None
        if o["bad"]:
            mismatch = "ORDER_QTY_UNREADABLE"
        elif manifest_key_kind.get(k) and o.get("norm_kind") and manifest_key_kind[k] != o["norm_kind"]:
            mismatch = "ORDER_VS_MANIFEST_UOM_MISMATCH"
        elif shipped is not None and abs(shipped - o["qty"]) > 1e-9:
            mismatch = ("ORDER_QTY_ROUNDING" if o.get("norm_kind") == "weight"
                        and abs(shipped - o["qty"]) < ROUNDING_G else "ORDER_QTY_MISMATCH")
        for l in lines:
            if l["source"] == "manifest" and l["join_key"] == k:
                l["order_qty"] = o["qty"]
                if mismatch:
                    l["flags"] = ";".join(filter(None, [l["flags"], mismatch]))
                    l["result"] = "HOLD"

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "precheck_lines.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lines[0].keys()))
        w.writeheader()
        w.writerows(lines)

    flag_counts = Counter(fl for l in lines for fl in l["flags"].split(";") if fl)
    overall = "GO" if all(l["result"] == "GO" for l in lines) and not problems else "HOLD"
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
        "verify_manually": [{"check": c, "where": w} for c, w in MANUAL_VERIFY],
    }
    with open(os.path.join(a.out_dir, "precheck_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
