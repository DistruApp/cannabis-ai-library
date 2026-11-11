"""Gate 2 script tests for cannabis-replenishment-planner/scripts/replenish.py.

Run: python3 -m unittest discover -s tests -t . -v
"""
import csv
import json
import re
import shlex
import unittest

from tests import helpers as h

NAME = "replenish"
FILES = h.skill_dir(NAME) / "evals" / "files"
POS = FILES / "pos_sales_2026-08-02_to_2026-09-30.csv"
ONHAND = FILES / "onhand_2026-09-30.csv"
NO_SKU_SALES = FILES / "sales_by_product_no_sku.csv"
MESSY_ONHAND = FILES / "onhand_messy.csv"
REG_SALES = FILES / "sales_regression_2026-09-03_to_2026-09-30.csv"
REG_ONHAND = FILES / "onhand_regression_rows.csv"
BAD_SALES = FILES / "sales_regression_bad_numbers_2026-09-03_to_2026-09-30.csv"
BAD_ONHAND = FILES / "onhand_regression_bad_numbers.csv"
OUTPUTS = ("replenishment.csv", "po_draft.csv", "summary.json")
REPL_FIELDS = ["sku", "product", "brand", "category", "vendor", "units_sold_window", "days_measured", "units_per_day",
               "revenue_window", "on_hand", "open_po_qty", "sell_through_pct", "days_of_supply", "lead_time_days",
               "reorder_point", "suggested_order_qty", "case_pack", "unit_cost", "order_cost", "last_sale", "flags"]
AS_OF_MESSAGE = ("the following arguments are required: --as-of. The date of the on-hand count (YYYY-MM-DD). "
                 "The sales window ends on this date.")
EVAL1_PARAMS = ["--as-of", "2026-09-30", "--safety-days", "3"]
BD_PO_COST = 1680.0  # SP-BD-35's line on the eval 1 PO (120 units at $14)

CSV_SAFE_TEXT = '''_FORMULA_START = ("=", "+", "-", "@", "\\t", "\\r")


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
'''


def read_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def last_row_index(path, sku):
    """0-based data-row index of the last sales row for sku."""
    _, rows = read_rows(path)
    return max(i for i, r in enumerate(rows) if r[1] == sku)


class ReplenishCase(unittest.TestCase):
    """Every run goes through run_repl(): stderr must never hold a traceback."""

    def run_repl(self, args):
        res = h.run(NAME, args)
        self.assertNotIn("Traceback", res.stderr, res.stderr)
        return res

    def run_ok(self, sales, onhand, out_dir, *params):
        res = self.run_repl(["--sales", sales, "--onhand", onhand, "--out-dir", out_dir] + list(params))
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        out = h.strict_json_load(res.stdout, is_text=True)
        self.assertEqual(h.strict_json_load(out_dir / "summary.json"), out)
        skus = {r["sku"]: r for r in h.read_csv(out_dir / "replenishment.csv")}
        po = {r["sku"]: r for r in h.read_csv(out_dir / "po_draft.csv")}
        return out, skus, po, res

    def eval1(self, out_dir, sales=POS, onhand=ONHAND):
        return self.run_ok(sales, onhand, out_dir, *EVAL1_PARAMS)

    def assert_problem(self, out, *parts):
        self.assertTrue(any(all(p in prob for p in parts) for prob in out["input_problems"]),
                        f"no input_problem with {parts}: {out['input_problems']}")


