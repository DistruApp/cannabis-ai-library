"""Gate 2 script tests for cannabis-traceability-reconciliation/scripts/reconcile.py.

Run:  python3 -m unittest discover -s tests -t . -v
Every run writes only to a temporary directory.
"""
import csv
import filecmp
import importlib.util
import random
import re
import time
import unittest
from pathlib import Path

from tests import helpers as h

NAME = "reconcile"
SYSTEM = h.fixture(NAME, "metrc_active_packages.csv")
COUNT = h.fixture(NAME, "physical_count_2026-09-30.csv")
ERP = h.fixture(NAME, "erp_onhand_export.csv")
REG_SYSTEM = h.fixture(NAME, "regression_metrc_packages.csv")
REG_COUNT = h.fixture(NAME, "regression_count_sheet.csv")
INV_SYSTEM = h.fixture(NAME, "regression_invalid_numbers_metrc.csv")
INV_COUNT = h.fixture(NAME, "regression_invalid_numbers_count.csv")

OUTPUTS = ("reconciliation.csv", "summary.json")
TAG = "1A4060300003B21000000"  # shared prefix of every fixture tag


def tag(suffix):
    return TAG + suffix


class ReconcileCase(unittest.TestCase):
    """Shared helpers. Every script run goes through run_script, which checks for tracebacks."""

    def assertNoTraceback(self, proc):
        self.assertNotIn("Traceback", proc.stderr, proc.stderr)
        self.assertNotIn("Traceback", proc.stdout, proc.stdout)

    def run_script(self, args, cwd=None):
        proc = h.run(NAME, args, cwd=cwd)
        self.assertNoTraceback(proc)
        return proc

    def reconcile(self, tmp, system, count, *extra, expect_exit=0):
        """Run a full reconciliation into tmp/out and return (rows by package_id, summary)."""
        out = tmp / "out"
        proc = self.run_script(["--system", system, "--count", count, "--out-dir", out, *extra])
        self.assertEqual(proc.returncode, expect_exit, proc.stderr)
        summary = h.strict_json_load(out / "summary.json")
        self.assertEqual(h.strict_json_load(proc.stdout, is_text=True), summary)
        rows = h.read_csv(out / "reconciliation.csv")
        by_tag = {}
        for r in rows:
            by_tag.setdefault(r["package_id"], []).append(r)
        return {k: v[0] if len(v) == 1 else v for k, v in by_tag.items()}, summary

    def assertCleanFailure(self, proc, tmp, *phrases):
        """Non-zero exit, a readable message, no traceback, and no output files."""
        self.assertNotEqual(proc.returncode, 0)
        for p in phrases:
            self.assertIn(p, proc.stderr)
        self.assertFalse((tmp / "out").exists(), "outputs were written for a failed run")

    def assertFloat(self, cell, expected):
        self.assertNotEqual(cell, "", "expected a number, got a blank cell")
        self.assertAlmostEqual(float(cell), expected, places=6)

    def assertNumbersEqual(self, actual, expected):
        self.assertEqual(set(actual), set(expected))
        for k in expected:
            self.assertAlmostEqual(actual[k], expected[k], places=6, msg=k)


