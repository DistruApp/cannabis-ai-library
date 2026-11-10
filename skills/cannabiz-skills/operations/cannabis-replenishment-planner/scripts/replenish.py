#!/usr/bin/env python3
"""Compute sell-through, days of supply, reorder points, and a draft PO by vendor.

Standard library only. Deterministic: the same inputs and flags always give the same output.

Usage:
  python3 replenish.py --sales SALES.csv --onhand ONHAND.csv [--out-dir DIR]
                       [--map-sales field=Column ...] [--map-onhand field=Column ...]
                       [--window-days 28] [--as-of YYYY-MM-DD]
                       [--default-lead-time DAYS] [--safety-days N] [--cover-days N]
                       [--dead-days N] [--slow-dos N] [--vendor-from-brand] [--detect-only]

  --detect-only        print detected column mappings and data date range, then exit.
  --default-lead-time  used ONLY for SKUs whose lead time cell is truly blank; those SKUs are
                       flagged DEFAULT_LEAD_TIME(Nd). "7 days" / "2 weeks" are parsed; anything else
                       unreadable is flagged BAD_LEAD_TIME and not ordered.
  --vendor-from-brand  the operator confirmed brand = vendor: a blank vendor is filled from brand and
                       flagged VENDOR_FROM_BRAND. Without it a blank vendor is flagged NO_VENDOR and the
                       line is kept off the vendor PO draft (listed under lines_needing_vendor).

Data rules (nothing is dropped, merged or invented silently):
  - Duplicate on-hand rows for one SKU: on-hand and open PO are summed. Unit cost, case pack, lead
    time and vendor must agree (or be blank on all but one row); if they conflict the SKU is flagged
    CONFLICTING_ROWS, no order is suggested, and both values go in input_problems.
  - Non-numeric open PO (BAD_OPEN_PO) holds the SKU; non-numeric case pack (BAD_CASE_PACK) leaves the
    quantity unrounded; non-numeric unit cost (BAD_UNIT_COST) leaves cost blank. All are reported.

Defaults that are NOT operator-provided are listed in summary.json "assumptions" so
the report can tag them [ASSUMPTION]. No industry benchmarks are built in.

Outputs (in --out-dir, default ./replen_out):
  replenishment.csv  one row per SKU: velocity, sell-through, days of supply, flags, suggested qty
  po_draft.csv       suggested order lines grouped by vendor (DRAFT - never sent)
  summary.json       totals, flags, assumptions, input problems
"""
import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

SALES_ALIASES = {
    "date": ["date", "sale date", "order date", "transaction date", "sold date", "invoice date", "completed date"],
    "sku": ["sku", "product code", "item code", "product id", "sku id"],
    "product": ["product", "product name", "item", "item name", "sku name"],
    "brand": ["brand", "brand name", "vendor", "manufacturer", "supplier"],
    "category": ["category", "product category", "item category", "type"],
    "units": ["units", "qty", "quantity", "units sold", "qty sold", "quantity sold"],
    "revenue": ["revenue", "net sales", "sales", "total", "net revenue", "gross sales", "line total", "amount"],
}
ONHAND_ALIASES = {
    "sku": ["sku", "product code", "item code", "product id", "sku id"],
    "product": ["product", "product name", "item", "item name", "sku name"],
    "brand": ["brand", "brand name", "manufacturer"],
    "vendor": ["vendor", "supplier", "distributor", "vendor name"],
    "on_hand": ["on hand", "on_hand", "onhand", "qty on hand", "quantity on hand", "available", "current quantity",
                "inventory", "available qty"],
    "unit_cost": ["unit cost", "cost", "cost per unit", "wholesale cost", "cogs/unit"],
    "case_pack": ["case pack", "case size", "pack size", "moq", "min order qty", "order multiple"],
    "lead_time_days": ["lead time", "lead time days", "lead_time_days", "lead days"],
    "open_po_qty": ["open po", "open po qty", "on order", "incoming", "qty on order"],
}
REQUIRED_SALES = ("date", "sku", "units")
REQUIRED_ONHAND = ("sku", "on_hand")
DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M",
                "%m/%d/%Y %I:%M %p", "%Y-%m-%dT%H:%M:%S")


def norm_header(h):
    return re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " "))


def detect(headers, aliases, overrides):
    found, nh = {}, {norm_header(h): h for h in headers}
    for field, alist in aliases.items():
        if field in overrides:
            found[field] = overrides[field]
            continue
        hits = []
        for a in alist:
            h = nh.get(norm_header(a))
            if h and h not in hits:
                hits.append(h)
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


