"""Gate 2 script tests for cannabis-transfer-manifest-precheck/scripts/precheck.py.

Run:  python3 -m unittest discover -s tests -t . -v
Every run writes only to a temporary directory. The rule under test throughout: the script
fails closed. Any bad input gives HOLD (or a clean refusal to run), never GO.
"""
import filecmp
import re
import unittest

from tests import helpers as h

NAME = "precheck"
F = lambda name: h.fixture(NAME, name)  # noqa: E731

SO_1042 = (F("sales_order_SO-1042.csv"), F("draft_manifest_SO-1042.csv"), F("inventory_active_packages.csv"))
SO_1043 = (F("sales_order_SO-1043.csv"), F("draft_manifest_SO-1043.csv"), F("inventory_active_packages.csv"))
SO_2051 = (F("regression_sales_order_SO-2051.csv"), F("regression_draft_manifest_SO-2051.csv"),
           F("regression_inventory_active_packages.csv"))
SO_3061 = (F("regression_sales_order_SO-3061.csv"), F("regression_draft_manifest_SO-3061.csv"),
           F("regression_inventory_SO-3061.csv"))
ROLES = ("order", "manifest", "inventory")
OUTPUTS = ("precheck_lines.csv", "precheck_summary.json")
PASSED = ["--passing-lab-values", "TestPassed"]
TAG = "1A4060300003B21000000"


def tag(suffix):
    return TAG + suffix


class PrecheckCase(unittest.TestCase):

    def assertNoTraceback(self, proc):
        self.assertNotIn("Traceback", proc.stderr, proc.stderr)
        self.assertNotIn("Traceback", proc.stdout, proc.stdout)

    def run_script(self, args, cwd=None):
        proc = h.run(NAME, args, cwd=cwd)
        self.assertNoTraceback(proc)
        return proc

    def files_args(self, files):
        return [x for role, path in zip(ROLES, files) for x in (f"--{role}", path)]

    def precheck(self, tmp, files, *extra):
        """Run a full precheck into tmp/out; return (lines, summary). Exit status is always 0."""
        out = tmp / "out"
        proc = self.run_script(self.files_args(files) + ["--out-dir", out, *extra])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        summary = h.strict_json_load(out / "precheck_summary.json")
        self.assertEqual(h.strict_json_load(proc.stdout, is_text=True), summary)
        lines = h.read_csv(out / "precheck_lines.csv")
        self.assertEqual(summary["lines_go"] + summary["lines_hold"], len(lines))
        if summary["overall"] == "GO":  # the fail-closed invariant, checked on every run
            self.assertEqual(summary["input_problems"], [])
            self.assertTrue(all(l["result"] == "GO" for l in lines))
        return lines, summary

    def mutated(self, tmp, files, role, row, column, value):
        """Copy of the fixture set with one cell changed in one file."""
        files = list(files)
        i = ROLES.index(role)
        files[i] = h.mutate_csv(files[i], tmp / f"{role}.csv", row, column, value)
        return files

    def with_lines(self, tmp, files, role, edit):
        """Copy of the fixture set with one file's text lines edited by edit(lines) -> lines."""
        files = list(files)
        i = ROLES.index(role)
        lines = edit(files[i].read_text().splitlines())
        files[i] = tmp / f"{role}.csv"
        files[i].write_text("\n".join(lines) + ("\n" if lines else ""))
        return files

    def line(self, lines, manifest_row):
        found = [l for l in lines if l["manifest_row"] == str(manifest_row)]
        self.assertEqual(len(found), 1, manifest_row)
        return found[0]

    def flags(self, l):
        return l["flags"].split(";") if l["flags"] else []

    def assertHeld(self, l, flag):
        self.assertEqual(l["result"], "HOLD", l)
        self.assertIn(flag, self.flags(l), l)

    def assertCleanFailure(self, proc, tmp, *phrases):
        self.assertNotEqual(proc.returncode, 0)
        for p in phrases:
            self.assertIn(p, proc.stderr)
        self.assertNotIn('"overall": "GO"', proc.stdout)
        self.assertFalse((tmp / "out").exists(), "outputs were written for a failed run")