# --------------------------------------------------------------------------------------------
# 1. Known answers: every eval fixture, pinned to today's hand-verified output.
# --------------------------------------------------------------------------------------------
class KnownAnswers(ReconcileCase):

    def test_eval1_mi_month_end_statuses(self):
        with h.TempDir() as tmp:
            rows, _ = self.reconcile(tmp, SYSTEM, COUNT)
        expected = {
            "011": "COUNTED_NOT_IN_SYSTEM", "101": "MATCH", "102": "SHORT_IN_COUNT",
            "103": "SHORT_IN_COUNT", "104": "MATCH", "105": "SHORT_IN_COUNT", "106": "UOM_MISMATCH",
            "107": "IN_SYSTEM_NOT_COUNTED", "108": "OVER_IN_COUNT", "109": "MATCH",
            "110": "IN_SYSTEM_NOT_COUNTED", "199": "COUNTED_NOT_IN_SYSTEM",
        }
        self.assertEqual({k: v["status"] for k, v in rows.items()},
                         {tag(s.rjust(3, "0")): st for s, st in expected.items()})

    def test_eval1_mi_month_end_differences(self):
        with h.TempDir() as tmp:
            rows, _ = self.reconcile(tmp, SYSTEM, COUNT)
        r102 = rows[tag("102")]  # 1 lb in Metrc vs 447.9 g counted
        self.assertFloat(r102["difference"], -5.692)
        self.assertEqual(r102["difference_unit"], "g")
        self.assertFloat(r102["pct_of_system"], -1.255)
        self.assertIn("units converted", r102["notes"])
        self.assertFloat(rows[tag("103")]["difference"], -18.1)
        self.assertFloat(rows[tag("105")]["difference"], -2.0)
        self.assertEqual(rows[tag("105")]["difference_unit"], "each")
        self.assertFloat(rows[tag("108")]["difference"], 12.0)
        self.assertFloat(rows[tag("108")]["pct_of_system"], 4.0)
        self.assertEqual(rows[tag("106")]["difference"], "")  # each vs g never converted
        self.assertIn("possible tag typo", rows[tag("011")]["notes"])
        self.assertIn(tag("110"), rows[tag("011")]["notes"])
        self.assertIn(tag("011"), rows[tag("110")]["notes"])

    def test_eval1_mi_month_end_totals(self):
        with h.TempDir() as tmp:
            _, s = self.reconcile(tmp, SYSTEM, COUNT)
        self.assertEqual(s["packages_in_system"], 10)
        self.assertEqual(s["packages_in_count"], 10)
        self.assertEqual(s["packages_compared"], 12)
        self.assertEqual(s["packages_quantity_compared"], 7)
        self.assertEqual(s["by_status"], {"COUNTED_NOT_IN_SYSTEM": 2, "MATCH": 3, "SHORT_IN_COUNT": 3,
                                          "UOM_MISMATCH": 1, "IN_SYSTEM_NOT_COUNTED": 2, "OVER_IN_COUNT": 1})
        self.assertNumbersEqual(s["net_difference"], {"g": -23.792, "each": 10.0})
        self.assertNumbersEqual(s["gross_variance_outside_tolerance"], {"g": 23.792, "each": 14.0})
        self.assertNumbersEqual(s["system_total_compared"], {"g": 3041.192, "each": 420.0})
        self.assertNumbersEqual(s["system_total_all_packages"], {"g": 5309.192, "each": 718.0})
        self.assertNumbersEqual(s["net_difference_pct_of_compared_total"], {"g": -0.782, "each": 2.381})
        self.assertEqual(s["packages_over_5pct_abs"], 0)
        self.assertEqual(s["input_problems"], [])

    def test_eval2_erp_ambiguous_quantity_column_stops(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--system", SYSTEM, "--count", ERP, "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "AMBIGUOUS:Qty|Counted", "--map-count quantity=")

    def test_eval2_erp_detect_only_also_reports_ambiguity(self):
        proc = self.run_script(["--system", SYSTEM, "--count", ERP, "--detect-only"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("AMBIGUOUS:Qty|Counted", proc.stderr)

    def test_eval2_erp_mapped_to_counted_blank_is_not_zero(self):
        with h.TempDir() as tmp:
            rows, s = self.reconcile(tmp, SYSTEM, ERP, "--map-count", "quantity=Counted")
        self.assertEqual(rows[tag("103")]["status"], "BAD_QUANTITY")
        self.assertEqual(rows[tag("103")]["count_qty"], "")
        self.assertEqual(rows[tag("102")]["status"], "SHORT_IN_COUNT")
        self.assertFloat(rows[tag("102")]["difference"], -3.592)
        for t in ("104", "106", "107", "108", "109", "110"):
            self.assertEqual(rows[tag(t)]["status"], "IN_SYSTEM_NOT_COUNTED", t)
        self.assertEqual(s["by_status"], {"MATCH": 2, "SHORT_IN_COUNT": 1, "BAD_QUANTITY": 1,
                                          "IN_SYSTEM_NOT_COUNTED": 6})
        self.assertNumbersEqual(s["net_difference"], {"g": -3.592, "each": 0.0})
        self.assertNumbersEqual(s["system_total_compared"], {"g": 907.192, "each": 120.0})
        self.assertNumbersEqual(s["net_difference_pct_of_compared_total"], {"g": -0.396, "each": 0.0})
        self.assertEqual(s["packages_quantity_compared"], 3)
        self.assertEqual(s["count_mapping"]["quantity"], "Counted")
        self.assertEqual(s["input_problems"],
                         [f"count row 4 ({tag('103')}), column 'Counted': blank quantity"])

    def test_eval4_regression_statuses(self):
        with h.TempDir() as tmp:
            rows, _ = self.reconcile(tmp, REG_SYSTEM, REG_COUNT)
        # Gate 5: ...302 (two identical 50 ea rows) is held, not summed into a MATCH (F07), and
        # ...306 (+0.016 g after lb -> g) is a real overage: no automatic rounding allowance (F01).
        expected = {"301": "SHORT_IN_COUNT", "302": "DUPLICATE_CONFLICT", "303": "DUPLICATE_CONFLICT",
                    "304": "DUPLICATE_CONFLICT", "305": "MISSING_UNIT", "306": "OVER_IN_COUNT",
                    "307": "SHORT_IN_COUNT", "311": "IN_SYSTEM_NOT_COUNTED",
                    "313": "COUNTED_NOT_IN_SYSTEM", "320": "MISSING_UNIT"}
        self.assertEqual({k: v["status"] for k, v in rows.items()},
                         {tag(s): st for s, st in expected.items()})

    def test_eval4_regression_rows(self):
        with h.TempDir() as tmp:
            rows, _ = self.reconcile(tmp, REG_SYSTEM, REG_COUNT)
        r301 = rows[tag("301")]  # 500 g + 1.1 lb summed after converting to g
        self.assertFloat(r301["count_qty"], 998.9512)
        self.assertEqual(r301["count_uom"], "g")
        self.assertFloat(r301["difference"], -1.0488)
        self.assertIn("converted to g", r301["notes"])
        self.assertIn("copy-paste duplicate", rows[tag("302")]["notes"])
        for t in ("302", "303", "304"):
            self.assertEqual(rows[tag(t)]["count_qty"], "")
            self.assertEqual(rows[tag(t)]["difference"], "")
        self.assertEqual(rows[tag("305")]["count_uom"], "")  # never borrowed from the system file
        self.assertEqual(rows[tag("320")]["system_uom"], "")
        self.assertFloat(rows[tag("306")]["difference"], 0.016)
        self.assertIn("small difference (0.016 g) after converting units", rows[tag("306")]["notes"])
        self.assertFloat(rows[tag("307")]["difference"], -0.592)
        self.assertIn("possible tag typo", rows[tag("313")]["notes"])

    def test_eval4_regression_totals_and_problems(self):
        with h.TempDir() as tmp:
            _, s = self.reconcile(tmp, REG_SYSTEM, REG_COUNT)
        self.assertEqual(s["packages_quantity_compared"], 3)  # ...302 held (F07)
        self.assertNumbersEqual(s["net_difference"], {"g": -1.6248})
        self.assertNumbersEqual(s["gross_variance_outside_tolerance"], {"g": 1.6568})  # ...306 counts (F01)
        self.assertNumbersEqual(s["gross_variance_all_compared"], {"g": 1.6568})
        self.assertNumbersEqual(s["system_total_compared"], {"g": 2360.776})
        self.assertNumbersEqual(s["system_total_all_packages"], {"g": 3314.368, "each": 174.0})
        self.assertNumbersEqual(s["net_difference_pct_of_compared_total"], {"g": -0.069})
        self.assertEqual(s["default_units"], {"system": None, "count": None, "rows_using_default": {}})
        problems = s["input_problems"]
        self.assertEqual(len(problems), 7)
        self.assertEqual(problems[0], f"count row 6 ({tag('303')}), column 'Counted Qty': blank quantity")
        self.assertIn("summed (converted to g) to 998.951 g", problems[1])
        self.assertIn("copy-paste duplicate", problems[2])
        self.assertIn("NOT summed", problems[2])
        self.assertIn("NOT summed", problems[3])
        self.assertIn("NOT summed", problems[4])
        self.assertIn(f"{tag('305')}: unit is blank in the count file", problems[5])
        self.assertIn("count row(s) 10, column 'Unit'", problems[5])
        self.assertIn(f"{tag('320')}: unit is blank in the system file", problems[6])
        self.assertIn("system row(s) 10, column 'UoM'", problems[6])

    def test_eval5_invalid_numbers(self):
        with h.TempDir() as tmp:
            rows, s = self.reconcile(tmp, INV_SYSTEM, INV_COUNT)
        bad = {"601": "NaN", "602": "inf", "603": "-10", "604": "1,5", "605": "1.234,5"}
        for t in bad:
            self.assertEqual(rows[tag(t)]["status"], "INVALID_NUMBER", t)
            self.assertEqual(rows[tag(t)]["count_qty"], "", t)
            self.assertEqual(rows[tag(t)]["difference"], "", t)
        self.assertEqual(rows[tag("606")]["status"], "MATCH")  # '1,234.5' read as 1234.5
        self.assertFloat(rows[tag("606")]["system_qty"], 1234.5)
        self.assertEqual(rows[tag("607")]["status"], "SHORT_IN_COUNT")
        self.assertFloat(rows[tag("607")]["difference"], -10.0)
        self.assertEqual(s["by_status"], {"INVALID_NUMBER": 5, "MATCH": 1, "SHORT_IN_COUNT": 1})
        self.assertEqual(s["packages_quantity_compared"], 2)
        self.assertNumbersEqual(s["net_difference"], {"g": -10.0})
        self.assertNumbersEqual(s["system_total_compared"], {"g": 1434.5})
        self.assertNumbersEqual(s["net_difference_pct_of_compared_total"], {"g": -0.697})
        self.assertEqual(len(s["input_problems"]), 5)
        for (t, raw), problem, row in zip(bad.items(), s["input_problems"], range(2, 7)):
            self.assertIn(f"count row {row}, column 'Counted Qty', value '{raw}'", problem)
            self.assertIn(tag(t), problem)

    def test_detect_only_prints_mapping(self):
        proc = self.run_script(["--system", SYSTEM, "--count", COUNT, "--detect-only"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        d = h.strict_json_load(proc.stdout, is_text=True)
        self.assertEqual(d["system_mapping"], {"package_id": "Tag", "item": "Item", "quantity": "Quantity",
                                               "uom": "UoM", "location": "Location", "category": "Category"})
        self.assertEqual(d["count_mapping"], {"package_id": "Package Tag", "item": "Product",
                                              "quantity": "Counted Qty", "uom": "Unit", "location": "Room"})
        self.assertEqual((d["system_rows"], d["count_rows"]), (10, 10))

    def test_operator_tolerance_moves_small_gaps_to_within_tolerance(self):
        with h.TempDir() as tmp:
            rows, s = self.reconcile(tmp, SYSTEM, COUNT, "--tolerance-g", "20", "--tolerance-each", "2")
        self.assertEqual(rows[tag("102")]["status"], "WITHIN_TOLERANCE")
        self.assertEqual(rows[tag("103")]["status"], "WITHIN_TOLERANCE")
        self.assertEqual(rows[tag("105")]["status"], "WITHIN_TOLERANCE")
        self.assertEqual(rows[tag("108")]["status"], "OVER_IN_COUNT")
        self.assertNumbersEqual(s["net_difference"], {"g": -23.792, "each": 10.0})  # net is unchanged


# --------------------------------------------------------------------------------------------
# 2. Bad numbers: every value in h.BAD_NUMBERS in every numeric input.
# --------------------------------------------------------------------------------------------
class BadNumbers(ReconcileCase):
    """Package ...103 (907.2 g in Metrc, 889.1 g counted, -18.1 g) gets the bad value."""

    ROW = 2  # 0-based data row of ...103 in both MI fixtures; CSV line 4

    def check_bad_quantity(self, side, src, column):
        for key, raw in h.BAD_NUMBERS.items():
            with self.subTest(side=side, case=key, value=raw), h.TempDir() as tmp:
                bad = h.mutate_csv(src, tmp / f"{side}.csv", self.ROW, column, raw)
                system, count = (bad, COUNT) if side == "system" else (SYSTEM, bad)
                rows, s = self.reconcile(tmp, system, count)
                r = rows[tag("103")]
                self.assertEqual(r["status"], "INVALID_NUMBER")
                self.assertEqual(r[f"{side}_qty"], "")
                self.assertEqual(r["difference"], "")
                self.assertEqual(r["pct_of_system"], "")
                matches = [p for p in s["input_problems"]
                           if f"{side} row 4, column '{column}', value '{raw}'" in p]
                self.assertEqual(len(matches), 1, s["input_problems"])
                self.assertIn(tag("103"), matches[0])
                # ...103 drops out of every total; the other packages are unchanged.
                self.assertEqual(s["packages_quantity_compared"], 6)
                self.assertNumbersEqual(s["net_difference"], {"g": -23.792 + 18.1, "each": 10.0})
                self.assertNumbersEqual(s["gross_variance_outside_tolerance"],
                                        {"g": 23.792 - 18.1, "each": 14.0})
                self.assertNumbersEqual(s["system_total_compared"], {"g": 3041.192 - 907.2, "each": 420.0})
                all_g = 5309.192 - 907.2 if side == "system" else 5309.192
                self.assertNumbersEqual(s["system_total_all_packages"], {"g": all_g, "each": 718.0})

    def test_bad_count_quantity(self):
        self.check_bad_quantity("count", COUNT, "Counted Qty")

    def test_bad_system_quantity(self):
        self.check_bad_quantity("system", SYSTEM, "Quantity")

    def test_bad_quantity_on_package_in_only_one_file(self):
        # ...107 is only in the system file: it must not reach system_total_all_packages.
        for key, raw in h.BAD_NUMBERS.items():
            with self.subTest(case=key, value=raw), h.TempDir() as tmp:
                bad = h.mutate_csv(SYSTEM, tmp / "system.csv", 6, "Quantity", raw)
                rows, s = self.reconcile(tmp, bad, COUNT)
                self.assertEqual(rows[tag("107")]["status"], "IN_SYSTEM_NOT_COUNTED")
                self.assertEqual(rows[tag("107")]["system_qty"], "")
                self.assertNumbersEqual(s["system_total_all_packages"], {"g": 5309.192 - 2268.0, "each": 718.0})
                self.assertTrue(any(f"system row 8, column 'Quantity', value '{raw}'" in p
                                    for p in s["input_problems"]), s["input_problems"])

    def check_bad_tolerance(self, flag):
        for key, raw in h.BAD_NUMBERS.items():
            with self.subTest(flag=flag, case=key, value=raw), h.TempDir() as tmp:
                proc = self.run_script(["--system", SYSTEM, "--count", COUNT, "--out-dir", tmp / "out",
                                        f"{flag}={raw}"])
                self.assertEqual(proc.returncode, 2, proc.stderr)  # argparse usage error
                self.assertCleanFailure(proc, tmp, flag)

    def test_bad_tolerance_g(self):
        self.check_bad_tolerance("--tolerance-g")

    def test_bad_tolerance_each(self):
        self.check_bad_tolerance("--tolerance-each")


# --------------------------------------------------------------------------------------------
# 3. Structure: broken or odd files give a clean message or a reported problem, never a traceback.
# --------------------------------------------------------------------------------------------
class Structure(ReconcileCase):

    def test_empty_count_file(self):
        with h.TempDir() as tmp:
            (tmp / "count.csv").write_text("")
            proc = self.run_script(["--system", SYSTEM, "--count", tmp / "count.csv", "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "[count]", "empty")

    def test_header_only_system_file(self):
        with h.TempDir() as tmp:
            (tmp / "system.csv").write_text(SYSTEM.read_text().splitlines()[0] + "\n")
            proc = self.run_script(["--system", tmp / "system.csv", "--count", COUNT, "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "[system]", "no data rows")

    def test_missing_file(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--system", tmp / "nope.csv", "--count", COUNT, "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "[system]", "Cannot read")

    def test_non_utf8_file(self):
        with h.TempDir() as tmp:
            (tmp / "count.csv").write_bytes(COUNT.read_bytes().replace(b"Gelato", b"G\xe9lato"))
            proc = self.run_script(["--system", SYSTEM, "--count", tmp / "count.csv", "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "[count]", "UTF-8")

    def test_duplicate_column_name(self):
        with h.TempDir() as tmp:
            lines = COUNT.read_text().splitlines()
            lines = [lines[0] + ",Counted Qty"] + [l + ",1" for l in lines[1:]]
            (tmp / "count.csv").write_text("\n".join(lines) + "\n")
            proc = self.run_script(["--system", SYSTEM, "--count", tmp / "count.csv", "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "more than one column named")

    def test_mapping_to_missing_column(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--system", SYSTEM, "--count", ERP, "--out-dir", tmp / "out",
                                    "--map-count", "quantity=Countd"])
            self.assertCleanFailure(proc, tmp, "no column named 'Countd'")

    def test_mapping_with_unknown_field(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--system", SYSTEM, "--count", ERP, "--out-dir", tmp / "out",
                                    "--map-count", "qty=Counted"])
            self.assertCleanFailure(proc, tmp, "unknown field 'qty'")

    def test_identical_duplicate_count_row_is_held_and_reported(self):
        # Gate 5 (F07): an identical repeated row is a possible double entry, so it is not summed.
        with h.TempDir() as tmp:
            lines = COUNT.read_text().splitlines()
            (tmp / "count.csv").write_text("\n".join(lines + [lines[2]]) + "\n")  # ...102 twice
            rows, s = self.reconcile(tmp, SYSTEM, tmp / "count.csv")
        self.assertEqual(rows[tag("102")]["status"], "DUPLICATE_CONFLICT")
        self.assertEqual(rows[tag("102")]["count_qty"], "")
        self.assertIn("copy-paste duplicate", rows[tag("102")]["notes"])
        self.assertTrue(any(f"duplicate tag {tag('102')}" in p and "copy-paste" in p
                            for p in s["input_problems"]), s["input_problems"])

    def test_blank_tag_is_reported(self):
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Package Tag", "")
            rows, s = self.reconcile(tmp, SYSTEM, count)
        self.assertEqual(rows[tag("103")]["status"], "IN_SYSTEM_NOT_COUNTED")
        self.assertIn("count row 4, column 'Package Tag': blank package tag; row not used", s["input_problems"])

    def test_blank_quantity_is_bad_quantity_not_zero(self):
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Counted Qty", "")
            rows, s = self.reconcile(tmp, SYSTEM, count)
        self.assertEqual(rows[tag("103")]["status"], "BAD_QUANTITY")
        self.assertEqual(rows[tag("103")]["count_qty"], "")
        self.assertIn(f"count row 4 ({tag('103')}), column 'Counted Qty': blank quantity", s["input_problems"])
        self.assertNumbersEqual(s["system_total_compared"], {"g": 3041.192 - 907.2, "each": 420.0})

    def test_blank_unit_is_missing_unit(self):
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Unit", "")
            rows, s = self.reconcile(tmp, SYSTEM, count)
        self.assertEqual(rows[tag("103")]["status"], "MISSING_UNIT")
        self.assertEqual(rows[tag("103")]["count_uom"], "")
        self.assertTrue(any(tag("103") in p and "unit is blank in the count file" in p
                            for p in s["input_problems"]))

    def test_unknown_unit_is_not_compared_or_totalled(self):
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Unit", "Grms")
            rows, s = self.reconcile(tmp, SYSTEM, count)
        self.assertEqual(rows[tag("103")]["status"], "UNKNOWN_UOM")
        self.assertEqual(rows[tag("103")]["difference"], "")
        self.assertNumbersEqual(s["net_difference"], {"g": -5.692, "each": 10.0})
        self.assertNumbersEqual(s["system_total_compared"], {"g": 3041.192 - 907.2, "each": 420.0})

    def test_weight_vs_each_is_uom_mismatch(self):
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Unit", "ea")
            rows, s = self.reconcile(tmp, SYSTEM, count)
        self.assertEqual(rows[tag("103")]["status"], "UOM_MISMATCH")
        self.assertNumbersEqual(s["net_difference"], {"g": -5.692, "each": 10.0})

    def test_scientific_notation_tag_in_count(self):
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Package Tag", "1.23457E+23")
            rows, s = self.reconcile(tmp, SYSTEM, count)
        self.assertEqual(rows["1.23457E+23"]["status"], "TAG_SCIENTIFIC_NOTATION")
        self.assertEqual(rows["1.23457E+23"]["difference"], "")
        self.assertIn("count row 4", rows["1.23457E+23"]["notes"])
        self.assertEqual(rows[tag("103")]["status"], "IN_SYSTEM_NOT_COUNTED")
        self.assertTrue(any("count row 4, column 'Package Tag', value '1.23457E+23'" in p
                            and "scientific notation" in p for p in s["input_problems"]))
        self.assertEqual(s["by_status"]["TAG_SCIENTIFIC_NOTATION"], 1)
        self.assertNumbersEqual(s["net_difference"], {"g": -5.692, "each": 10.0})
        self.assertNumbersEqual(s["system_total_compared"], {"g": 3041.192 - 907.2, "each": 420.0})

    def test_scientific_notation_tags_are_never_merged_or_matched(self):
        # Excel can collapse two packages to the same value; and if both files were mangled the
        # same way they must still not "match" each other.
        with h.TempDir() as tmp:
            count = h.mutate_csv(COUNT, tmp / "c1.csv", 0, "Package Tag", "1.23457E+23")
            count = h.mutate_csv(count, tmp / "count.csv", 1, "Package Tag", "1.23457E+23")
            system = h.mutate_csv(SYSTEM, tmp / "system.csv", 0, "Tag", "1.23457E+23")
            rows, s = self.reconcile(tmp, system, count)
        sci = rows["1.23457E+23"]
        self.assertEqual(len(sci), 3)
        self.assertEqual({r["status"] for r in sci}, {"TAG_SCIENTIFIC_NOTATION"})
        self.assertFalse(any("duplicate tag" in p for p in s["input_problems"]))
        self.assertEqual(sum("scientific notation" in p for p in s["input_problems"]), 3)
        self.assertNumbersEqual(s["system_total_all_packages"], {"g": 5309.192 - 453.6, "each": 718.0})
        self.assertEqual(rows[tag("102")]["status"], "IN_SYSTEM_NOT_COUNTED")

    def test_scientific_notation_lower_case_and_negative_exponent(self):
        for raw in ("6.64713e+15", "1.5E-05", " 1.23457E+23 "):
            with self.subTest(raw=raw), h.TempDir() as tmp:
                count = h.mutate_csv(COUNT, tmp / "count.csv", 2, "Package Tag", raw)
                rows, s = self.reconcile(tmp, SYSTEM, count)
                self.assertEqual(s["by_status"].get("TAG_SCIENTIFIC_NOTATION"), 1)

    def test_bad_default_unit_is_rejected(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--system", SYSTEM, "--count", COUNT, "--out-dir", tmp / "out",
                                    "--default-count-unit", "bags"])
            self.assertCleanFailure(proc, tmp, "--default-count-unit")


# --------------------------------------------------------------------------------------------
# 4. Formula injection: no written cell may run as a spreadsheet formula.
# --------------------------------------------------------------------------------------------
class FormulaInjection(ReconcileCase):

    TEXT_COLUMNS = [
        ("count", COUNT, "Product"), ("count", COUNT, "Package Tag"), ("count", COUNT, "Room"),
        ("count", COUNT, "Unit"),
        ("system", SYSTEM, "Item"), ("system", SYSTEM, "Tag"), ("system", SYSTEM, "Location"),
        ("system", SYSTEM, "UoM"),
    ]

    def test_formula_cells_are_neutralised(self):
        for side, src, column in self.TEXT_COLUMNS:
            for value in h.FORMULA_CELLS:
                with self.subTest(side=side, column=column, value=value), h.TempDir() as tmp:
                    bad = h.mutate_csv(src, tmp / f"{side}.csv", 2, column, value)
                    system, count = (bad, COUNT) if side == "system" else (SYSTEM, bad)
                    self.reconcile(tmp, system, count)
                    h.assert_no_live_formulas(self, tmp / "out")

    def test_negative_differences_stay_numbers(self):
        with h.TempDir() as tmp:
            rows, _ = self.reconcile(tmp, SYSTEM, COUNT)
            h.assert_no_live_formulas(self, tmp / "out")
        self.assertEqual(rows[tag("102")]["difference"], "-5.692")


# --------------------------------------------------------------------------------------------
# 5. Determinism.
# --------------------------------------------------------------------------------------------
class Determinism(ReconcileCase):

    def check_identical(self, system, count):
        with h.TempDir() as tmp:
            for d in ("a", "b"):
                proc = self.run_script(["--system", system, "--count", count, "--out-dir", tmp / d])
                self.assertEqual(proc.returncode, 0, proc.stderr)
            for name in OUTPUTS:
                self.assertTrue(filecmp.cmp(tmp / "a" / name, tmp / "b" / name, shallow=False), name)

    def test_main_fixture_is_byte_identical(self):
        self.check_identical(SYSTEM, COUNT)

    def test_regression_fixture_is_byte_identical(self):
        self.check_identical(REG_SYSTEM, REG_COUNT)


# --------------------------------------------------------------------------------------------
# 6. SKILL.md commands: every required option is documented, and each documented command runs.
# --------------------------------------------------------------------------------------------
def fill_placeholders(cmd, values):
    """Turn a SKILL.md command line into argv, filling <placeholders> from values[option]."""
    cmd = re.sub(r"\[[^\]]*\]", " ", cmd)  # optional parts
    tokens = cmd.split()
    assert tokens[0] == "python3" and tokens[1].startswith("<skill-dir>/scripts/"), cmd
    args, opt = [], None
    for tok in tokens[2:]:
        if tok.startswith("--"):
            opt = tok
            args.append(tok)
        elif tok.startswith("<") or tok in ("…", "..."):
            if opt not in values:
                raise KeyError(f"no test value for placeholder {tok} after {opt} in: {cmd}")
            args.append(values[opt])
        else:
            args.append(tok)
    return args


class SkillMdCommand(ReconcileCase):

    def test_commands_found(self):
        self.assertGreaterEqual(len(h.skill_md_run_commands(NAME)), 2)

    def test_every_required_option_is_documented(self):
        required = h.required_options(NAME)
        self.assertEqual(required, ["--count", "--system"])
        cmds = h.skill_md_run_commands(NAME)
        for opt in required:
            with self.subTest(option=opt):
                self.assertTrue(any(re.search(re.escape(opt) + r"(?![\w-])", c) for c in cmds), cmds)

    def test_documented_commands_run(self):
        for cmd in h.skill_md_run_commands(NAME):
            with self.subTest(cmd=cmd), h.TempDir() as tmp:
                out = tmp / "out"
                args = fill_placeholders(cmd, {"--system": SYSTEM, "--count": COUNT, "--out-dir": out})
                proc = self.run_script(args, cwd=tmp)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                stdout = h.strict_json_load(proc.stdout, is_text=True)
                if "--detect-only" in args:
                    self.assertIn("system_mapping", stdout)
                    self.assertEqual(list(tmp.iterdir()), [])
                    continue
                self.assertIn("--out-dir", args, "run command must name the output folder")
                self.assertEqual([p.name for p in tmp.iterdir()], ["out"], "wrote outside --out-dir")
                for name in OUTPUTS:
                    self.assertTrue((out / name).is_file(), name)
                s = h.strict_json_load(out / "summary.json")
                self.assertNumbersEqual(s["net_difference"], {"g": -23.792, "each": 10.0})


# --------------------------------------------------------------------------------------------
# 7. No traceback, even on the worst input.
# --------------------------------------------------------------------------------------------
class NoTraceback(ReconcileCase):

    def test_help(self):
        proc = self.run_script(["--help"])
        self.assertEqual(proc.returncode, 0)

    def test_no_arguments(self):
        proc = self.run_script([])
        self.assertEqual(proc.returncode, 2)

    def test_binary_garbage(self):
        with h.TempDir() as tmp:
            (tmp / "count.csv").write_bytes(b"\x00\xff\xfe\x00garbage\x00\n\x00")
            proc = self.run_script(["--system", SYSTEM, "--count", tmp / "count.csv", "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp)

    def test_directory_as_input(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--system", tmp, "--count", COUNT, "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "Cannot read")

    def test_out_dir_is_a_file(self):
        with h.TempDir() as tmp:
            (tmp / "out").write_text("x")
            proc = self.run_script(["--system", SYSTEM, "--count", COUNT, "--out-dir", tmp / "out"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--out-dir", proc.stderr)

    def test_ragged_rows(self):
        with h.TempDir() as tmp:
            lines = COUNT.read_text().splitlines()
            lines[3] = lines[3].split(",")[0]  # ...103 row with only a tag
            lines[4] = lines[4] + ",extra,cells"
            (tmp / "count.csv").write_text("\n".join(lines) + "\n")
            rows, s = self.reconcile(tmp, SYSTEM, tmp / "count.csv")
        self.assertEqual(rows[tag("103")]["status"], "BAD_QUANTITY")


# --------------------------------------------------------------------------------------------
# 8. Gate 5 regressions: each one reproduces a reviewer finding (F01-F14).
# --------------------------------------------------------------------------------------------
SYS_HDR = ["Tag", "Item", "Quantity", "UoM"]
CNT_HDR = ["Package Tag", "Product", "Counted Qty", "Unit"]


class Gate5(ReconcileCase):

    def pair(self, tmp, system_rows, count_rows, *extra, sys_hdr=SYS_HDR, cnt_hdr=CNT_HDR):
        h.write_csv(tmp / "s.csv", sys_hdr, system_rows)
        h.write_csv(tmp / "c.csv", cnt_hdr, count_rows)
        return self.reconcile(tmp, tmp / "s.csv", tmp / "c.csv", *extra)

    def test_f01_unit_conversion_never_hides_a_shortage(self):
        # Different weight units are not evidence of rounding: 1 g vs 960 mg is a real -0.04 g.
        cases = [("1", "g", "960", "mg", -0.04), ("0.01", "g", "0", "mg", -0.01),
                 ("100", "kg", "99995", "g", -5.0), ("2", "lb", "907.2", "g", 0.016)]
        for sq, su, cq, cu, diff in cases:
            with self.subTest(system=f"{sq} {su}", count=f"{cq} {cu}"), h.TempDir() as tmp:
                rows, s = self.pair(tmp, [["P1", "x", sq, su]], [["P1", "x", cq, cu]])
                r = rows["P1"]
                self.assertEqual(r["status"], "SHORT_IN_COUNT" if diff < 0 else "OVER_IN_COUNT")
                self.assertFloat(r["difference"], diff)
                self.assertNumbersEqual(s["gross_variance_outside_tolerance"], {"g": abs(diff)})

    def test_f01_operator_tolerance_still_applies_to_converted_rows(self):
        with h.TempDir() as tmp:
            rows, _ = self.pair(tmp, [["P1", "x", "2", "lb"]], [["P1", "x", "907.2", "g"]],
                                "--tolerance-g", "0.05")
        self.assertEqual(rows["P1"]["status"], "WITHIN_TOLERANCE")

    def test_f02_single_comma_group_is_held_not_guessed(self):
        # '1,234' is 1234 in US format but 1.234 in European format: never guessed.
        for raw in ("1,234", "12,345", "-1,234"):
            with self.subTest(raw=raw), h.TempDir() as tmp:
                rows, s = self.pair(tmp, [["P1", "x", "1234", "g"]], [["P1", "x", raw, "g"]])
                self.assertEqual(rows["P1"]["status"], "INVALID_NUMBER")
                self.assertEqual(rows["P1"]["count_qty"], "")
                self.assertTrue(any(f"value '{raw}'" in p for p in s["input_problems"]), s["input_problems"])

    def test_f02_unambiguous_thousands_still_read(self):
        with h.TempDir() as tmp:
            rows, _ = self.pair(tmp, [["P1", "x", "1,234,567", "g"], ["P2", "x", "1,234.5", "g"]],
                                [["P1", "x", "1234567", "g"], ["P2", "x", "1234.5", "g"]])
        self.assertEqual(rows["P1"]["status"], "MATCH")
        self.assertEqual(rows["P2"]["status"], "MATCH")

    def test_f02_currency_symbol_in_quantity_is_invalid(self):
        for raw in ("$1$0", "$10"):
            with self.subTest(raw=raw), h.TempDir() as tmp:
                rows, _ = self.pair(tmp, [["P1", "x", "10", "g"]], [["P1", "x", raw, "g"]])
                self.assertEqual(rows["P1"]["status"], "INVALID_NUMBER")

    def test_f02_ambiguous_tolerance_is_rejected(self):
        for raw in ("1,000", "$5"):
            with self.subTest(raw=raw), h.TempDir() as tmp:
                proc = self.run_script(["--system", SYSTEM, "--count", COUNT, "--out-dir", tmp / "out",
                                        f"--tolerance-g={raw}"])
                self.assertEqual(proc.returncode, 2, proc.stderr)
                self.assertCleanFailure(proc, tmp, "--tolerance-g")

    def test_f03_headers_that_collide_after_normalising_stop(self):
        for hdr in (["Package Tag", "Product", "Qty", "qty", "Unit"],
                    ["Package Tag", "package_tag", "Product", "Qty", "Unit"]):
            with self.subTest(headers=hdr), h.TempDir() as tmp:
                h.write_csv(tmp / "c.csv", hdr, [["P", "P", "x", "100", "g"]])
                proc = self.run_script(["--system", SYSTEM, "--count", tmp / "c.csv", "--out-dir", tmp / "out"])
                self.assertCleanFailure(proc, tmp, "more than one column named")

    def test_f04_unsigned_exponent_tag_is_never_matched(self):
        for raw in ("1.23457E23", "6.64713e15", "1E23"):
            with self.subTest(raw=raw), h.TempDir() as tmp:
                rows, s = self.pair(tmp, [[raw, "x", "10", "g"]], [[raw, "x", "10", "g"]])
                self.assertEqual(s["by_status"], {"TAG_SCIENTIFIC_NOTATION": 2})
                self.assertEqual(s["packages_quantity_compared"], 0)
                self.assertEqual(s["net_difference"], {})

    def test_f05_huge_converted_values_never_overflow(self):
        with h.TempDir() as tmp:
            rows, s = self.pair(tmp, [["P1", "x", "1e308", "kg"], ["P2", "x", "1e12", "kg"]],
                                [["P1", "x", "1e308", "kg"], ["P2", "x", "1e12", "kg"]])
        self.assertEqual(rows["P1"]["status"], "INVALID_NUMBER")
        self.assertEqual(rows["P2"]["status"], "MATCH")
        self.assertNumbersEqual(s["system_total_compared"], {"g": 1e15})

    def test_f06_tiny_difference_is_kept_in_row_and_totals(self):
        with h.TempDir() as tmp:
            rows, s = self.pair(tmp, [["P1", "x", "1", "mg"]], [["P1", "x", "0.96", "mg"]])
        self.assertEqual(rows["P1"]["status"], "SHORT_IN_COUNT")
        self.assertFloat(rows["P1"]["difference"], -0.00004)
        self.assertNumbersEqual(s["net_difference"], {"g": -0.00004})
        self.assertNumbersEqual(s["gross_variance_outside_tolerance"], {"g": 0.00004})

    def test_f06_threshold_uses_unrounded_percentage(self):
        with h.TempDir() as tmp:
            rows, s = self.pair(tmp, [["P1", "x", "1000000", "ea"], ["P2", "x", "100", "ea"]],
                                [["P1", "x", "950004", "ea"], ["P2", "x", "95", "ea"]])
        # P1 is -4.9996% (shown rounded as -5.0); only P2 actually reaches 5%.
        self.assertEqual(s["packages_over_5pct_abs"], 1)

    def test_f07_identical_duplicate_rows_are_held_not_summed(self):
        with h.TempDir() as tmp:
            rows, s = self.pair(tmp, [["P1", "x", "100", "ea"]],
                                [["P1", "x", "50", "ea"], ["P1", "x", "50", "ea"]])
        r = rows["P1"]
        self.assertEqual(r["status"], "DUPLICATE_CONFLICT")  # never a MATCH on 50 + 50
        self.assertEqual(r["count_qty"], "")
        self.assertIn("copy-paste duplicate", r["notes"])
        self.assertEqual(s["packages_quantity_compared"], 0)
        self.assertTrue(any("NOT summed" in p and "copy-paste" in p for p in s["input_problems"]))

    def test_f08_default_unit_is_applied_before_duplicates_are_combined(self):
        with h.TempDir() as tmp:
            rows, s = self.pair(tmp, [["P1", "x", "1000", "g"]],
                                [["P1", "x", "500", ""], ["P1", "x", "400", "g"]],
                                "--default-count-unit", "g")
        r = rows["P1"]
        self.assertEqual(r["status"], "SHORT_IN_COUNT")
        self.assertFloat(r["difference"], -100.0)
        self.assertIn("--default-count-unit g", r["notes"])
        self.assertEqual(s["default_units"]["rows_using_default"], {"count": 1})

    def test_f09_file_with_no_usable_tag_stops(self):
        with h.TempDir() as tmp:
            h.write_csv(tmp / "c.csv", CNT_HDR, [["", "x", "10", "g"], [" ", "x", "5", "g"]])
            proc = self.run_script(["--system", SYSTEM, "--count", tmp / "c.csv", "--out-dir", tmp / "out"])
            self.assertCleanFailure(proc, tmp, "[count]", "package tag")

    def test_f14_gross_variance_of_all_compared_rows(self):
        with h.TempDir() as tmp:
            _, s = self.reconcile(tmp, SYSTEM, COUNT, "--tolerance-g", "20")
        self.assertNumbersEqual(s["gross_variance_outside_tolerance"], {"each": 14.0})
        self.assertNumbersEqual(s["gross_variance_all_compared"], {"g": 23.792, "each": 14.0})



def _load_reconcile_module():
    spec = importlib.util.spec_from_file_location("reconcile_under_test", h.script_path(NAME))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _levenshtein(a, b):
    """Plain full-table edit distance: the oracle for the near-match index."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _random_tags(rng, n):
    return ["1A40603000" + "".join(rng.choice("0123456789ABCDEF") for _ in range(4))
            + "%010d" % rng.randrange(10 ** 10) for _ in range(n)]


class Round2(ReconcileCase):
    """Gate 5 round 2 (second reviewer): T1 near-match speed, T6 invisible characters in tags."""

    def pair(self, tmp, system_rows, count_rows, *extra):
        h.write_csv(tmp / "s.csv", SYS_HDR, system_rows)
        h.write_csv(tmp / "c.csv", CNT_HDR, count_rows)
        return self.reconcile(tmp, tmp / "s.csv", tmp / "c.csv", *extra)

    def test_t1_near_match_index_finds_exactly_what_a_full_scan_finds(self):
        # The index must be exact: same hints as comparing every pair, never fewer.
        mod = _load_reconcile_module()
        rng = random.Random(20261111)
        for trial in range(25):
            system = _random_tags(rng, 60) + [TAG + "%03d" % i for i in range(40)] + ["AB", "A", "ABC"]
            count = []
            for t in rng.sample(system, 50):
                t = list(t)
                for _ in range(rng.randint(1, 3)):
                    op, p = rng.choice("sid"), rng.randrange(len(t))
                    if op == "s":
                        t[p] = rng.choice("0123456789AB")
                    elif op == "i":
                        t.insert(p, rng.choice("0123456789"))
                    elif len(t) > 1:
                        del t[p]
                count.append("".join(t))
            count += _random_tags(rng, 20) + ["", "B", "AC"]
            only_s = sorted(set(system) - set(count))
            only_c = sorted(set(count) - set(system))
            want = {}
            for c in only_c:
                cands = [s for s in only_s if _levenshtein(c, s) <= 2]
                if len(cands) == 1:
                    want[c] = cands
            with self.subTest(trial=trial):
                self.assertEqual(mod.single_near_matches(only_c, only_s), want)
                # A small block size must give the same answer as one block.
                self.assertEqual(mod.single_near_matches(only_c, only_s, block=7), want)

    def test_t1_edit_distance_check_matches_full_table(self):
        mod = _load_reconcile_module()
        rng = random.Random(7)
        for _ in range(3000):
            a = "".join(rng.choice("AB12") for _ in range(rng.randint(0, 9)))
            b = "".join(rng.choice("AB12") for _ in range(rng.randint(0, 9)))
            self.assertEqual(mod.edit_distance_le(a, b, 2), _levenshtein(a, b) <= 2, (a, b))

    def test_t1_5000_by_5000_with_no_tags_in_common_runs_fast(self):
        # Reviewer's case: a full export against the wrong file, so every tag is unmatched.
        # The old all-pairs scan took 82 s at 1,500 x 1,500 (about 15 min here).
        rng = random.Random(1)
        system = _random_tags(rng, 5000)
        count = _random_tags(rng, 5000)
        typo = system[0][:-1] + ("0" if system[0][-1] != "0" else "1")  # one planted typo
        count[0] = typo
        with h.TempDir() as tmp:
            start = time.monotonic()
            rows, s = self.pair(tmp, [[t, "x", "100", "g"] for t in system],
                                [[t, "x", "100", "g"] for t in count])
            elapsed = time.monotonic() - start
        self.assertLess(elapsed, 10.0, f"5,000 x 5,000 took {elapsed:.1f} s")
        self.assertEqual(s["by_status"].get("COUNTED_NOT_IN_SYSTEM"), 5000)
        self.assertIn("possible tag typo", rows[typo]["notes"])
        self.assertIn(system[0], rows[typo]["notes"])
        self.assertIn(typo, rows[system[0]]["notes"])

    def test_t1_sequential_tag_runs_stay_fast(self):
        # Sequential tags are the worst case for any index: many tags sit within 2 edits.
        system = [["1A4060300003D2F000%06d" % i, "x", "1", "each"] for i in range(0, 8000, 2)]
        count = [["1A4060300003D2F000%06d" % i, "x", "1", "each"] for i in range(1, 8000, 2)]
        with h.TempDir() as tmp:
            start = time.monotonic()
            rows, s = self.pair(tmp, system, count)
            elapsed = time.monotonic() - start
        self.assertLess(elapsed, 10.0, f"4,000 x 4,000 sequential took {elapsed:.1f} s")
        self.assertEqual(s["by_status"].get("COUNTED_NOT_IN_SYSTEM"), 4000)
        # Every count tag has several system tags within 2 edits, so no single-typo hint.
        self.assertNotIn("possible tag typo", rows["1A4060300003D2F000000001"]["notes"])

    def test_t6_invisible_characters_in_a_tag_do_not_split_the_package(self):
        # A zero-width space, zero-width joiner, word joiner or byte-order mark pasted into a tag
        # is invisible on screen; the same package must match, not show as two variances.
        for ch in ("​", "‌", "‍", "⁠", "﻿", "­"):
            with self.subTest(char=hex(ord(ch))), h.TempDir() as tmp:
                rows, s = self.pair(tmp, [[tag("101"), "x", "100", "g"]],
                                    [[tag("1") + ch + "01", "x", "100", "g"]])
                self.assertEqual(list(rows), [tag("101")])
                self.assertEqual(rows[tag("101")]["status"], "MATCH")
                self.assertEqual(s["by_status"], {"MATCH": 1})


if __name__ == "__main__":
    unittest.main()