def load(path, aliases, overrides, required, label):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        headers = list(rows[0].keys()) if rows else []
    m = detect(headers, aliases, overrides)
    for req in required:
        if req not in m or m[req].startswith("AMBIGUOUS:"):
            sys.exit(f"[{label}] Cannot identify '{req}' column (found: {m.get(req, 'none')}). "
                     f"Headers: {headers}. Pass --map-{label} {req}=<Column>.")
    # drop ambiguous optional fields so they are not silently used
    clean = {k: v for k, v in m.items() if not v.startswith("AMBIGUOUS:")}
    return rows, m, clean


def num(s):
    """None for blank, "BAD" for text that is not a number, else float."""
    s = (s or "").strip().replace(",", "").replace("$", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return "BAD"


def parse_lead(s):
    """Lead time in days. Accepts 7, 7d, 7 days, 2 wk, 2 weeks. None if blank, "BAD" if unreadable."""
    s = (s or "").strip().lower()
    if s == "":
        return None
    mt = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(d|day|days|w|wk|wks|week|weeks)?\.?", s)
    if not mt:
        return "BAD"
    n = float(mt.group(1))
    return n * 7 if (mt.group(2) or "").startswith("w") else n


def parse_date(s):
    s = (s or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def get(r, m, field):
    return (r.get(m[field], "") or "").strip() if field in m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sales", required=True)
    ap.add_argument("--onhand", required=True)
    ap.add_argument("--out-dir", default="replen_out")
    ap.add_argument("--map-sales", nargs="*")
    ap.add_argument("--map-onhand", nargs="*")
    ap.add_argument("--window-days", type=int, default=None)
    ap.add_argument("--as-of", default=None, help="End date of the sales window (default: last date in sales data)")
    ap.add_argument("--default-lead-time", type=float, default=None)
    ap.add_argument("--safety-days", type=float, default=None)
    ap.add_argument("--cover-days", type=float, default=None,
                    help="Days of demand to cover after the order arrives (order-up-to horizon)")
    ap.add_argument("--dead-days", type=int, default=None)
    ap.add_argument("--slow-dos", type=float, default=None, help="Flag SLOW when days of supply exceed this")
    ap.add_argument("--vendor-from-brand", action="store_true",
                    help="Operator confirmed brand = vendor: fill blank vendor from brand (flagged VENDOR_FROM_BRAND)")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    srows, sm_raw, sm = load(a.sales, SALES_ALIASES, parse_overrides(a.map_sales), REQUIRED_SALES, "sales")
    orows, om_raw, om = load(a.onhand, ONHAND_ALIASES, parse_overrides(a.map_onhand), REQUIRED_ONHAND, "onhand")

    problems = []
    dates = []
    for i, r in enumerate(srows, start=2):
        d = parse_date(get(r, sm, "date"))
        if d is None:
            problems.append(f"sales row {i}: unparseable date '{get(r, sm, 'date')}'")
        else:
            dates.append(d)
    if not dates:
        sys.exit("No parseable sales dates.")

    if a.detect_only:
        print(json.dumps({"sales_mapping": sm_raw, "onhand_mapping": om_raw, "sales_rows": len(srows),
                          "onhand_rows": len(orows), "sales_date_range": [str(min(dates)), str(max(dates))]},
                         indent=2))
        return

    assumptions = []

    def pick(val, default, name, unit):
        if val is None:
            assumptions.append(f"{name} = {default} {unit} (script default, not operator-provided)")
            return default
        return val

    window = pick(a.window_days, 28, "window_days", "days")
    safety = pick(a.safety_days, 0.0, "safety_days", "days")
    cover = pick(a.cover_days, 14.0, "cover_days", "days")
    dead_days = pick(a.dead_days, 30, "dead_days", "days")
    slow_dos = pick(a.slow_dos, 90.0, "slow_dos", "days of supply")

    as_of = parse_date(a.as_of) if a.as_of else max(dates)
    if as_of is None:
        sys.exit(f"Bad --as-of '{a.as_of}'")
    start = as_of - timedelta(days=window - 1)
    recent_start = as_of - timedelta(days=6)

    sales = defaultdict(lambda: {"units": 0.0, "units_recent7": 0.0, "revenue": 0.0, "first": None, "last": None,
                                 "first_in_window": None, "product": "", "brand": "", "category": "", "neg": 0.0})
    for i, r in enumerate(srows, start=2):
        d = parse_date(get(r, sm, "date"))
        sku = get(r, sm, "sku")
        u = num(get(r, sm, "units"))
        if d is None:
            continue
        if not sku:
            problems.append(f"sales row {i}: blank sku")
            continue
        if u is None or u == "BAD":
            problems.append(f"sales row {i} ({sku}): non-numeric units '{get(r, sm, 'units')}'")
            continue
        s = sales[sku]
        s["product"] = s["product"] or get(r, sm, "product")
        s["brand"] = s["brand"] or get(r, sm, "brand")
        s["category"] = s["category"] or get(r, sm, "category")
        if d > as_of:
            continue
        s["first"] = d if s["first"] is None else min(s["first"], d)
        if u > 0:
            s["last"] = d if s["last"] is None else max(s["last"], d)
        if d >= start:
            s["units"] += u
            if u < 0:
                s["neg"] += u
            rev = num(get(r, sm, "revenue"))
            if rev == "BAD":
                problems.append(f"sales row {i} ({sku}): non-numeric revenue '{get(r, sm, 'revenue')}' left out "
                                f"of revenue_window")
            elif rev is not None:
                s["revenue"] += rev
            if d >= recent_start:
                s["units_recent7"] += u

    # ---- on-hand: group rows by SKU so duplicates are combined openly, never by keeping the first row
    by_sku = defaultdict(list)
    for i, r in enumerate(orows, start=2):
        sku = get(r, om, "sku")
        if not sku:
            problems.append(f"onhand row {i}: blank sku")
            continue
        by_sku[sku].append((i, r))
    onhand = {}
    ATTRS = (("unit_cost", "unit cost", num), ("case_pack", "case pack", num),
             ("lead_time_days", "lead time", parse_lead), ("vendor", "vendor", None))
    for sku, rws in by_sku.items():
        rec = {"rows": [i for i, _ in rws], "on_hand": 0.0, "open_po": 0.0, "flags": [], "hold": False,
               "product": next((get(r, om, "product") for _, r in rws if get(r, om, "product")), ""),
               "brand": next((get(r, om, "brand") for _, r in rws if get(r, om, "brand")), ""),
               "lead_status": "blank"}
        good_rows = 0
        for i, r in rws:
            q = num(get(r, om, "on_hand"))
            if q is None or q == "BAD":
                problems.append(f"onhand row {i} ({sku}): non-numeric on-hand '{get(r, om, 'on_hand')}'")
                if len(rws) > 1:
                    rec["flags"].append(f"BAD_ONHAND_ROW(row {i})")
                    rec["hold"] = True
                continue
            good_rows += 1
            rec["on_hand"] += q
            po = num(get(r, om, "open_po_qty"))
            if po == "BAD":
                problems.append(f"onhand row {i} ({sku}): open PO '{get(r, om, 'open_po_qty')}' is not a number; "
                                f"no order suggested until the open PO is confirmed")
                rec["flags"].append("BAD_OPEN_PO")
                rec["hold"] = True
            elif po is not None:
                rec["open_po"] += po
        if good_rows == 0:
            continue  # single unreadable row: SKU shows as NO_ONHAND_RECORD, as reported above
        if len(rws) > 1:
            problems.append(f"onhand: SKU {sku} is on rows {', '.join(map(str, rec['rows']))}; on-hand "
                            f"({rec['on_hand']:g}) and open PO ({rec['open_po']:g}) are the sums of those rows")
        for field, label, parse in ATTRS:
            vals = []  # (row, raw text, parsed)
            for i, r in rws:
                raw = get(r, om, field)
                if raw == "":
                    continue
                v = parse(raw) if parse else raw
                if v == "BAD":
                    tag = {"unit_cost": "BAD_UNIT_COST", "case_pack": "BAD_CASE_PACK",
                           "lead_time_days": "BAD_LEAD_TIME"}[field]
                    rec["flags"].append(tag)
                    effect = {"unit_cost": "order cost left blank",
                              "case_pack": "suggested quantity is NOT rounded to a case pack",
                              "lead_time_days": "no default used and no order suggested until a lead time in days "
                                                "is given"}[field]
                    problems.append(f"onhand row {i} ({sku}): {label} '{raw}' is not readable; {effect}")
                    if field == "lead_time_days":
                        rec["lead_status"] = "bad"
                    continue
                if field == "case_pack" and v <= 0:
                    rec["flags"].append("BAD_CASE_PACK")
                    problems.append(f"onhand row {i} ({sku}): case pack '{raw}' is not a positive number; suggested "
                                    f"quantity is NOT rounded to a case pack")
                    continue
                if field == "lead_time_days" and not re.fullmatch(r"\d+(\.\d+)?", raw):
                    problems.append(f"onhand row {i} ({sku}): lead time '{raw}' read as {v:g} days")
                vals.append((i, raw, v))
            distinct = {v for _, _, v in vals}
            if len(distinct) > 1:
                rec["flags"].append(f"CONFLICTING_ROWS({label})")
                rec["hold"] = True
                problems.append(f"onhand: SKU {sku} rows disagree on {label}: "
                                + "; ".join(f"row {i} '{raw}'" for i, raw, _ in vals)
                                + ". No order suggested until the operator says which is right.")
                rec[field] = None
                if field == "lead_time_days":
                    rec["lead_status"] = "conflict"
            else:
                rec[field] = vals[0][2] if vals else None
                if field == "lead_time_days" and vals and rec["lead_status"] != "bad":
                    rec["lead_status"] = "ok"
        if rec["lead_status"] == "bad":
            rec["lead_time_days"] = None  # an unreadable cell is never silently outvoted by another row
        rec["vendor"] = rec["vendor"] or ""
        onhand[sku] = rec

    vendor_brand_used = False
    out, po_lines, needs_vendor = [], [], []
    missing_lead, default_lead, held = [], [], []
    for sku in sorted(set(sales) | set(onhand)):
        s = sales.get(sku)
        o = onhand.get(sku)
        flags = []
        units = s["units"] if s else 0.0
        days = window
        if s and s["first"] is not None and s["first"] > start:
            days = (as_of - s["first"]).days + 1
            flags.append(f"NEW_SKU({days}d of history)")
        rate = units / days if days > 0 else 0.0
        oh = o["on_hand"] if o else None
        open_po = o["open_po"] if o else 0.0
        vendor = o["vendor"] if o else ""
        if o and not vendor:
            if a.vendor_from_brand and o["brand"]:
                vendor = o["brand"]
                flags.append("VENDOR_FROM_BRAND")
                vendor_brand_used = True
            elif not any(f.startswith("CONFLICTING_ROWS(vendor") for f in o["flags"]):
                flags.append("NO_VENDOR")
        row = {"sku": sku,
               "product": (o and o["product"]) or (s and s["product"]) or "",
               "brand": (o and o["brand"]) or (s and s["brand"]) or "",
               "category": (s and s["category"]) or "",
               "vendor": vendor,
               "units_sold_window": round(units, 3), "days_measured": days,
               "units_per_day": round(rate, 4),
               "revenue_window": round(s["revenue"], 2) if s else 0.0,
               "on_hand": oh if oh is not None else "", "open_po_qty": open_po,
               "sell_through_pct": "", "days_of_supply": "", "lead_time_days": "", "reorder_point": "",
               "suggested_order_qty": 0, "case_pack": "", "unit_cost": "", "order_cost": "",
               "last_sale": str(s["last"]) if s and s["last"] else "", "flags": ""}
        if s and s["neg"] < 0:
            flags.append(f"RETURNS_IN_WINDOW({s['neg']:g})")
        if o is None:
            flags.append("NO_ONHAND_RECORD")
        else:
            flags.extend(o["flags"])
            denom = units + oh
            if denom > 0:
                row["sell_through_pct"] = round(100.0 * units / denom, 1)
            if rate > 0:
                row["days_of_supply"] = round(oh / rate, 1)
            else:
                row["days_of_supply"] = "no sales" if oh > 0 else ""
            lead = o["lead_time_days"]
            if o["lead_status"] == "blank" and a.default_lead_time is not None:
                lead = a.default_lead_time
                flags.append(f"DEFAULT_LEAD_TIME({lead:g}d)")
                default_lead.append(sku)
            if oh <= 0 and s and s["units_recent7"] > 0:
                flags.append("STOCKOUT(demand understated)")
            elif oh <= 0 and rate > 0:
                flags.append("STOCKOUT")
            if oh > 0 and (not s or s["last"] is None or (as_of - s["last"]).days >= dead_days):
                flags.append(f"DEAD(no sales {dead_days}d+)")
            elif rate > 0 and oh / rate > slow_dos:
                flags.append("SLOW")
            if o["hold"]:
                held.append(sku)
            if lead is None:
                if rate > 0:
                    missing_lead.append(sku)
                    if o["lead_status"] == "blank":
                        flags.append("NO_LEAD_TIME")
            elif not o["hold"]:
                row["lead_time_days"] = lead
                rop = rate * (lead + safety)
                row["reorder_point"] = round(rop, 2)
                if rate > 0 and oh + open_po <= rop:
                    target = rate * (lead + safety + cover)
                    need = max(0.0, target - oh - open_po)
                    qty = math.ceil(need - 1e-9)
                    cp = o["case_pack"]
                    if cp and cp > 0:
                        qty = int(math.ceil(qty / cp) * cp)
                        row["case_pack"] = cp
                    if qty > 0:
                        row["suggested_order_qty"] = qty
                        flags.append("REORDER")
                        cost = o["unit_cost"]
                        if cost is not None:
                            row["unit_cost"] = cost
                            row["order_cost"] = round(qty * cost, 2)
                        line = {"vendor": vendor, "sku": sku,
                                "product": row["product"], "qty": qty,
                                "case_pack": cp or "", "unit_cost": cost if cost is not None else "",
                                "line_cost": round(qty * cost, 2) if cost is not None else "",
                                "days_of_supply_now": row["days_of_supply"],
                                "flags": ";".join(flags)}
                        (po_lines if vendor else needs_vendor).append(line)
        row["flags"] = ";".join(flags)
        out.append(row)
    if vendor_brand_used:
        assumptions.append("vendor filled from brand where the vendor cell was blank (--vendor-from-brand, "
                           "operator said brand = vendor); those lines are flagged VENDOR_FROM_BRAND")

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "replenishment.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    po_lines.sort(key=lambda r: (r["vendor"], r["sku"]))
    po_fields = ["vendor", "sku", "product", "qty", "case_pack", "unit_cost", "line_cost", "days_of_supply_now",
                 "flags"]
    with open(os.path.join(a.out_dir, "po_draft.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=po_fields)
        w.writeheader()
        w.writerows(po_lines)

    by_vendor = defaultdict(lambda: {"lines": 0, "units": 0, "cost": 0.0, "lines_missing_cost": 0})
    for p in po_lines:
        v = by_vendor[p["vendor"]]
        v["lines"] += 1
        v["units"] += p["qty"]
        if p["line_cost"] == "":
            v["lines_missing_cost"] += 1
        else:
            v["cost"] += p["line_cost"]
    for v in by_vendor.values():
        v["cost"] = round(v["cost"], 2)

    def count(flag):
        return sum(1 for r in out if any(f.split("(")[0] == flag for f in r["flags"].split(";")))

    inv_value_dead = round(sum((r["on_hand"] or 0) * (onhand[r["sku"]]["unit_cost"] or 0)
                               for r in out if "DEAD" in r["flags"] and r["sku"] in onhand), 2)
    summary = {
        "sales_file": a.sales, "onhand_file": a.onhand,
        "sales_mapping": sm_raw, "onhand_mapping": om_raw,
        "window": {"start": str(start), "end": str(as_of), "days": window},
        "parameters": {"safety_days": safety, "cover_days": cover, "dead_days": dead_days, "slow_dos": slow_dos,
                       "default_lead_time": a.default_lead_time},
        "assumptions": assumptions,
        "skus": len(out),
        "flag_counts": {k: count(k) for k in ("REORDER", "STOCKOUT", "DEAD", "SLOW", "NEW_SKU", "NO_LEAD_TIME",
                                              "NO_ONHAND_RECORD", "RETURNS_IN_WINDOW", "DEFAULT_LEAD_TIME",
                                              "BAD_LEAD_TIME", "NO_VENDOR", "VENDOR_FROM_BRAND", "CONFLICTING_ROWS",
                                              "BAD_OPEN_PO", "BAD_CASE_PACK", "BAD_UNIT_COST", "BAD_ONHAND_ROW")},
        "po_draft_by_vendor": dict(sorted(by_vendor.items())),
        "po_draft_total_cost": round(sum(v["cost"] for v in by_vendor.values()), 2),
        "dead_stock_cost_value": inv_value_dead,
        "skus_missing_lead_time": missing_lead,
        "skus_using_default_lead_time": default_lead,
        "skus_held_for_review": held,
        "lines_needing_vendor": needs_vendor,
        "lines_needing_vendor_cost": round(sum(x["line_cost"] or 0 for x in needs_vendor), 2),
        "input_problems": problems,
        "note": "PO lines are a DRAFT for buyer review. Nothing has been sent to any vendor. Lines in "
                "lines_needing_vendor are suggested quantities with no vendor; they are not in the PO total.",
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