# --------------------------------------------------------------------------------------------
# 1. Known answers: every eval fixture, pinned to today's hand-verified output.
# --------------------------------------------------------------------------------------------
class KnownAnswers(PrecheckCase):

    def test_eval1_so1042_lines(self):
        with h.TempDir() as tmp:
            lines, _ = self.precheck(tmp, SO_1042, *PASSED)
        got = [(l["source"], l["manifest_row"], l["package_id"], l["flags"], l["result"]) for l in lines]
        self.assertEqual(got, [
            ("manifest", "2", tag("201"), "", "GO"),
            ("manifest", "3", tag("202"), "UNIT_CONVERSION_ROUNDING;ORDER_QTY_ROUNDING", "HOLD"),
            ("manifest", "4", tag("203"), "ORDER_QTY_MISMATCH", "HOLD"),
            ("manifest", "5", tag("204"), "EXCEEDS_ON_HAND;ORDER_QTY_MISMATCH", "HOLD"),
            ("manifest", "6", tag("205"), "NOT_ON_ORDER;LAB_NOT_PASSED", "HOLD"),
            ("manifest", "7", tag("206"), "NOT_ON_ORDER;NOT_IN_ACTIVE_INVENTORY", "HOLD"),
            ("manifest", "8", tag("207"), "DUPLICATE_TAG_ON_MANIFEST;LAB_NOT_PASSED", "HOLD"),
            ("manifest", "9", tag("207"), "DUPLICATE_TAG_ON_MANIFEST;LAB_NOT_PASSED", "HOLD"),
            ("order", "", tag("208"), "ON_ORDER_NOT_ON_MANIFEST", "HOLD"),
        ])
        by_row = {l["manifest_row"]: l for l in lines}
        self.assertEqual((by_row["5"]["manifest_qty"], by_row["5"]["on_hand_qty"], by_row["5"]["order_qty"]),
                         ("60.0", "48.0", "50.0"))
        self.assertEqual((by_row["3"]["manifest_qty"], by_row["3"]["manifest_uom"], by_row["3"]["on_hand_qty"],
                          by_row["3"]["on_hand_uom"]), ("2268.0", "Grams", "5.0", "Pounds"))
        self.assertEqual(by_row["3"]["order_qty"], "2267.96")  # 5 lb in grams
        self.assertEqual(by_row["4"]["order_qty"], "24.0")
        self.assertEqual(by_row["6"]["lab_status"], "TestFailed")
        self.assertEqual(by_row["8"]["lab_status"], "SubmittedForTesting")
        self.assertEqual(by_row[""]["order_qty"], "12.0")

    def test_eval1_so1042_summary(self):
        with h.TempDir() as tmp:
            _, s = self.precheck(tmp, SO_1042, *PASSED)
        self.assertEqual(s["overall"], "HOLD")
        self.assertEqual(s["order_join_key"], "package_id")
        self.assertEqual(s["passing_lab_values_used"], ["testpassed"])
        self.assertEqual((s["manifest_lines"], s["lines_go"], s["lines_hold"]), (8, 1, 8))
        self.assertEqual(s["flags"], {"UNIT_CONVERSION_ROUNDING": 1, "ORDER_QTY_ROUNDING": 1,
                                      "ORDER_QTY_MISMATCH": 2, "EXCEEDS_ON_HAND": 1, "NOT_ON_ORDER": 2,
                                      "LAB_NOT_PASSED": 3, "NOT_IN_ACTIVE_INVENTORY": 1,
                                      "DUPLICATE_TAG_ON_MANIFEST": 2, "ON_ORDER_NOT_ON_MANIFEST": 1})
        self.assertEqual(s["input_problems"], [])
        checks = " ".join(v["check"] for v in s["verify_manually"])
        self.assertIn("Receiving license", checks)
        self.assertIn("Driver(s), vehicle", checks)

    def test_eval1_so1042_detect_only_lists_lab_values(self):
        proc = self.run_script(self.files_args(SO_1042) + ["--detect-only"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        d = h.strict_json_load(proc.stdout, is_text=True)
        self.assertEqual(d["distinct_lab_status_values"], ["SubmittedForTesting", "TestFailed", "TestPassed"])
        self.assertEqual(d["order_join_key"], "package_id")
        self.assertEqual(d["rows"], {"order": 6, "manifest": 8, "inventory": 7})
        self.assertEqual(d["inventory_mapping"]["lab_status"], "Lab Testing State")

    def test_eval1_so1042_without_confirmed_lab_values_holds_every_line(self):
        with h.TempDir() as tmp:
            lines, s = self.precheck(tmp, SO_1042)
        self.assertEqual(s["overall"], "HOLD")
        self.assertEqual(s["lines_go"], 0)
        self.assertEqual(s["passing_lab_values_used"], [])
        self.assertHeld(self.line(lines, 2), "LAB_STATUS_UNCONFIRMED")
        self.assertEqual(s["flags"]["LAB_STATUS_UNCONFIRMED"], 7)  # every line found in inventory

    def test_eval2_so1043_sku_join_is_go(self):
        with h.TempDir() as tmp:
            lines, s = self.precheck(tmp, SO_1043, *PASSED)
        self.assertEqual(s["overall"], "GO")
        self.assertEqual(s["order_join_key"], "sku")
        self.assertEqual([(l["join_key"], l["flags"], l["result"]) for l in lines],
                         [("gel-35", "", "GO"), ("tin-11", "", "GO")])
        self.assertEqual((s["manifest_lines"], s["lines_go"], s["lines_hold"]), (2, 2, 0))
        self.assertEqual(s["flags"], {})
        self.assertIn("Manual checks below are still required", s["note"])
        self.assertTrue(s["verify_manually"])

    def test_eval2_so1043_lab_values_are_case_insensitive(self):
        with h.TempDir() as tmp:
            _, s = self.precheck(tmp, SO_1043, "--passing-lab-values", "testpassed")
        self.assertEqual(s["overall"], "GO")

    def test_eval3_missing_inventory_refuses_to_run(self):
        with h.TempDir() as tmp:
            proc = self.run_script(["--order", SO_1043[0], "--manifest", SO_1043[1], "--out-dir", tmp / "out"])
            self.assertEqual(proc.returncode, 2)
            self.assertCleanFailure(proc, tmp, "--inventory")

    def test_eval4_so2051_lines(self):
        with h.TempDir() as tmp:
            lines, s = self.precheck(tmp, SO_2051, *PASSED)
        got = [(l["package_id"], l["flags"], l["result"]) for l in lines]
        self.assertEqual(got, [
            (tag("401"), "MISSING_UNIT", "HOLD"),
            (tag("402"), "EXCEEDS_ON_HAND;ORDER_QTY_MISMATCH", "HOLD"),
            (tag("403"), "DUPLICATE_INVENTORY_TAG", "HOLD"),
            (tag("404"), "", "GO"),
            (tag("405"), "UNIT_CONVERSION_ROUNDING;ORDER_QTY_ROUNDING", "HOLD"),
            (tag("406"), "INVENTORY_UNIT_MISSING", "HOLD"),
        ])
        self.assertEqual(lines[0]["manifest_uom"], "")  # never borrowed from order or inventory
        self.assertIn("row 4: 50 Each, lab status TestPassed; row 5: 10 Each, lab status TestFailed",
                      lines[2]["notes"])
        self.assertEqual((lines[2]["on_hand_qty"], lines[2]["lab_status"]), ("", ""))
        self.assertEqual(s["overall"], "HOLD")
        self.assertEqual((s["manifest_lines"], s["lines_go"], s["lines_hold"]), (6, 1, 5))

    def test_eval4_so2051_input_problems(self):
        with h.TempDir() as tmp:
            _, s = self.precheck(tmp, SO_2051, *PASSED)
        self.assertEqual(s["input_problems"], [
            "inventory row(s) 7: blank package tag; these rows were not checked against the manifest",
            f"inventory: duplicate tag {tag('403')} on 2 rows (row 4: 50 Each, lab status TestPassed; row 5: "
            "10 Each, lab status TestFailed); any manifest line with this tag is held as DUPLICATE_INVENTORY_TAG",
            f"manifest row 2 ({tag('401')}): blank unit; line held as MISSING_UNIT",
            f"inventory row 9 ({tag('406')}): blank unit; manifest row 7 held as INVENTORY_UNIT_MISSING",
        ])

    def test_eval5_so3061_lines(self):
        with h.TempDir() as tmp:
            lines, s = self.precheck(tmp, SO_3061, *PASSED)
        got = [(l["package_id"], l["flags"], l["result"]) for l in lines]
        self.assertEqual(got, [(tag("501"), "INVALID_NUMBER", "HOLD"), (tag("502"), "INVALID_NUMBER", "HOLD"),
                               (tag("503"), "INVALID_NUMBER", "HOLD"), (tag("504"), "INVALID_NUMBER", "HOLD"),
                               (tag("505"), "INVALID_NUMBER", "HOLD"), (tag("506"), "ITEM_MISMATCH", "HOLD"),
                               (tag("507"), "", "GO"), (tag("508"), "INVALID_NUMBER", "HOLD"),
                               (tag("509"), "INVALID_NUMBER", "HOLD"), (tag("510"), "ITEM_MISSING", "HOLD")])
        for l in lines[:5]:  # never guessed
            self.assertEqual(l["manifest_qty"], "")
        self.assertEqual(lines[7]["on_hand_qty"], "")
        self.assertEqual(lines[8]["order_qty"], "")
        self.assertIn("'Example Pre-Roll 1g'", lines[5]["notes"])
        self.assertIn("'Example Gel Caps 10mg 30ct'", lines[5]["notes"])
        self.assertEqual((s["overall"], s["lines_go"], s["lines_hold"]), ("HOLD", 1, 9))
        self.assertEqual(s["flags"], {"INVALID_NUMBER": 7, "ITEM_MISMATCH": 1, "ITEM_MISSING": 1})

    def test_eval5_so3061_input_problems(self):
        with h.TempDir() as tmp:
            _, s = self.precheck(tmp, SO_3061, *PASSED)
        p = s["input_problems"]
        self.assertEqual(len(p), 8)
        self.assertIn("inventory row 9, column 'Quantity', value '12,5'", p[0])
        self.assertIn("order row 10, column 'Ordered Qty', value 'inf'", p[1])
        for i, (row, raw) in enumerate([(2, "NaN"), (3, "inf"), (4, "-10"), (5, "1,5"), (6, "1.234,5")]):
            self.assertIn(f"manifest row {row}, column 'Quantity', value '{raw}'", p[2 + i])
            self.assertIn("line held as INVALID_NUMBER", p[2 + i])
        self.assertEqual(p[7], f"inventory row 11 ({tag('510')}), column 'Item': blank item; "
                               "manifest row 11 held as ITEM_MISSING")


# --------------------------------------------------------------------------------------------
# 2. Bad numbers: every value in h.BAD_NUMBERS in every quantity column. SO-1043 is all GO
#    before the change, so any HOLD is caused by the bad value alone.
# --------------------------------------------------------------------------------------------
class BadNumbers(PrecheckCase):

    COLUMNS = [  # (file, column, problem prefix, output cell that must stay blank)
        ("manifest", "Quantity", "manifest row 2, column 'Quantity'", "manifest_qty"),
        ("inventory", "Quantity", "inventory row 2, column 'Quantity'", "on_hand_qty"),
        ("order", "Qty", "order row 2, column 'Qty'", "order_qty"),
    ]

    def test_bad_numbers_hold_the_line_and_overall(self):
        for role, column, where, cell in self.COLUMNS:
            for key, raw in h.BAD_NUMBERS.items():
                with self.subTest(file=role, case=key, value=raw), h.TempDir() as tmp:
                    files = self.mutated(tmp, SO_1043, role, 0, column, raw)
                    lines, s = self.precheck(tmp, files, *PASSED)
                    l = self.line(lines, 2)
                    self.assertHeld(l, "INVALID_NUMBER")
                    self.assertEqual(l[cell], "")
                    self.assertEqual(s["overall"], "HOLD")
                    self.assertEqual(s["flags"].get("INVALID_NUMBER"), 1)
                    matches = [p for p in s["input_problems"] if f"{where}, value '{raw}'" in p]
                    self.assertEqual(len(matches), 1, s["input_problems"])
                    # Never totalled: no quantity comparison was made with the bad value.
                    for f in ("ORDER_QTY_MISMATCH", "EXCEEDS_ON_HAND", "ORDER_QTY_ROUNDING"):
                        self.assertNotIn(f, self.flags(l))
                    self.assertEqual(self.line(lines, 3)["result"], "GO")  # other line unaffected

    def test_bad_order_quantity_on_unshipped_order_line(self):
        for key, raw in h.BAD_NUMBERS.items():
            with self.subTest(case=key, value=raw), h.TempDir() as tmp:
                files = self.mutated(tmp, SO_1042, "order", 5, "Ordered Qty", raw)  # ...208, not shipped
                lines, s = self.precheck(tmp, files, *PASSED)
                order_line = [l for l in lines if l["source"] == "order"][0]
                self.assertEqual(order_line["flags"], "ON_ORDER_NOT_ON_MANIFEST;INVALID_NUMBER")
                self.assertEqual(order_line["order_qty"], "")
                self.assertTrue(any(f"order row 7, column 'Ordered Qty', value '{raw}'" in p
                                    for p in s["input_problems"]))


# --------------------------------------------------------------------------------------------
# 3. Structure: broken or odd files give a clean message or HOLD, never a traceback, never GO.
# --------------------------------------------------------------------------------------------
class Structure(PrecheckCase):

    def test_empty_files(self):
        for role in ROLES:
            with self.subTest(file=role), h.TempDir() as tmp:
                files = self.with_lines(tmp, SO_1043, role, lambda lines: [])
                proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
                self.assertCleanFailure(proc, tmp, f"[{role}]", "empty")

    def test_header_only_files(self):
        for role in ROLES:
            with self.subTest(file=role), h.TempDir() as tmp:
                files = self.with_lines(tmp, SO_1043, role, lambda lines: lines[:1])
                proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
                self.assertCleanFailure(proc, tmp, f"[{role}]", "no data rows")

    def test_missing_file(self):
        with h.TempDir() as tmp:
            files = (SO_1043[0], tmp / "nope.csv", SO_1043[2])
            proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
            self.assertCleanFailure(proc, tmp, "[manifest]", "Cannot read")

    def test_non_utf8_file(self):
        with h.TempDir() as tmp:
            (tmp / "inventory.csv").write_bytes(SO_1043[2].read_bytes().replace(b"Gelato", b"G\xe9lato"))
            files = (SO_1043[0], SO_1043[1], tmp / "inventory.csv")
            proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
            self.assertCleanFailure(proc, tmp, "[inventory]", "UTF-8")

    def test_mapping_to_missing_column(self):
        with h.TempDir() as tmp:
            proc = self.run_script(self.files_args(SO_1043) + ["--out-dir", tmp / "out", *PASSED,
                                                               "--map-inventory", "lab_status=Lab Stat"])
            self.assertCleanFailure(proc, tmp, "no column named 'Lab Stat'")

    def test_mapping_with_unknown_field(self):
        with h.TempDir() as tmp:
            proc = self.run_script(self.files_args(SO_1043) + ["--out-dir", tmp / "out", *PASSED,
                                                               "--map-manifest", "qty=Quantity"])
            self.assertCleanFailure(proc, tmp, "unknown field 'qty'")

    def test_duplicate_manifest_row(self):
        with h.TempDir() as tmp:
            files = self.with_lines(tmp, SO_1043, "manifest", lambda l: l + [l[1]])
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "DUPLICATE_TAG_ON_MANIFEST")
        self.assertHeld(self.line(lines, 4), "DUPLICATE_TAG_ON_MANIFEST")
        self.assertEqual(s["overall"], "HOLD")

    def test_duplicate_inventory_row(self):
        with h.TempDir() as tmp:
            files = self.with_lines(tmp, SO_1043, "inventory", lambda l: l + [l[1]])
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "DUPLICATE_INVENTORY_TAG")
        self.assertTrue(any(f"duplicate tag {tag('201')}" in p for p in s["input_problems"]))
        self.assertEqual(s["overall"], "HOLD")

    def test_duplicate_order_row_is_reported_and_holds(self):
        # Order GEL-35 x24 entered twice (48) and a manifest that ships 48: the totals agree, but
        # a copy-paste duplicate on the order must not slip through as GO.
        with h.TempDir() as tmp:
            files = self.with_lines(tmp, SO_1043, "order", lambda l: l + [l[1]])
            files = self.mutated(tmp, files, "manifest", 0, "Quantity", "48")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertEqual(self.line(lines, 2)["order_qty"], "48.0")
        self.assertEqual(s["overall"], "HOLD")
        self.assertTrue(any("gel-35 is on 2 rows (2, 4)" in p for p in s["input_problems"]), s["input_problems"])

    def test_blank_manifest_tag(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "Package Tag", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "BLANK_TAG")
        self.assertIn("manifest row 2, column 'Package Tag': blank package tag; line held as BLANK_TAG",
                      s["input_problems"])
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_manifest_quantity(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "Quantity", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "BAD_QUANTITY")
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_manifest_unit(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "UoM", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "MISSING_UNIT")
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_inventory_quantity(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "inventory", 0, "Quantity", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "INVENTORY_QTY_UNREADABLE")
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_inventory_lab_status(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "inventory", 0, "Lab Testing State", "")
            lines, s = self.precheck(tmp, files, "--passing-lab-values", "TestPassed", "")
        self.assertHeld(self.line(lines, 2), "LAB_NOT_PASSED")
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_inventory_item(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "inventory", 0, "Item", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "ITEM_MISSING")
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_order_quantity(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "order", 0, "Qty", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "ORDER_QTY_UNREADABLE")
        self.assertEqual(s["overall"], "HOLD")

    def test_blank_order_key(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "order", 0, "SKU", "")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "NOT_ON_ORDER")
        self.assertIn("order row 2: blank sku", s["input_problems"])

    def test_unknown_manifest_unit(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "UoM", "Boxes")
            lines, s = self.precheck(tmp, files, *PASSED)
        l = self.line(lines, 2)
        self.assertHeld(l, "MANIFEST_VS_INVENTORY_UNKNOWN_UOM")
        self.assertHeld(l, "ORDER_VS_MANIFEST_UOM_MISMATCH")

    def test_unknown_unit_everywhere_still_holds(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "UoM", "Boxes")
            files = self.mutated(tmp, files, "inventory", 0, "UoM", "Boxes")
            files = self.mutated(tmp, files, "order", 0, "Unit", "Boxes")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "MANIFEST_VS_INVENTORY_UNKNOWN_UOM")
        self.assertEqual(s["overall"], "HOLD")

    def test_weight_vs_each(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "UoM", "Grams")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "MANIFEST_VS_INVENTORY_UOM_MISMATCH")

    def test_mixed_units_on_one_order_line(self):
        with h.TempDir() as tmp:
            files = self.with_lines(tmp, SO_1043, "order",
                                    lambda l: l + ["SO-1043,Example Harbor Wellness,GEL-35,Gelato 3.5g Jar,5,g"])
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "ORDER_QTY_UNREADABLE")
        self.assertIn("order: mixed units for gel-35", s["input_problems"])

    def test_scientific_notation_tag_on_manifest(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "Package Tag", "1.23457E+23")
            lines, s = self.precheck(tmp, files, *PASSED)
        l = self.line(lines, 2)
        self.assertHeld(l, "TAG_SCIENTIFIC_NOTATION")
        self.assertIn("scientific notation", l["notes"])
        self.assertTrue(any("manifest row 2, column 'Package Tag', value '1.23457E+23'" in p
                            for p in s["input_problems"]))
        self.assertEqual(s["overall"], "HOLD")

    def test_scientific_notation_tag_mangled_the_same_in_every_file_never_goes(self):
        # Manifest and inventory both exported through Excel: the mangled tags agree with each
        # other, so before the fix this line matched and shipped as GO.
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "manifest", 0, "Package Tag", "1.23457E+23")
            files = self.mutated(tmp, files, "inventory", 0, "Tag", "1.23457E+23")
            lines, s = self.precheck(tmp, files, *PASSED)
        l = self.line(lines, 2)
        self.assertHeld(l, "TAG_SCIENTIFIC_NOTATION")
        self.assertHeld(l, "NOT_IN_ACTIVE_INVENTORY")
        self.assertTrue(any("inventory row 2, column 'Tag', value '1.23457E+23'" in p
                            for p in s["input_problems"]))
        self.assertEqual(s["overall"], "HOLD")

    def test_scientific_notation_tag_on_order(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1042, "order", 0, "Package Tag", "1.23457E+23")
            files = self.mutated(tmp, files, "manifest", 0, "Package Label", "1.23457E+23")
            files = self.mutated(tmp, files, "inventory", 0, "Tag", "1.23457E+23")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "TAG_SCIENTIFIC_NOTATION")
        self.assertTrue(any("order row 2, column 'Package Tag', value '1.23457E+23'" in p
                            for p in s["input_problems"]))

    def test_scientific_notation_tag_only_on_order(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1042, "order", 0, "Package Tag", "1.23457E+23")
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertHeld(self.line(lines, 2), "NOT_ON_ORDER")
        order_lines = [l for l in lines if l["source"] == "order" and l["item"] == "1.23457E+23"]
        self.assertEqual(len(order_lines), 1)
        self.assertEqual(order_lines[0]["flags"], "ON_ORDER_NOT_ON_MANIFEST;TAG_SCIENTIFIC_NOTATION")


