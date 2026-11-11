#!/usr/bin/env python3
"""Compute sell-through, days of supply, reorder points, and a draft PO by vendor.

Standard library only. Deterministic: the same inputs and flags always give the same output.

Usage:
  python3 replenish.py --sales SALES.csv --onhand ONHAND.csv --as-of YYYY-MM-DD [--out-dir DIR]
                       [--map-sales field=Column ...] [--map-onhand field=Column ...]
                       [--window-days 28]
                       [--default-lead-time DAYS] [--safety-days N] [--cover-days N]
                       [--dead-days N] [--slow-dos N] [--vendor-from-brand] [--detect-only]

  --as-of              REQUIRED. The date of the on-hand count; the sales window ends on this date.
                       If the last sale in the file is more than 1 day earlier, summary.json "warnings"
                       says so; sales dated after it are left out and counted in "warnings".
  --detect-only        print detected column mappings and data date range, then exit. A missing or
                       AMBIGUOUS required column is listed under "missing_required_columns" instead of
                       stopping the script, so both files' mappings can be confirmed in one step.
  --default-lead-time  used ONLY for SKUs whose lead time cell is truly blank; those SKUs are
                       flagged DEFAULT_LEAD_TIME(Nd). "7 days" / "2 weeks" are parsed; anything else
                       unreadable, or over 365 days, is flagged BAD_LEAD_TIME and not ordered.
  --vendor-from-brand  the operator confirmed brand = vendor: a blank vendor is filled from brand and
                       flagged VENDOR_FROM_BRAND. Without it a blank vendor is flagged NO_VENDOR and the
                       line is kept off the vendor PO draft (listed under lines_needing_vendor).

Data rules (nothing is dropped, merged or invented silently):
  - Duplicate on-hand rows for one SKU: on-hand and open PO are summed. Unit cost, case pack, lead
    time and vendor must agree (or be blank on all but one row); if they conflict the SKU is flagged
    CONFLICTING_ROWS, no order is suggested, and both values go in input_problems.
  - Numbers are parsed strictly (see to_number): NaN, inf and decimal commas ("4,25", "1.234,56") are
    reported with row, column and raw value, never guessed. An unreadable sales units cell drops that
    sales row; an unreadable on-hand cell is handled like any non-numeric on-hand value.
  - Negative sales units are returns (RETURNS_IN_WINDOW). If a SKU's net units in the window are
    negative, velocity is set to 0 and the SKU is flagged NEGATIVE_NET_SALES.
  - Negative on-hand (NEGATIVE_ONHAND) or negative open PO (BAD_OPEN_PO) holds the SKU: no order.
  - Non-numeric open PO (BAD_OPEN_PO) holds the SKU; a case pack that is not a whole number above 0
    (BAD_CASE_PACK) leaves the quantity unrounded; non-numeric unit cost (BAD_UNIT_COST) leaves cost
    blank. One unreadable cell among duplicate rows is never outvoted by a readable one. All are reported.
  - A blank open PO cell, or no open PO column, counts as 0 and is listed in "assumptions".
  - Minimum order qty (MOQ) is not a case pack: a quantity below it is flagged BELOW_MOQ, not raised.
  - An account/store column with more than one value stops the run: plan one account per run.
  - A first sale inside the window is NEW_SKU (velocity over days since that sale) only when the export
    reaches back before the window; otherwise NEW_OR_SLOW, measured over the whole window. No sale in an
    export shorter than --dead-days is NO_SALES_SEEN, not DEAD.
  - SKUs are matched ignoring case and repeated spaces ("e-case" in sales = "E-CASE " on hand). The
    outputs show the on-hand spelling; a SKU written more than one way is flagged SKU_VARIANTS and
    every spelling is listed in input_problems.
  - Rows with a blank SKU are listed in input_problems. If no row has a SKU, or the on-hand file has no
    data rows, the outputs are still written and summary.json "warnings" says so.
  - Text cells written to the CSVs that start with = + - @ get a leading apostrophe (csv_safe), so a
    spreadsheet never runs them as formulas.

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

# A column naming the retail account or store. One run plans one account: summing two stores' sales and
# stock under one SKU lets one store's surplus hide the other's stockout, so more than one value stops the run.
ACCOUNT_ALIASES = ["account", "account name", "retail account", "retailer", "store", "store name", "dispensary",
                   "dispensary name", "shop"]
# Longest lead time accepted from a cell or --default-lead-time. Not a planning target: anything longer is far
# more likely a typo or a pasted ID than a vendor lead time, so it is reported instead of ordered against.
MAX_LEAD_DAYS = 365
SALES_ALIASES = {
    "date": ["date", "sale date", "order date", "transaction date", "sold date", "invoice date", "completed date"],
    "sku": ["sku", "product code", "item code", "product id", "sku id"],
    "product": ["product", "product name", "item", "item name", "sku name"],
    "brand": ["brand", "brand name", "vendor", "manufacturer", "supplier"],
    "category": ["category", "product category", "item category", "type"],
    "units": ["units", "qty", "quantity", "units sold", "qty sold", "quantity sold"],
    "revenue": ["revenue", "net sales", "sales", "total", "net revenue", "gross sales", "line total", "amount"],
    "account": ACCOUNT_ALIASES,
}
ONHAND_ALIASES = {
    "sku": ["sku", "product code", "item code", "product id", "sku id"],
    "product": ["product", "product name", "item", "item name", "sku name"],
    "brand": ["brand", "brand name", "manufacturer"],
    "vendor": ["vendor", "supplier", "distributor", "vendor name"],
    "on_hand": ["on hand", "on_hand", "onhand", "qty on hand", "quantity on hand", "available", "current quantity",
                "inventory", "available qty"],
    "unit_cost": ["unit cost", "cost", "cost per unit", "wholesale cost", "cogs/unit"],
    "case_pack": ["case pack", "case size", "pack size", "order multiple"],
    "min_order_qty": ["moq", "min order qty", "minimum order qty", "minimum order quantity", "min order"],
    "lead_time_days": ["lead time", "lead time days", "lead_time_days", "lead days"],
    "open_po_qty": ["open po", "open po qty", "on order", "incoming", "qty on order"],
    "account": ACCOUNT_ALIASES,
}
REPL_FIELDS = ["sku", "product", "brand", "category", "vendor", "units_sold_window", "days_measured", "units_per_day",
               "revenue_window", "on_hand", "open_po_qty", "sell_through_pct", "days_of_supply", "lead_time_days",
               "reorder_point", "suggested_order_qty", "case_pack", "unit_cost", "order_cost", "last_sale", "flags"]
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


def load(path, aliases, overrides, required, label, strict=True):
    """Read a CSV and detect its columns. strict=False (--detect-only) reports a missing required
    column in the returned "missing" list instead of exiting, so the whole mapping can be shown."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = list(reader.fieldnames or [])
    except OSError as e:
        sys.exit(f"[{label}] Cannot read {path}: {e.strerror or e}.")
    except (UnicodeDecodeError, csv.Error) as e:
        sys.exit(f"[{label}] Cannot read {path} as a UTF-8 CSV ({e}). Export it as CSV (UTF-8) and rerun.")
    if not headers:
        sys.exit(f"[{label}] {path} is empty (no header row). Export it again with its column headers.")
    m = detect(headers, aliases, overrides)
    missing = []
    for req in required:
        if req not in m or m[req].startswith("AMBIGUOUS:"):
            if strict:
                sys.exit(f"[{label}] Cannot identify '{req}' column (found: {m.get(req, 'none')}). "
                         f"Headers: {headers}. Pass --map-{label} {req}=<Column>.")
            missing.append(f"{req} (found: {m.get(req, 'none')}); pass --map-{label} {req}=<Column>")
    # drop ambiguous optional fields so they are not silently used
    clean = {k: v for k, v in m.items() if not v.startswith("AMBIGUOUS:")}
    return rows, m, clean, missing