class KnownAnswers(ReplenishCase):
    def test_every_eval_with_files_is_covered(self):
        evals = json.loads((h.skill_dir(NAME) / "evals" / "evals.json").read_text())["evals"]
        self.assertEqual({e["id"] for e in evals if e["files"]}, {1, 2, 3, 4, 5, 6})

    def test_eval1_weekly_reorder_po_total(self):
        with h.TempDir() as d:
            out, skus, po, _ = self.eval1(d)
            self.assertEqual(out["po_draft_total_cost"], 4620.0)
            self.assertEqual(out["po_draft_by_vendor"], {
                "Example Coast Extracts": {"lines": 1, "units": 110, "cost": 1980.0, "lines_missing_cost": 0},
                "Example North Farms": {"lines": 1, "units": 40, "cost": 960.0, "lines_missing_cost": 0},
                "Example Pines Distribution": {"lines": 1, "units": 120, "cost": 1680.0, "lines_missing_cost": 0}})
            self.assertEqual(out["window"], {"start": "2026-09-03", "end": "2026-09-30", "days": 28})
            self.assertEqual(out["warnings"], [])
            self.assertEqual(out["assumptions"], [
                "window_days = 28 days (script default, not operator-provided)",
                "cover_days = 14.0 days (script default, not operator-provided)",
                "dead_days = 30 days (script default, not operator-provided)",
                "slow_dos = 90.0 days of supply (script default, not operator-provided)"])
            self.assertEqual(out["input_problems"], [])

    def test_eval1_weekly_reorder_flags(self):
        with h.TempDir() as d:
            out, skus, po, _ = self.eval1(d)
            self.assertEqual(sorted(po), ["CE-LR-GEL", "NB-SM-14", "SP-BD-35"])
            self.assertEqual(skus["CE-LR-GEL"]["flags"], "STOCKOUT(demand understated);REORDER")
            self.assertEqual(skus["CE-LR-GEL"]["suggested_order_qty"], "110")
            self.assertEqual(skus["NB-PR-5PK"]["flags"], "DEAD(no sales 30d+)")
            self.assertEqual(out["dead_stock_cost_value"], 350.0)
            self.assertEqual(skus["GH-CHOC-100"]["flags"], "NO_VENDOR;NO_LEAD_TIME")
            self.assertEqual(out["skus_missing_lead_time"], ["GH-CHOC-100"])
            dist = skus["CE-DIST-1G"]
            self.assertEqual((dist["open_po_qty"], dist["suggested_order_qty"], dist["flags"]), ("50.0", "0", ""))
            self.assertEqual(skus["SP-BD-35"]["units_per_day"], "6.0")
            self.assertEqual(skus["NB-SM-14"]["flags"], "NEW_SKU(11d of history);REORDER")
            self.assertEqual(skus["GH-GUM-100"]["flags"], "RETURNS_IN_WINDOW(-2)")

    def test_eval2_promo_window_default_lead_time_and_no_vendor(self):
        with h.TempDir() as d:
            out, skus, po, _ = self.run_ok(POS, ONHAND, d, "--as-of", "2026-09-30", "--window-days", "35",
                                           "--default-lead-time", "7", "--safety-days", "0")
            self.assertEqual(out["po_draft_total_cost"], 3864.0)
            self.assertEqual(out["window"], {"start": "2026-08-27", "end": "2026-09-30", "days": 35})
            self.assertEqual({k: (v["qty"], v["line_cost"]) for k, v in po.items()},
                             {"CE-LR-GEL": ("100", "1800.0"), "NB-SM-14": ("30", "720.0"),
                              "SP-BD-35": ("96", "1344.0")})
            self.assertNotIn("GH-CHOC-100", po)
            self.assertEqual(out["lines_needing_vendor"], [{
                "vendor": "", "sku": "GH-CHOC-100", "product": "Chocolate Bar 100mg - Dark", "qty": 18,
                "case_pack": "", "unit_cost": 9.0, "line_cost": 162.0, "days_of_supply_now": 3.1,
                "flags": "NO_VENDOR;DEFAULT_LEAD_TIME(7d);REORDER"}])
            self.assertEqual(out["skus_using_default_lead_time"], ["GH-CHOC-100"])
            self.assertEqual(skus["NB-SM-14"]["flags"], "NEW_SKU(11d of history);REORDER")
            self.assertFalse(any(a.startswith("safety_days") for a in out["assumptions"]))

    def test_eval3_detect_only_reports_missing_sku_and_ambiguous_on_hand(self):
        res = self.run_repl(["--sales", NO_SKU_SALES, "--onhand", MESSY_ONHAND, "--as-of", "2026-09-30",
                             "--detect-only"])
        self.assertEqual(res.returncode, 0, res.stderr)
        out = h.strict_json_load(res.stdout, is_text=True)
        self.assertEqual(out["onhand_mapping"]["on_hand"], "AMBIGUOUS:On Hand|Available")
        self.assertEqual(out["missing_required_columns"], {
            "sales": ["sku (found: none); pass --map-sales sku=<Column>"],
            "onhand": ["sku (found: none); pass --map-onhand sku=<Column>",
                       "on_hand (found: AMBIGUOUS:On Hand|Available); pass --map-onhand on_hand=<Column>"]})
        self.assertEqual(out["sales_date_range"], ["2026-08-02", "2026-09-30"])

    def test_eval3_run_without_mapping_stops_and_mapped_run_orders_nothing_without_lead_times(self):
        with h.TempDir() as d:
            res = self.run_repl(["--sales", NO_SKU_SALES, "--onhand", MESSY_ONHAND, "--as-of", "2026-09-30",
                                 "--out-dir", d / "x"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("[sales] Cannot identify 'sku' column", res.stderr)
            out, skus, po, _ = self.run_ok(NO_SKU_SALES, MESSY_ONHAND, d / "out", "--as-of", "2026-09-30",
                                           "--map-sales", "sku=Product", "--map-onhand", "sku=Product",
                                           "on_hand=Available")
            self.assertEqual((out["po_draft_total_cost"], po), (0, {}))
            self.assertEqual(len(out["skus_missing_lead_time"]), 7)

    def test_eval4_duplicate_rows_lead_time_text_and_vendor(self):
        with h.TempDir() as d:
            out, skus, po, res = self.run_ok(REG_SALES, REG_ONHAND, d, "--as-of", "2026-09-30",
                                             "--default-lead-time", "7", "--safety-days", "2")
            self.assertEqual(out["po_draft_total_cost"], 1569.0)
            self.assertEqual({k: (v["vendor"], v["qty"], v["line_cost"]) for k, v in po.items()},
                             {"EX-C": ("Example Distro", "60", "360.0"),
                              "EX-E": ("Example Wellness Supply", "42", "840.0"),
                              "EX-H": ("Example Wellness Supply", "41", "369.0")})
            self.assertEqual(out["warnings"], ["Last sale is 2026-09-24, 6 days before the on-hand count date. "
                                               "Check the sales export covers the full period."])
            self.assertIn("WARNING: Last sale is 2026-09-24, 6 days", res.stderr)
            self.assertEqual((skus["EX-A"]["on_hand"], skus["EX-A"]["open_po_qty"], skus["EX-A"]["suggested_order_qty"]),
                             ("8.0", "100.0", "0"))
            self.assertEqual(skus["EX-B"]["flags"], "CONFLICTING_ROWS(unit cost)")
            self.assertEqual(skus["EX-D"]["flags"], "BAD_LEAD_TIME")
            self.assertEqual(skus["EX-E"]["flags"], "DEFAULT_LEAD_TIME(7d);REORDER")
            self.assertEqual(skus["EX-H"]["flags"], "BAD_CASE_PACK;REORDER")
            self.assertEqual(out["skus_held_for_review"], ["EX-B", "EX-G"])
            self.assertEqual([(x["sku"], x["qty"], x["line_cost"]) for x in out["lines_needing_vendor"]],
                             [("EX-F", 50, 700.0)])
            self.assert_problem(out, "onhand row 6 (EX-C): lead time '2 weeks' read as 14 days")

    def test_eval5_unreadable_and_negative_numbers(self):
        with h.TempDir() as d:
            out, skus, po, _ = self.run_ok(BAD_SALES, BAD_ONHAND, d, "--as-of", "2026-09-30", "--safety-days", "2")
            self.assertEqual(out["warnings"], [])
            self.assertEqual(out["po_draft_total_cost"], 240.0)
            self.assertEqual(out["po_draft_by_vendor"], {"Example Distro": {"lines": 2, "units": 80, "cost": 240.0,
                                                                            "lines_missing_cost": 1}})
            self.assertEqual({k: (v["qty"], v["line_cost"]) for k, v in po.items()},
                             {"EX-K": ("40", ""), "EX-L": ("40", "240.0")})
            self.assertEqual(out["skus_held_for_review"], ["EX-M", "EX-P"])
            self.assertEqual(skus["EX-N"]["units_per_day"], "0.0")
            self.assertIn("NEGATIVE_NET_SALES(-5)", skus["EX-N"]["flags"])
            self.assertEqual((skus["EX-Q"]["on_hand"], skus["EX-Q"]["flags"]), ("1200.0", "SLOW"))
            self.assertEqual(skus["EX-J"]["flags"], "NO_ONHAND_RECORD")
            for where, col, raw in (("sales row", "Units Sold", "NaN"), ("sales row", "Units Sold", "inf"),
                                    ("sales row", "Units Sold", "4,25"), ("sales row", "Net Sales", "1.234,56"),
                                    ("onhand row 2", "Available", "inf"), ("onhand row 3", "Unit Cost", "4,25"),
                                    ("onhand row 4", "Case Pack", "NaN"), ("onhand row 5", "On Order", "1.234,56"),
                                    ("onhand row 7", "Available", "-3")):
                with self.subTest(column=col, raw=raw):
                    self.assert_problem(out, where, f"column '{col}' value '{raw}'")

    def test_eval6_missing_as_of_exits_with_clear_message(self):
        with h.TempDir() as d:
            res = self.run_repl(["--sales", POS, "--onhand", ONHAND, "--safety-days", "3", "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 2)
            self.assertIn(AS_OF_MESSAGE, res.stderr)
            self.assertFalse((d / "out").exists())
            out, _, _, _ = self.eval1(d / "out2")
            self.assertEqual(out["po_draft_total_cost"], 4620.0)


class BadNumbers(ReplenishCase):
    """One bad cell on SP-BD-35 (on-hand row 2) in the eval 1 files; eval 1's PO is $4,620."""

    def onhand_case(self, column, check):
        for label, raw in h.BAD_NUMBERS.items():
            with self.subTest(column=column, value=label), h.TempDir() as d:
                onhand = h.mutate_csv(ONHAND, d / "onhand.csv", 0, column, raw)
                out, skus, po, _ = self.eval1(d / "out", onhand=onhand)
                self.assert_problem(out, "onhand row 2 (SP-BD-35)", f"column '{column}' value '{raw}'")
                check(label, out, skus, po)

    def test_on_hand_bad_numbers(self):
        def check(label, out, skus, po):
            self.assertNotIn("SP-BD-35", po)
            self.assertEqual(out["po_draft_total_cost"], 4620.0 - BD_PO_COST)
            if label == "negative":
                self.assertIn("NEGATIVE_ONHAND", skus["SP-BD-35"]["flags"])
                self.assertIn("SP-BD-35", out["skus_held_for_review"])
            else:
                self.assertIn("NO_ONHAND_RECORD", skus["SP-BD-35"]["flags"])
        self.onhand_case("Available", check)

    def test_open_po_bad_numbers(self):
        def check(label, out, skus, po):
            self.assertIn("BAD_OPEN_PO", skus["SP-BD-35"]["flags"])
            self.assertIn("SP-BD-35", out["skus_held_for_review"])
            self.assertNotIn("SP-BD-35", po)
            self.assertEqual(out["po_draft_total_cost"], 4620.0 - BD_PO_COST)
        self.onhand_case("On Order", check)

    def test_unit_cost_bad_numbers(self):
        def check(label, out, skus, po):
            self.assertIn("BAD_UNIT_COST", skus["SP-BD-35"]["flags"])
            self.assertEqual((po["SP-BD-35"]["qty"], po["SP-BD-35"]["line_cost"]), ("120", ""))
            self.assertEqual(out["po_draft_total_cost"], 4620.0 - BD_PO_COST)
            self.assertEqual(out["po_draft_by_vendor"]["Example Pines Distribution"]["lines_missing_cost"], 1)
        self.onhand_case("Unit Cost", check)

    def test_case_pack_bad_numbers(self):
        def check(label, out, skus, po):
            self.assertIn("BAD_CASE_PACK", skus["SP-BD-35"]["flags"])
            # 6/day x (7 lead + 3 safety + 14 cover) - 40 on hand = 104, not rounded up to 120
            self.assertEqual((po["SP-BD-35"]["qty"], po["SP-BD-35"]["case_pack"], po["SP-BD-35"]["line_cost"]),
                             ("104", "", "1456.0"))
            self.assertEqual(out["po_draft_total_cost"], 4620.0 - BD_PO_COST + 1456.0)
        self.onhand_case("Case Pack", check)

    def test_lead_time_bad_numbers(self):
        def check(label, out, skus, po):
            self.assertIn("BAD_LEAD_TIME", skus["SP-BD-35"]["flags"])
            self.assertNotIn("SP-BD-35", po)
            self.assertEqual(out["po_draft_total_cost"], 4620.0 - BD_PO_COST)
        self.onhand_case("Lead Time Days", check)

    def test_lead_time_bad_numbers_never_replaced_by_default(self):
        for label, raw in h.BAD_NUMBERS.items():
            with self.subTest(value=label), h.TempDir() as d:
                onhand = h.mutate_csv(ONHAND, d / "onhand.csv", 0, "Lead Time Days", raw)
                out, skus, po, _ = self.run_ok(POS, onhand, d / "out", *EVAL1_PARAMS, "--default-lead-time", "7")
                self.assertNotIn("SP-BD-35", po)
                self.assertNotIn("SP-BD-35", out["skus_using_default_lead_time"])

    def test_sales_units_bad_numbers(self):
        idx = last_row_index(POS, "SP-BD-35")
        for label, raw in h.BAD_NUMBERS.items():
            with self.subTest(value=label), h.TempDir() as d:
                sales = h.mutate_csv(POS, d / "sales.csv", idx, "Units Sold", raw)
                out, skus, po, _ = self.eval1(d / "out", sales=sales)
                bd = skus["SP-BD-35"]
                if label == "negative":  # a negative sale is a return: counted and flagged, not dropped
                    self.assertEqual(bd["units_sold_window"], str(168.0 - 6 - 10))
                    self.assertIn("RETURNS_IN_WINDOW(-10)", bd["flags"])
                else:
                    self.assert_problem(out, f"sales row {idx + 2} (SP-BD-35)", f"column 'Units Sold' value '{raw}'",
                                        "row left out")
                    self.assertEqual(bd["units_sold_window"], "162.0")

    def test_sales_revenue_bad_numbers(self):
        idx = last_row_index(POS, "SP-BD-35")
        for label, raw in h.BAD_NUMBERS.items():
            if label == "negative":  # a refund is a valid negative amount
                continue
            with self.subTest(value=label), h.TempDir() as d:
                sales = h.mutate_csv(POS, d / "sales.csv", idx, "Net Sales", raw)
                out, skus, po, _ = self.eval1(d / "out", sales=sales)
                self.assert_problem(out, f"sales row {idx + 2} (SP-BD-35)", f"column 'Net Sales' value '{raw}'",
                                    "left out of revenue_window")
                self.assertEqual(skus["SP-BD-35"]["revenue_window"], "5670.0")
                self.assertEqual(out["po_draft_total_cost"], 4620.0)

    def test_cli_numeric_flags_reject_bad_numbers(self):
        for flag in ("--window-days", "--default-lead-time", "--safety-days", "--cover-days", "--dead-days",
                     "--slow-dos"):
            for label, raw in h.BAD_NUMBERS.items():
                with self.subTest(flag=flag, value=label), h.TempDir() as d:
                    res = self.run_repl(["--sales", POS, "--onhand", ONHAND, "--as-of", "2026-09-30",
                                         f"{flag}={raw}", "--out-dir", d / "out"])
                    self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
                    self.assertIn(f"argument {flag}", res.stderr)
                    self.assertIn(raw, res.stderr)
                    self.assertFalse((d / "out").exists())

    def test_us_thousands_separator_is_read(self):
        with h.TempDir() as d:
            onhand = h.mutate_csv(ONHAND, d / "onhand.csv", 0, "Available", "1,040")
            out, skus, po, _ = self.eval1(d / "out", onhand=onhand)
            self.assertEqual(skus["SP-BD-35"]["on_hand"], "1040.0")
            self.assertEqual(out["input_problems"], [])


class Structure(ReplenishCase):
    def test_empty_files_exit_with_message(self):
        for which in ("sales", "onhand"):
            with self.subTest(file=which), h.TempDir() as d:
                (d / "empty.csv").write_text("")
                files = {"sales": POS, "onhand": ONHAND, which: d / "empty.csv"}
                res = self.run_repl(["--sales", files["sales"], "--onhand", files["onhand"],
                                     "--out-dir", d / "out"] + EVAL1_PARAMS)
                self.assertEqual(res.returncode, 1)
                self.assertIn(f"[{which}]", res.stderr)
                self.assertIn("empty", res.stderr)

    def test_missing_file_exits_with_message(self):
        with h.TempDir() as d:
            res = self.run_repl(["--sales", d / "nope.csv", "--onhand", ONHAND, "--out-dir", d / "out"]
                                + EVAL1_PARAMS)
            self.assertEqual(res.returncode, 1)
            self.assertIn("[sales] Cannot read", res.stderr)

    def test_header_only_sales_exits_with_message(self):
        with h.TempDir() as d:
            header, _ = read_rows(POS)
            h.write_csv(d / "sales.csv", header, [])
            res = self.run_repl(["--sales", d / "sales.csv", "--onhand", ONHAND, "--out-dir", d / "out"]
                                + EVAL1_PARAMS)
            self.assertEqual(res.returncode, 1)
            self.assertIn("[sales] No sales rows with a readable date", res.stderr)

    def test_header_only_onhand_orders_nothing_and_warns(self):
        with h.TempDir() as d:
            header, _ = read_rows(ONHAND)
            h.write_csv(d / "onhand.csv", header, [])
            out, skus, po, res = self.eval1(d / "out", onhand=d / "onhand.csv")
            self.assertEqual((po, out["po_draft_total_cost"]), ({}, 0))
            self.assertTrue(all("NO_ONHAND_RECORD" in r["flags"] for r in skus.values()))
            self.assertTrue(any("has no data rows" in w for w in out["warnings"]), out["warnings"])

    def test_duplicate_onhand_rows_are_summed_and_reported(self):
        with h.TempDir() as d:
            header, rows = read_rows(ONHAND)
            h.write_csv(d / "onhand.csv", header, rows + [rows[0]])
            out, skus, po, _ = self.eval1(d / "out", onhand=d / "onhand.csv")
            self.assertEqual(skus["SP-BD-35"]["on_hand"], "80.0")
            self.assertNotIn("SP-BD-35", po)  # 80 on hand is above the 60-unit reorder point
            self.assert_problem(out, "onhand: SKU SP-BD-35 is on rows 2, 10")

    def test_duplicate_sales_rows_are_counted(self):
        with h.TempDir() as d:
            header, rows = read_rows(POS)
            idx = last_row_index(POS, "SP-BD-35")
            h.write_csv(d / "sales.csv", header, rows + [rows[idx]])
            out, skus, po, _ = self.eval1(d / "out", sales=d / "sales.csv")
            self.assertEqual(skus["SP-BD-35"]["units_sold_window"], "174.0")

    def test_blank_required_cells(self):
        idx = last_row_index(POS, "SP-BD-35")
        cases = (("sales", POS, idx, "Date", f"sales row {idx + 2}: unparseable date ''"),
                 ("sales", POS, idx, "SKU", f"sales row {idx + 2}: blank sku"),
                 ("sales", POS, idx, "Units Sold", f"sales row {idx + 2} (SP-BD-35): column 'Units Sold' value '': "
                                                   f"blank units; row left out"),
                 ("onhand", ONHAND, 0, "SKU", "onhand row 2: blank sku"),
                 ("onhand", ONHAND, 0, "Available", "onhand row 2 (SP-BD-35): column 'Available' value '': "
                                                    "blank on-hand"))
        for which, src, row, column, problem in cases:
            with self.subTest(file=which, column=column), h.TempDir() as d:
                path = h.mutate_csv(src, d / f"{which}.csv", row, column, "")
                kw = {which: path}
                out, skus, po, _ = self.eval1(d / "out", **kw)
                self.assertIn(problem, out["input_problems"])

    def test_sku_case_and_whitespace_variants_match_one_sku(self):
        with h.TempDir() as d:
            header, rows = read_rows(POS)
            for r in rows:
                if r[1] == "SP-BD-35":
                    r[1] = "sp-bd-35 "
            h.write_csv(d / "sales.csv", header, rows)
            out, skus, po, _ = self.eval1(d / "out", sales=d / "sales.csv")
            self.assertEqual(out["skus"], 8)
            self.assertNotIn("sp-bd-35", skus)
            bd = skus["SP-BD-35"]
            self.assertEqual(bd["flags"], "SKU_VARIANTS;REORDER")
            self.assertNotIn("DEAD", bd["flags"])
            self.assertEqual(out["po_draft_total_cost"], 4620.0)
            self.assertEqual(out["flag_counts"]["SKU_VARIANTS"], 1)
            self.assertEqual(out["flag_counts"]["NO_ONHAND_RECORD"], 0)
            self.assert_problem(out, "SKU 'SP-BD-35' is written more than one way", "'SP-BD-35' (onhand row 2)",
                                "'sp-bd-35' (sales rows 2, 9, 15, 22, 28 and 55 more)")

    def test_sku_case_variants_within_onhand_are_summed(self):
        with h.TempDir() as d:
            header, rows = read_rows(ONHAND)
            extra = list(rows[0])
            extra[0] = "e-case"
            first = list(rows[0])
            first[0] = "E-CASE "
            h.write_csv(d / "onhand.csv", header, [first, extra] + rows[1:])
            out, skus, po, _ = self.eval1(d / "out", onhand=d / "onhand.csv")
            self.assertEqual(skus["E-CASE"]["on_hand"], "80.0")
            self.assertIn("SKU_VARIANTS", skus["E-CASE"]["flags"])
            self.assertNotIn("e-case", skus)

    def test_only_blank_skus_writes_empty_outputs(self):
        with h.TempDir() as d:
            sh, srows = read_rows(POS)
            oh, orows = read_rows(ONHAND)
            for r in srows:
                r[1] = ""
            for r in orows:
                r[0] = " "
            h.write_csv(d / "sales.csv", sh, srows[:5])
            h.write_csv(d / "onhand.csv", oh, orows)
            out, skus, po, _ = self.eval1(d / "out", sales=d / "sales.csv", onhand=d / "onhand.csv")
            self.assertEqual((out["skus"], skus, po), (0, {}, {}))
            self.assertTrue(any(w.startswith("No SKUs to plan") for w in out["warnings"]), out["warnings"])
            with open(d / "out" / "replenishment.csv", newline="") as f:
                self.assertEqual(next(csv.reader(f)), REPL_FIELDS)

    def test_only_blank_sales_skus_still_plans_on_hand(self):
        with h.TempDir() as d:
            sh, srows = read_rows(POS)
            for r in srows:
                r[1] = ""
            h.write_csv(d / "sales.csv", sh, srows)
            out, skus, po, _ = self.eval1(d / "out", sales=d / "sales.csv")
            self.assertEqual(out["skus"], 8)
            self.assertEqual(po, {})

    def test_returns_only_sku_gets_zero_velocity_and_no_order(self):
        with h.TempDir() as d:
            header, rows = read_rows(POS)
            rows += [["2026-09-20", "RT-ONLY", "Returned thing", "Example Pines", "Flower", "-4", "-140.00"],
                     ["2026-09-25", "RT-ONLY", "Returned thing", "Example Pines", "Flower", "-1", "-35.00"]]
            h.write_csv(d / "sales.csv", header, rows)
            out, skus, po, _ = self.eval1(d / "out", sales=d / "sales.csv")
            rt = skus["RT-ONLY"]
            self.assertEqual((rt["units_sold_window"], rt["units_per_day"], rt["suggested_order_qty"]),
                             ("-5.0", "0.0", "0"))
            self.assertIn("NEGATIVE_NET_SALES(-5)", rt["flags"])
            self.assertIn("RETURNS_IN_WINDOW(-5)", rt["flags"])
            self.assertIn("NO_ONHAND_RECORD", rt["flags"])
            self.assertEqual(out["po_draft_total_cost"], 4620.0)

    def test_bad_as_of_date_exits_with_message(self):
        with h.TempDir() as d:
            res = self.run_repl(["--sales", POS, "--onhand", ONHAND, "--as-of", "30/09/2026", "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("Bad --as-of '30/09/2026'", res.stderr)

    def test_sales_after_as_of_are_left_out_and_warned(self):
        with h.TempDir() as d:
            out, skus, po, res = self.run_ok(POS, ONHAND, d, "--as-of", "2026-09-29", "--safety-days", "3")
            self.assertEqual(out["window"]["end"], "2026-09-29")
            self.assertTrue(any("dated after the on-hand count date (2026-09-29)" in w for w in out["warnings"]))


class FormulaInjection(ReplenishCase):
    def assert_neutralised(self, out_dir, cell):
        h.assert_no_live_formulas(self, out_dir)
        cells = [c for name in ("replenishment.csv", "po_draft.csv") for c in h.csv_cells(out_dir / name)]
        self.assertIn("'" + cell, cells)

    def test_onhand_text_columns_with_formulas_are_neutralised(self):
        for column in ("SKU", "Product Name", "Brand", "Vendor"):
            for cell in h.FORMULA_CELLS:
                with self.subTest(column=column, cell=cell), h.TempDir() as d:
                    onhand = h.mutate_csv(ONHAND, d / "onhand.csv", 0, column, cell)
                    self.eval1(d / "out", onhand=onhand)
                    self.assert_neutralised(d / "out", cell)

    def test_sales_text_columns_with_formulas_are_neutralised(self):
        # A sales-only SKU, so its sales-file text is what the outputs show.
        header, rows = read_rows(POS)
        for column in ("SKU", "Product Name", "Brand", "Category"):
            for cell in h.FORMULA_CELLS:
                with self.subTest(column=column, cell=cell), h.TempDir() as d:
                    new = ["2026-09-30", "NEW-1", "New thing", "Example Pines", "Flower", "3", "90.00"]
                    new[header.index(column)] = cell
                    h.write_csv(d / "sales.csv", header, rows + [new])
                    self.eval1(d / "out", sales=d / "sales.csv")
                    self.assert_neutralised(d / "out", cell)

    def test_csv_safe_matches_shared_text(self):
        self.assertIn("\n\n\n" + CSV_SAFE_TEXT, h.script_path(NAME).read_text())


class Determinism(ReplenishCase):
    def test_same_inputs_give_byte_identical_outputs(self):
        runs = (("eval1", POS, ONHAND, EVAL1_PARAMS),
                ("eval4", REG_SALES, REG_ONHAND, ["--as-of", "2026-09-30", "--default-lead-time", "7",
                                                  "--safety-days", "2"]),
                ("eval5", BAD_SALES, BAD_ONHAND, ["--as-of", "2026-09-30", "--safety-days", "2"]))
        for label, sales, onhand, params in runs:
            with self.subTest(run=label), h.TempDir() as d:
                self.run_ok(sales, onhand, d / "a", *params)
                self.run_ok(sales, onhand, d / "b", *params)
                for name in OUTPUTS:
                    self.assertEqual((d / "a" / name).read_bytes(), (d / "b" / name).read_bytes(), name)


def documented_args(cmd, skill_md, values):
    """Turn a SKILL.md command template into argv: drop [optional] parts, keep the first of
    `--a X | --b X` alternatives, and fill <placeholders> / bare metavars from `values`."""
    if cmd.rstrip().endswith("\\"):  # helpers' pattern stops at a line continuation; follow it here
        lines = skill_md.splitlines()
        i = next(n for n, line in enumerate(lines) if cmd.rstrip() in line)
        parts = [lines[i]]
        while parts[-1].rstrip().endswith("\\"):
            i += 1
            parts.append(lines[i])
        cmd = " ".join(p.rstrip().rstrip("\\").strip() for p in parts)
        cmd = cmd[cmd.index("python3 <skill-dir>"):]
    body = re.sub(r"^python3 <skill-dir>/scripts/\S+\.py", "", cmd)
    while re.search(r"\[[^\[\]]*\]", body):
        body = re.sub(r"\[[^\[\]]*\]", "", body)
    body = re.sub(r"\s*\|\s*--[a-z][a-z0-9-]*(\s+(?!--)[^\s|]+)?", "", body)
    argv, opt = [], None
    for tok in re.findall(r"<[^>]*>|\S+", body):
        if tok.startswith("--"):
            opt = tok
            argv.append(tok)
        elif tok.startswith("<") or re.fullmatch(r"[A-Z]+", tok):
            if opt not in values:
                raise AssertionError(f"SKILL.md documents {opt} {tok} but the test has no value for it")
            argv.append(str(values[opt]))
        else:
            argv.append(tok)
    return argv


class SkillMdCommand(ReplenishCase):
    def test_required_options_are_documented(self):
        cmds = h.skill_md_run_commands(NAME)
        self.assertTrue(cmds)
        for opt in h.required_options(NAME):
            with self.subTest(option=opt):
                self.assertTrue(any(re.search(r"(?<![\w-])" + re.escape(opt) + r"(?![\w-])", c) for c in cmds),
                                f"{opt} is required but no SKILL.md command shows it")

    def test_every_documented_command_passes_as_of(self):
        for cmd in h.skill_md_run_commands(NAME):
            with self.subTest(cmd=cmd):
                self.assertIn("--as-of <", cmd)

    def test_documented_commands_run_and_write_documented_outputs(self):
        skill_md = (h.skill_dir(NAME) / "SKILL.md").read_text()
        for cmd in h.skill_md_run_commands(NAME):
            with self.subTest(cmd=cmd), h.TempDir() as d:
                values = {"--sales": POS, "--onhand": ONHAND, "--as-of": "2026-09-30", "--out-dir": d / "out"}
                argv = documented_args(cmd, skill_md, values)
                res = self.run_repl(argv)
                self.assertEqual(res.returncode, 0, f"{shlex.join(map(str, argv))}\n{res.stdout}{res.stderr}")
                out = h.strict_json_load(res.stdout, is_text=True)
                if "--detect-only" in argv:
                    self.assertEqual(out["onhand_mapping"]["on_hand"], "Available")
                    self.assertEqual(out["missing_required_columns"], {"sales": [], "onhand": []})
                    continue
                for name in OUTPUTS:
                    self.assertTrue((d / "out" / name).exists(), name)
                self.assertEqual(out["window"]["end"], "2026-09-30")
                # Same command plus the eval 1 planning parameter gives the eval 1 answer.
                res = self.run_repl(argv + ["--safety-days", "3"])
                self.assertEqual(h.strict_json_load(res.stdout, is_text=True)["po_draft_total_cost"], 4620.0)


class NoTraceback(ReplenishCase):
    def test_odd_invocations_never_traceback(self):
        base = ["--sales", POS, "--onhand", ONHAND]
        cases = [[], base, base + ["--as-of", ""], base + ["--as-of", "2026-02-30"],
                 base + ["--as-of", "2026-09-30", "--map-sales", "units"],
                 base + ["--as-of", "2026-09-30", "--map-sales", "units=Nope"],
                 base + ["--as-of", "2026-09-30", "--map-onhand", "on_hand=Product Name"],
                 base + ["--as-of", "2026-09-30", "--window-days", "1"],
                 base + ["--as-of", "2000-01-01"]]
        for args in cases:
            with self.subTest(args=args), h.TempDir() as d:
                res = self.run_repl(args + ["--out-dir", d / "out"])
                self.assertIn(res.returncode, (0, 1, 2))

    def test_non_utf8_file_exits_with_message(self):
        with h.TempDir() as d:
            (d / "s.csv").write_bytes("Date,SKU,Units\n2026-09-30,\xe9\xff,1\n".encode("latin-1"))
            res = self.run_repl(["--sales", d / "s.csv", "--onhand", ONHAND, "--out-dir", d / "out"] + EVAL1_PARAMS)
            self.assertEqual(res.returncode, 1)
            self.assertIn("UTF-8", res.stderr)


if __name__ == "__main__":
    unittest.main()