# --------------------------------------------------------------------------------------------
# 4. Formula injection: no written cell may run as a spreadsheet formula.
# --------------------------------------------------------------------------------------------
class FormulaInjection(PrecheckCase):

    TEXT_COLUMNS = [  # (fixture set, file, column)
        (SO_1043, "manifest", "Item"), (SO_1043, "manifest", "Package Tag"), (SO_1043, "manifest", "SKU"),
        (SO_1043, "manifest", "UoM"),
        (SO_1043, "inventory", "Item"), (SO_1043, "inventory", "Tag"), (SO_1043, "inventory", "UoM"),
        (SO_1043, "inventory", "Lab Testing State"),
        (SO_1043, "order", "SKU"), (SO_1043, "order", "Unit"),
        (SO_1042, "order", "Package Tag"), (SO_1042, "order", "Product Name"),
        (SO_1042, "manifest", "Package Label"),
    ]

    def test_formula_cells_are_neutralised(self):
        for files, role, column in self.TEXT_COLUMNS:
            for value in h.FORMULA_CELLS:
                with self.subTest(file=role, column=column, value=value), h.TempDir() as tmp:
                    _, s = self.precheck(tmp, self.mutated(tmp, files, role, 0, column, value), *PASSED)
                    h.assert_no_live_formulas(self, tmp / "out")
                    self.assertEqual(s["overall"], "HOLD")

    def test_lab_value_that_looks_like_a_formula(self):
        with h.TempDir() as tmp:
            files = self.mutated(tmp, SO_1043, "inventory", 0, "Lab Testing State", "=1+1")
            lines, _ = self.precheck(tmp, files, *PASSED)
            h.assert_no_live_formulas(self, tmp / "out")
        self.assertEqual(self.line(lines, 2)["lab_status"], "'=1+1")