def sku_key(s):
    """Matching key for a SKU: case and repeated inner spaces are ignored ("e-case" = "E-CASE ").
    The SKU as written is still what the outputs show."""
    return " ".join(s.split()).casefold()


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


def cli_number(minimum, whole=False):
    """argparse type for numeric flags: finite, at least `minimum` ("pos" means greater than 0)."""
    def parse(s):
        v, prob = to_number(s)
        if prob or v is None:
            raise argparse.ArgumentTypeError(prob or "blank value")
        if whole and not v.is_integer():
            raise argparse.ArgumentTypeError(f"must be a whole number of days (got '{s}')")
        if (minimum == "pos" and v <= 0) or (minimum != "pos" and v < minimum):
            raise argparse.ArgumentTypeError(
                f"must be greater than 0 (got '{s}')" if minimum == "pos" else f"must not be negative (got '{s}')")
        return int(v) if whole else v
    return parse


def lead_flag(s):
    """argparse type for --default-lead-time: days greater than 0 and at most MAX_LEAD_DAYS."""
    v = cli_number("pos")(s)
    if v > MAX_LEAD_DAYS:
        raise argparse.ArgumentTypeError(f"must be at most {MAX_LEAD_DAYS} days (got '{s}')")
    return v


AS_OF_HELP = "The date of the on-hand count (YYYY-MM-DD). The sales window ends on this date."