# --------------------------------------------------------------------------------------------
# 5. Determinism.
# --------------------------------------------------------------------------------------------
class Determinism(PrecheckCase):

    def check_identical(self, files):
        with h.TempDir() as tmp:
            for d in ("a", "b"):
                proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / d, *PASSED])
                self.assertEqual(proc.returncode, 0, proc.stderr)
            for name in OUTPUTS:
                self.assertTrue(filecmp.cmp(tmp / "a" / name, tmp / "b" / name, shallow=False), name)

    def test_main_fixture_is_byte_identical(self):
        self.check_identical(SO_1042)

    def test_regression_fixture_is_byte_identical(self):
        self.check_identical(SO_3061)


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


class SkillMdCommand(PrecheckCase):

    def test_commands_found(self):
        self.assertGreaterEqual(len(h.skill_md_run_commands(NAME)), 2)

    def test_every_required_option_is_documented(self):
        required = h.required_options(NAME)
        self.assertEqual(required, ["--inventory", "--manifest", "--order"])
        cmds = h.skill_md_run_commands(NAME)
        for opt in required:
            with self.subTest(option=opt):
                for c in cmds:  # every documented command needs all three files
                    self.assertRegex(c, re.escape(opt) + r"(?![\w-])")

    def test_run_command_confirms_lab_values(self):
        runs = [c for c in h.skill_md_run_commands(NAME) if "--detect-only" not in c]
        self.assertTrue(runs)
        for c in runs:  # without it every line holds as LAB_STATUS_UNCONFIRMED
            self.assertIn("--passing-lab-values", c)

    def test_documented_commands_run(self):
        for cmd in h.skill_md_run_commands(NAME):
            with self.subTest(cmd=cmd), h.TempDir() as tmp:
                out = tmp / "out"
                values = {"--order": SO_1042[0], "--manifest": SO_1042[1], "--inventory": SO_1042[2],
                          "--passing-lab-values": "TestPassed", "--out-dir": out}
                args = fill_placeholders(cmd, values)
                proc = self.run_script(args, cwd=tmp)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                stdout = h.strict_json_load(proc.stdout, is_text=True)
                if "--detect-only" in args:
                    self.assertIn("distinct_lab_status_values", stdout)
                    self.assertEqual(list(tmp.iterdir()), [])
                    continue
                self.assertIn("--out-dir", args, "run command must name the output folder")
                self.assertEqual([p.name for p in tmp.iterdir()], ["out"], "wrote outside --out-dir")
                for name in OUTPUTS:
                    self.assertTrue((out / name).is_file(), name)
                s = h.strict_json_load(out / "precheck_summary.json")
                self.assertEqual((s["overall"], s["lines_go"], s["lines_hold"]), ("HOLD", 1, 8))
                self.assertEqual(s["passing_lab_values_used"], ["testpassed"])