class Parser(argparse.ArgumentParser):
    def error(self, message):
        if "--as-of" in message:
            message += ". " + AS_OF_HELP
        super().error(message)


def parse_lead(s):
    """Lead time in days. Accepts 7, 7d, 7 days, 2 wk, 2 weeks.

    Returns (days, problem): (None, None) if blank; (None, reason) if unreadable or outside
    0..MAX_LEAD_DAYS. The number goes through to_number, so its limits apply here too.
    """
    s = (s or "").strip().lower()
    if s == "":
        return None, None
    mt = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(d|day|days|w|wk|wks|week|weeks)?\.?", s)
    if not mt:
        return None, "not days or weeks"
    n, prob = to_number(mt.group(1))
    if prob:
        return None, prob
    days = n * 7 if (mt.group(2) or "").startswith("w") else n
    if days > MAX_LEAD_DAYS:
        return None, f"{days:g} days is over {MAX_LEAD_DAYS} days"
    return days, None


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


def accounts(rows, m):
    """Distinct non-blank values of the account/store column, if the file has one."""
    return sorted({get(r, m, "account") for r in rows} - {""}) if "account" in m else []


_SLASH_DATE = re.compile(r"^(\d{1,2})/(\d{1,2})/")


def us_ambiguous_dates(values):
    """Slash dates that would be a different date read as day/month (e.g. 03/09/2026)."""
    out = []
    for v in values:
        mt = _SLASH_DATE.match(v)
        if mt and mt.group(1) != mt.group(2) and int(mt.group(1)) <= 12 and int(mt.group(2)) <= 12:
            out.append(v)
    return out