# --------------------------------------------------------------------------------------------
# 7. No traceback, even on the worst input.
# --------------------------------------------------------------------------------------------
class NoTraceback(PrecheckCase):

    def test_help(self):
        self.assertEqual(self.run_script(["--help"]).returncode, 0)

    def test_no_arguments(self):
        self.assertEqual(self.run_script([]).returncode, 2)

    def test_binary_garbage(self):
        with h.TempDir() as tmp:
            (tmp / "manifest.csv").write_bytes(b"\x00\xff\xfe\x00garbage\x00\n\x00")
            files = (SO_1043[0], tmp / "manifest.csv", SO_1043[2])
            proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
            self.assertCleanFailure(proc, tmp)

    def test_directory_as_input(self):
        with h.TempDir() as tmp:
            files = (SO_1043[0], SO_1043[1], tmp)
            proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
            self.assertCleanFailure(proc, tmp, "Cannot read")

    def test_out_dir_is_a_file(self):
        with h.TempDir() as tmp:
            (tmp / "out").write_text("x")
            proc = self.run_script(self.files_args(SO_1043) + ["--out-dir", tmp / "out", *PASSED])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("--out-dir", proc.stderr)
            self.assertNotIn('"overall": "GO"', proc.stdout)

    def test_no_shared_join_key(self):
        with h.TempDir() as tmp:
            files = self.with_lines(tmp, SO_1043, "order",
                                    lambda l: ["Order #,Customer,Code,Name,Qty,Unit"] + l[1:])
            proc = self.run_script(self.files_args(files) + ["--out-dir", tmp / "out", *PASSED])
            self.assertCleanFailure(proc, tmp, "No shared key")

    def test_ragged_rows(self):
        with h.TempDir() as tmp:
            files = self.with_lines(tmp, SO_1043, "manifest",
                                    lambda l: [l[0], l[1].split(",")[0], l[2] + ",extra"])
            lines, s = self.precheck(tmp, files, *PASSED)
        self.assertEqual(self.line(lines, 2)["result"], "HOLD")
        self.assertEqual(s["overall"], "HOLD")


if __name__ == "__main__":
    unittest.main()