def main():
    ap = Parser()
    ap.add_argument("--sales", required=True)
    ap.add_argument("--onhand", required=True)
    ap.add_argument("--out-dir", default="replen_out")
    ap.add_argument("--map-sales", nargs="*")
    ap.add_argument("--map-onhand", nargs="*")
    ap.add_argument("--window-days", type=cli_number("pos", whole=True), default=None)
    ap.add_argument("--as-of", required=True, metavar="YYYY-MM-DD", help=AS_OF_HELP)
    ap.add_argument("--default-lead-time", type=lead_flag, default=None)
    ap.add_argument("--safety-days", type=cli_number(0), default=None)
    ap.add_argument("--cover-days", type=cli_number(0), default=None,
                    help="Days of demand to cover after the order arrives (order-up-to horizon)")
    ap.add_argument("--dead-days", type=cli_number("pos", whole=True), default=None)
    ap.add_argument("--slow-dos", type=cli_number("pos"), default=None,
                    help="Flag SLOW when days of supply exceed this")
    ap.add_argument("--vendor-from-brand", action="store_true",
                    help="Operator confirmed brand = vendor: fill blank vendor from brand (flagged VENDOR_FROM_BRAND)")
    ap.add_argument("--detect-only", action="store_true")
    a = ap.parse_args()

    strict = not a.detect_only
    srows, sm_raw, sm, s_missing = load(a.sales, SALES_ALIASES, parse_overrides(a.map_sales), REQUIRED_SALES,
                                        "sales", strict)
    orows, om_raw, om, o_missing = load(a.onhand, ONHAND_ALIASES, parse_overrides(a.map_onhand), REQUIRED_ONHAND,
                                        "onhand", strict)

    problems = []
    dates = []
    for i, r in enumerate(srows, start=2):
        d = parse_date(get(r, sm, "date"))
        if d is None:
            problems.append(f"sales row {i}: unparseable date '{get(r, sm, 'date')}'")
        else:
            dates.append(d)

    early_warnings = []
    ambiguous = us_ambiguous_dates(get(r, sm, "date") for r in srows)
    if ambiguous:
        early_warnings.append(f"{len(ambiguous)} sales date(s) such as '{ambiguous[0]}' were read as month/day (US). "
                              f"Confirm the export uses US dates; if it is day/month, the dates are wrong.")
    s_acc, o_acc = accounts(srows, sm), accounts(orows, om)
    account_problem = None
    if len(s_acc) > 1 or len(o_acc) > 1 or (s_acc and o_acc and s_acc != o_acc):
        account_problem = (f"The files cover more than one account or store (sales: {s_acc or 'no column'}; "
                           f"on-hand: {o_acc or 'no column'}). Each account's sales and stock must be planned "
                           f"separately: filter both exports to one account and run once per account.")

    if a.detect_only:
        print(json.dumps({"sales_mapping": sm_raw, "onhand_mapping": om_raw, "sales_rows": len(srows),
                          "onhand_rows": len(orows),
                          "sales_date_range": [str(min(dates)), str(max(dates))] if dates else None,
                          "missing_required_columns": {"sales": s_missing, "onhand": o_missing},
                          "accounts": {"sales": s_acc, "onhand": o_acc},
                          "warnings": early_warnings + ([account_problem] if account_problem else [])},
                         indent=2, allow_nan=False))
        return
    if account_problem:
        sys.exit(account_problem)
    if not dates:
        sys.exit(f"[sales] No sales rows with a readable date in {a.sales} ({len(srows)} data row(s)). "
                 f"Check the export has sales rows and a date column (pass --map-sales date=<Column>).")

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

    as_of = parse_date(a.as_of)
    if as_of is None:
        sys.exit(f"Bad --as-of '{a.as_of}'. {AS_OF_HELP}")
    start = as_of - timedelta(days=window - 1)
    recent_start = as_of - timedelta(days=6)
    warnings = early_warnings
    # What the export can show. A first sale inside the window only means "new" if the export reaches back
    # before the window and the SKU sold nothing there; otherwise it may be a slow seller (NEW_OR_SLOW).
    export_start = min((d for d in dates if d <= as_of), default=None)
    obs_start = max(start, export_start) if export_start else start
    covered_days = (as_of - export_start).days + 1 if export_start else 0
    has_history_before_window = export_start is not None and export_start < start
    if export_start and export_start > start:
        warnings.append(f"The sales export starts {export_start}, after the {window}-day window start ({start}). "
                        f"Velocity is measured over the {(as_of - obs_start).days + 1} days the export covers. "
                        f"Check the export covers the full window.")
    last_sale = max(dates)
    if (as_of - last_sale).days > 1:
        warnings.append(f"Last sale is {last_sale}, {(as_of - last_sale).days} days before the on-hand count date. "
                        f"Check the sales export covers the full period.")
    after = sum(1 for d in dates if d > as_of)
    if after:
        warnings.append(f"{after} sales row(s) are dated after the on-hand count date ({as_of}) and were left out. "
                        f"Check the --as-of date and the on-hand count date match.")
    for w in warnings:
        print("WARNING: " + w, file=sys.stderr)

    sales = defaultdict(lambda: {"units": 0.0, "units_recent7": 0.0, "revenue": 0.0, "first": None, "last": None,
                                 "first_in_window": None, "product": "", "brand": "", "category": "", "neg": 0.0})
    written = defaultdict(dict)  # sku_key -> {SKU as written: [where]}, to report case/spacing variants
    for i, r in enumerate(srows, start=2):
        d = parse_date(get(r, sm, "date"))
        sku = get(r, sm, "sku")
        u, u_prob = to_number(get(r, sm, "units"))
        if d is None:
            continue
        if not sku:
            problems.append(f"sales row {i}: blank sku")
            continue
        if u is None:
            problems.append(f"sales row {i} ({sku}): column '{sm['units']}' value '{get(r, sm, 'units')}': "
                            f"{u_prob or 'blank units'}; row left out")
            continue
        written[sku_key(sku)].setdefault(sku, []).append(("sales", i))
        s = sales[sku_key(sku)]
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
            rev, rev_prob = to_number(get(r, sm, "revenue"))
            if rev_prob:
                problems.append(f"sales row {i} ({sku}): column '{sm['revenue']}' value '{get(r, sm, 'revenue')}': "
                                f"{rev_prob}; left out of revenue_window")
            elif rev is not None:
                s["revenue"] += rev
            if d >= recent_start:
                s["units_recent7"] += u

    # ---- on-hand: group rows by SKU so duplicates are combined openly, never by keeping the first row
    by_sku = defaultdict(list)
    onhand_written = defaultdict(dict)
    for i, r in enumerate(orows, start=2):
        sku = get(r, om, "sku")
        if not sku:
            problems.append(f"onhand row {i}: blank sku")
            continue
        by_sku[sku_key(sku)].append((i, r))
        onhand_written[sku_key(sku)].setdefault(sku, []).append(("onhand", i))
    # The SKU shown in the outputs is the on-hand file's spelling (first row), else the sales file's.
    display = {k: next(iter(v)) for k, v in written.items()}
    display.update({k: next(iter(v)) for k, v in onhand_written.items()})
    variants = set()
    for k in sorted(set(written) | set(onhand_written), key=lambda k: (display[k], k)):
        forms = {}
        for src in (onhand_written.get(k, {}), written.get(k, {})):
            for form, where in src.items():
                forms.setdefault(form, []).extend(where)
        if len(forms) > 1:
            variants.add(k)

            def places(where):
                txt = []
                for file in ("onhand", "sales"):
                    rws = [str(i) for f, i in where if f == file]
                    if rws:
                        more = f" and {len(rws) - 5} more" if len(rws) > 5 else ""
                        txt.append(f"{file} row{'s' if len(rws) > 1 else ''} {', '.join(rws[:5])}{more}")
                return "; ".join(txt)
            problems.append(f"SKU '{display[k]}' is written more than one way: "
                            + ", ".join(f"'{form}' ({places(where)})" for form, where in forms.items())
                            + ". Matched as one SKU (case and spacing ignored), flagged SKU_VARIANTS. "
                              "Fix the exports so the SKU is written the same way everywhere.")
    onhand = {}
    unreadable_onhand = set()
    blank_open_po = []

    def nonneg_number(raw):
        v, prob = to_number(raw)
        if v is not None and v < 0:
            return None, "negative value"
        return v, prob

    def lead(raw):
        return parse_lead(raw)

    def whole_pack(raw):
        """Case pack / MOQ: a whole number of units, greater than 0."""
        v, prob = nonneg_number(raw)
        if prob or v is None:
            return v, prob
        if v <= 0 or not v.is_integer():
            return None, "not a whole number of units greater than 0"
        return v, None

    ATTRS = (("unit_cost", "unit cost", nonneg_number), ("case_pack", "case pack", whole_pack),
             ("min_order_qty", "minimum order qty", whole_pack), ("lead_time_days", "lead time", lead),
             ("vendor", "vendor", None))
    for key, rws in by_sku.items():
        sku = display[key]
        rec = {"rows": [i for i, _ in rws], "on_hand": 0.0, "open_po": 0.0, "flags": [], "hold": False,
               "product": next((get(r, om, "product") for _, r in rws if get(r, om, "product")), ""),
               "brand": next((get(r, om, "brand") for _, r in rws if get(r, om, "brand")), ""),
               "lead_status": "blank", "neg_onhand": False}
        good_rows = 0
        for i, r in rws:
            q, q_prob = to_number(get(r, om, "on_hand"))
            if q is None:
                problems.append(f"onhand row {i} ({sku}): column '{om['on_hand']}' value '{get(r, om, 'on_hand')}': "
                                f"{q_prob or 'blank on-hand'}")
                if len(rws) > 1:
                    rec["flags"].append(f"BAD_ONHAND_ROW(row {i})")
                    rec["hold"] = True
                continue
            good_rows += 1
            rec["on_hand"] += q
            if q < 0:
                problems.append(f"onhand row {i} ({sku}): column '{om['on_hand']}' value '{get(r, om, 'on_hand')}': "
                                f"negative on-hand; no order suggested until the count is corrected")
                rec["flags"].append("NEGATIVE_ONHAND")
                rec["hold"] = rec["neg_onhand"] = True
            po, po_prob = to_number(get(r, om, "open_po_qty"))
            if po is not None and po < 0:
                po, po_prob = None, "negative open PO"
            if po_prob:
                problems.append(f"onhand row {i} ({sku}): column '{om['open_po_qty']}' value "
                                f"'{get(r, om, 'open_po_qty')}': {po_prob}; no order suggested until the open PO "
                                f"is confirmed")
                rec["flags"].append("BAD_OPEN_PO")
                rec["hold"] = True
            elif po is not None:
                rec["open_po"] += po
            elif "open_po_qty" in om and sku not in blank_open_po:
                blank_open_po.append(sku)
        if good_rows == 0:
            unreadable_onhand.add(key)  # still listed, as NO_ONHAND_RECORD; the cells are in input_problems
            continue
        if len(rws) > 1:
            problems.append(f"onhand: SKU {sku} is on rows {', '.join(map(str, rec['rows']))}; on-hand "
                            f"({rec['on_hand']:g}) and open PO ({rec['open_po']:g}) are the sums of those rows")
        for field, label, parse in ATTRS:
            vals = []  # (row, raw text, parsed)
            bad = False  # an unreadable cell is never silently outvoted by a readable one on another row
            for i, r in rws:
                raw = get(r, om, field)
                if raw == "":
                    continue
                v, prob = parse(raw) if parse else (raw, None)
                if prob:
                    tag = {"unit_cost": "BAD_UNIT_COST", "case_pack": "BAD_CASE_PACK", "min_order_qty": "BAD_MOQ",
                           "lead_time_days": "BAD_LEAD_TIME"}[field]
                    if tag not in rec["flags"]:
                        rec["flags"].append(tag)
                    effect = {"unit_cost": "order cost left blank",
                              "case_pack": "suggested quantity is NOT rounded to a case pack",
                              "min_order_qty": "the minimum order is not checked",
                              "lead_time_days": "no default used and no order suggested until a lead time in days "
                                                "is given"}[field]
                    problems.append(f"onhand row {i} ({sku}): column '{om[field]}' value '{raw}' is not readable "
                                    f"({prob}); {effect}")
                    bad = True
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
            elif bad:
                rec[field] = None
                if field == "lead_time_days":
                    rec["lead_status"] = "bad"
            else:
                rec[field] = vals[0][2] if vals else None
                if field == "lead_time_days" and vals:
                    rec["lead_status"] = "ok"
        rec["vendor"] = rec["vendor"] or ""
        onhand[key] = rec

    vendor_brand_used = False
    out, po_lines, needs_vendor = [], [], []
    missing_lead, default_lead, held = [], [], []
    out_keys = []
    if "open_po_qty" not in om:
        assumptions.append("open PO = 0 for every SKU: the on-hand file has no open PO column (not "
                           "operator-provided; confirm nothing is already on order)")
    elif blank_open_po:
        assumptions.append(f"open PO = 0 where the open PO cell is blank ({len(blank_open_po)} SKU(s): "
                           f"{', '.join(blank_open_po[:10])}{' and more' if len(blank_open_po) > 10 else ''}); "
                           f"confirm a blank means nothing on order")
    for key in sorted(set(sales) | set(onhand) | unreadable_onhand, key=lambda k: (display[k], k)):
        sku = display[key]
        s = sales.get(key)
        o = onhand.get(key)
        flags = ["SKU_VARIANTS"] if key in variants else []
        units = s["units"] if s else 0.0
        days = (as_of - obs_start).days + 1
        if s and s["first"] is not None and s["first"] > obs_start:
            if has_history_before_window:
                days = (as_of - s["first"]).days + 1
                flags.append(f"NEW_SKU({days}d of history)")
            else:  # the export starts inside the window: a late first sale may just be a slow seller
                flags.append(f"NEW_OR_SLOW(first sale {s['first']})")
        rate = units / days if days > 0 else 0.0
        if units < 0:  # returns exceed sales in the window: never a negative velocity
            rate = 0.0
            flags.append(f"NEGATIVE_NET_SALES({units:g})")
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
            if o["neg_onhand"]:
                pass  # negative on-hand: sell-through and days of supply would be meaningless
            else:
                if denom > 0 and units >= 0:
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
            no_sale_seen = not s or s["last"] is None
            if oh > 0 and no_sale_seen and covered_days < dead_days:
                flags.append(f"NO_SALES_SEEN(export covers {covered_days}d)")  # too short to call it dead
            elif oh > 0 and (no_sale_seen or (as_of - s["last"]).days >= dead_days):
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
                    if cp:  # whole number > 0 (whole_pack)
                        qty = -(-qty // int(cp)) * int(cp)
                        row["case_pack"] = cp
                    moq = o["min_order_qty"]
                    if moq and 0 < qty < moq:  # not raised: buying up to the minimum is the buyer's call
                        flags.append(f"BELOW_MOQ({moq:g})")
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
        out_keys.append(key)
    if vendor_brand_used:
        assumptions.append("vendor filled from brand where the vendor cell was blank (--vendor-from-brand, "
                           "operator said brand = vendor); those lines are flagged VENDOR_FROM_BRAND")

    late_warnings = []
    if not orows:
        late_warnings.append(f"The on-hand file {a.onhand} has no data rows, so every SKU shows NO_ONHAND_RECORD "
                             f"and nothing is ordered. Check the on-hand export.")
    if not out:
        late_warnings.append("No SKUs to plan: no sales or on-hand row has a SKU (see input_problems). "
                             "Check the SKU column (pass --map-sales / --map-onhand sku=<Column>).")
    for w in late_warnings:
        print("WARNING: " + w, file=sys.stderr)
    warnings.extend(late_warnings)

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "replenishment.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REPL_FIELDS)
        w.writeheader()
        w.writerows([{k: csv_safe(v) for k, v in x.items()} for x in out])
    po_lines.sort(key=lambda r: (r["vendor"], r["sku"]))
    po_fields = ["vendor", "sku", "product", "qty", "case_pack", "unit_cost", "line_cost", "days_of_supply_now",
                 "flags"]
    with open(os.path.join(a.out_dir, "po_draft.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=po_fields)
        w.writeheader()
        w.writerows([{k: csv_safe(v) for k, v in x.items()} for x in po_lines])

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

    dead = [(r, onhand[k]) for r, k in zip(out, out_keys) if "DEAD" in r["flags"] and k in onhand]
    inv_value_dead = round(sum(r["on_hand"] * o["unit_cost"] for r, o in dead if o["unit_cost"] is not None), 2)
    dead_missing_cost = [{"sku": r["sku"], "on_hand": r["on_hand"]} for r, o in dead if o["unit_cost"] is None]
    summary = {
        "warnings": warnings,
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
                                              "BAD_OPEN_PO", "BAD_CASE_PACK", "BAD_UNIT_COST", "BAD_ONHAND_ROW",
                                              "NEGATIVE_ONHAND", "NEGATIVE_NET_SALES", "SKU_VARIANTS",
                                              "NEW_OR_SLOW", "NO_SALES_SEEN", "BAD_MOQ", "BELOW_MOQ")},
        "po_draft_by_vendor": dict(sorted(by_vendor.items())),
        "po_draft_total_cost": round(sum(v["cost"] for v in by_vendor.values()), 2),
        "dead_stock_cost_value": inv_value_dead,
        "dead_stock_missing_cost": dead_missing_cost,
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
        json.dump(summary, f, indent=2, allow_nan=False)
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
