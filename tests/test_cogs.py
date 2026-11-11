"""Gate 2 script tests for cannabis-batch-cogs/scripts/cogs.py.

Run: python3 -m unittest discover -s tests -t . -v
"""
import csv
import re
import shlex
import unittest
from pathlib import Path

from tests import helpers as h

NAME = "cogs"
FILES = h.skill_dir(NAME) / "evals" / "files"
CART = FILES / "bom_distillate_cart_batch.csv"
RESIN = FILES / "bom_live_resin_run.csv"
OUTPUTS = ("cogs_lines.csv", "summary.json")

# Eval 1 (cart batch): the operator gave every number.
EVAL1_FLAGS = {"--units-produced": "492", "--expected-units": "500", "--labor-hours": "14", "--labor-rate": "24",
               "--overhead-per-labor-hour": "35", "--testing-cost": "425"}
# Eval 2 (live resin): overhead as % of materials, solvent cost assumed.
EVAL2_ARGS = ["--units-produced", "1180", "--labor-hours", "30", "--labor-rate", "26",
              "--overhead-pct-materials", "12", "--testing-cost", "600",
              "--assume", "cost:Butane/propane solvent blend=10"]

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


def flag_args(flags):
    return [f"{k}={v}" for k, v in flags.items()]


def eval1_args(bom=CART, **override):
    flags = dict(EVAL1_FLAGS)
    flags.update(override)
    return ["--bom", bom] + flag_args(flags)


class CogsCase(unittest.TestCase):
    """Every run goes through run(): stderr must never hold a traceback."""

    def run_cogs(self, args):
        res = h.run(NAME, args)
        self.assertNotIn("Traceback", res.stderr, res.stderr)
        return res

    def run_ok(self, args):
        res = self.run_cogs(args)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        return h.strict_json_load(res.stdout, is_text=True)

    def run_blocked(self, args):
        res = self.run_cogs(args)
        self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
        out = h.strict_json_load(res.stdout, is_text=True)
        self.assertEqual(out["status"], "BLOCKED")
        return out

    def assert_no_outputs(self, out_dir):
        for name in OUTPUTS:
            self.assertFalse((Path(out_dir) / name).exists(), f"{name} written for a BLOCKED batch")

    def write_bom(self, path, rows, header=("Component", "Qty", "UoM", "Unit Cost", "Cost UoM")):
        h.write_csv(path, list(header), rows)
        return path

    def cart_rows(self):
        with open(CART, newline="") as f:
            return list(csv.reader(f))[1:]


class KnownAnswers(CogsCase):
    def test_eval1_cart_batch_totals(self):
        with h.TempDir() as d:
            out = self.run_ok(eval1_args() + ["--out-dir", d])
            self.assertEqual(h.strict_json_load(d / "summary.json"), out)
            self.assertEqual(out["status"], "OK")
            self.assertEqual(out["materials"], 3429.75)
            self.assertEqual(out["labor"], 336.0)
            self.assertEqual(out["overhead"], 490.0)
            self.assertEqual(out["testing"], 425.0)
            self.assertEqual(out["total_batch_cost"], 4680.75)
            self.assertEqual(out["cost_per_unit"], 9.5137)
            self.assertEqual(out["yield_variance"], {
                "expected_units": 500.0, "actual_units": 492.0, "variance_units": -8.0, "variance_pct": -1.6,
                "cost_per_unit_at_expected": 9.3615, "cost_of_shortfall_per_unit": 0.1522})
            self.assertEqual(out["assumptions"], [])
            self.assertEqual(out["input_problems"], [])
            self.assertEqual(out["lines_tagged_assumption"], [])

    def test_eval1_cart_batch_lines_and_sensitivity(self):
        with h.TempDir() as d:
            out = self.run_ok(eval1_args() + ["--out-dir", d])
            lines = {r["line"]: r for r in h.read_csv(d / "cogs_lines.csv")}
            dist = lines["Distillate - bulk (lot D-0921)"]
            self.assertEqual((dist["line_cost"], dist["cost_per_unit"], dist["pct_of_total"]),
                             ("2146.25", "4.3623", "45.85"))
            self.assertEqual(lines["510 cartridge hardware 1.0 mL"]["line_cost"], "943.5")
            self.assertEqual(lines["Direct labor"]["line_cost"], "336.0")
            self.assertEqual(lines["Overhead (35.0/labor hour x 14.0 h)"]["line_cost"], "490.0")
            self.assertEqual(lines["Testing"]["line_cost"], "425.0")
            self.assertEqual([s["driver"] for s in out["sensitivity"]],
                             ["Distillate - bulk (lot D-0921)", "510 cartridge hardware 1.0 mL",
                              "Overhead (35.0/labor hour x 14.0 h)"])
            self.assertEqual(out["sensitivity"][0], {
                "driver": "Distillate - bulk (lot D-0921)", "base_line_cost": 2146.25,
                "cost_per_unit_-20%": 8.6413, "cost_per_unit_-10%": 9.0775,
                "cost_per_unit_+10%": 9.9499, "cost_per_unit_+20%": 10.3862})

    def test_eval2_live_resin_converts_kg_to_lb_and_tags_assumption(self):
        with h.TempDir() as d:
            out = self.run_ok(["--bom", RESIN] + EVAL2_ARGS + ["--out-dir", d])
            self.assertEqual(out["materials"], 10351.77)
            self.assertEqual(out["labor"], 780.0)
            self.assertEqual(out["overhead"], 1242.21)
            self.assertEqual(out["testing"], 600.0)
            self.assertEqual(out["total_batch_cost"], 12973.98)
            self.assertEqual(out["cost_per_unit"], 10.9949)
            self.assertEqual(out["assumptions"], [
                "unit cost of Butane/propane solvent blend = 10.0 per kg [ASSUMPTION]",
                "overhead line is an ASSUMPTION because it is % of materials that include assumed values: "
                "Butane/propane solvent blend"])
            self.assertEqual(out["lines_tagged_assumption"],
                             ["Butane/propane solvent blend", "Overhead (12.0% of materials)"])
            lines = {r["line"]: r for r in h.read_csv(d / "cogs_lines.csv")}
            biomass = lines["Fresh frozen biomass - Papaya (harvest PAP-F4-0927)"]
            self.assertEqual((biomass["qty_in_cost_uom"], biomass["line_cost"]), ("100.001764", "9500.1676"))
            self.assertEqual(lines["Butane/propane solvent blend"]["source"], "ASSUMPTION")

    def test_eval3_preroll_thin_inputs_blocked(self):
        with h.TempDir() as d:
            out = self.run_blocked(["--bom", FILES / "bom_preroll_mixed_units.csv", "--out-dir", d])
            self.assertEqual(out["missing_inputs"], [
                "units_produced", "labor_hours", "labor_rate", "testing_cost",
                "one of overhead_per_batch/overhead_per_labor_hour/overhead_pct_materials "
                "(pass 0 if the operator confirms no overhead)",
                "cost:Flower - Blue Dream smalls (BD-F1-1004)"])
            self.assertEqual(out["input_problems"], [])
            self.assert_no_outputs(d)

    def test_eval4_blank_cost_unit_blank_rows_negative_qty_blocked(self):
        with h.TempDir() as d:
            out = self.run_blocked(["--bom", FILES / "bom_regression_cost_units.csv", "--units-produced", "800",
                                    "--labor-hours", "20", "--labor-rate", "25", "--overhead-pct-materials", "10",
                                    "--testing-cost", "400", "--assume", "cost:Example solvent blend=12",
                                    "--out-dir", d])
            self.assertEqual(out["missing_inputs"], [
                "cost_uom:Example Farms fresh frozen biomass (lot EX-0101) (row 2): price per what unit? Quantity "
                "is in 'kg' but the cost unit is blank. Add it to the BOM (e.g. g, lb, kg, ml)."])
            self.assertEqual(out["input_problems"], [
                "row 6 (Labels returned to stock): column 'Qty' value '-20': negative quantity. A BOM line is the "
                "quantity consumed; net a return or correction into the line it corrects, or confirm the right "
                "figure",
                "Skipped 2 fully blank row(s) in the BOM.",
                "Cost unit blank on 1 count line(s), so the price was read as per each: row 4 (Jars 1g glass + CR "
                "lid). Check none is priced per case or pack."])
            self.assert_no_outputs(d)

    def test_eval5_unreadable_and_negative_numbers_blocked(self):
        with h.TempDir() as d:
            out = self.run_blocked(["--bom", FILES / "bom_regression_bad_numbers.csv", "--units-produced", "500",
                                    "--labor-hours", "12", "--labor-rate", "25", "--overhead-per-labor-hour", "30",
                                    "--testing-cost", "400", "--out-dir", d])
            probs = out["input_problems"]
            self.assertEqual(len(probs), 5, probs)
            for row, col, raw in ((2, "Unit Cost", "4,25"), (3, "Qty", "NaN"), (4, "Unit Cost", "inf"),
                                  (5, "Qty", "-500"), (6, "Unit Cost", "1.234,56")):
                with self.subTest(row=row):
                    self.assertTrue(any(p.startswith(f"row {row} ") and f"column '{col}' value '{raw}'" in p
                                        for p in probs), probs)
            self.assertFalse(any("1,200" in p for p in probs), "US thousands '1,200' must be read, not flagged")
            self.assert_no_outputs(d)


class BadNumbers(CogsCase):
    def check_bom_column(self, column):
        for label, raw in h.BAD_NUMBERS.items():
            with self.subTest(column=column, value=label), h.TempDir() as d:
                bom = h.mutate_csv(CART, d / "bom.csv", 0, column, raw)
                out = self.run_blocked(eval1_args(bom) + ["--out-dir", d / "out"])
                self.assertTrue(any(p.startswith("row 2 ") and f"column '{column}' value '{raw}'" in p
                                    for p in out["input_problems"]), out["input_problems"])
                self.assertNotIn("total_batch_cost", out)
                self.assert_no_outputs(d / "out")

    def test_bom_qty_bad_numbers_block_the_batch(self):
        self.check_bom_column("Qty")

    def test_bom_unit_cost_bad_numbers_block_the_batch(self):
        self.check_bom_column("Unit Cost")

    def test_cli_numeric_flags_reject_bad_numbers(self):
        flags = list(EVAL1_FLAGS) + ["--overhead-per-batch", "--overhead-pct-materials"]
        for flag in flags:
            for label, raw in h.BAD_NUMBERS.items():
                with self.subTest(flag=flag, value=label), h.TempDir() as d:
                    over = dict(EVAL1_FLAGS)
                    if flag in ("--overhead-per-batch", "--overhead-pct-materials"):
                        del over["--overhead-per-labor-hour"]
                    over[flag] = raw
                    res = self.run_cogs(["--bom", CART] + flag_args(over) + ["--out-dir", d / "out"])
                    self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
                    self.assertIn(f"argument {flag}", res.stderr)
                    self.assertIn(raw, res.stderr)
                    self.assertFalse((d / "out").exists())

    def test_assumed_values_reject_bad_numbers(self):
        for label, raw in h.BAD_NUMBERS.items():
            with self.subTest(value=label), h.TempDir() as d:
                args = EVAL2_ARGS[:-1] + [f"cost:Butane/propane solvent blend={raw}"]
                res = self.run_cogs(["--bom", RESIN] + args + ["--out-dir", d / "out"])
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("Bad --assume cost:Butane/propane solvent blend", res.stderr)
                self.assertIn(raw, res.stderr)
                self.assertFalse((d / "out").exists())

    def test_us_thousands_separator_is_read(self):
        with h.TempDir() as d:
            bom = h.mutate_csv(CART, d / "bom.csv", 2, "Qty", "1,020")  # 510 -> 1,020 cartridges
            out = self.run_ok(eval1_args(bom) + ["--out-dir", d / "out"])
            self.assertEqual(out["materials"], round(3429.75 + 510 * 1.85, 2))


class Structure(CogsCase):
    def test_empty_file_exits_with_message(self):
        with h.TempDir() as d:
            (d / "bom.csv").write_text("")
            res = self.run_cogs(eval1_args(d / "bom.csv") + ["--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("empty", res.stderr)

    def test_missing_file_exits_with_message(self):
        with h.TempDir() as d:
            res = self.run_cogs(eval1_args(d / "nope.csv") + ["--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("Cannot read", res.stderr)

    def test_header_only_is_blocked(self):
        with h.TempDir() as d:
            out = self.run_blocked(eval1_args(self.write_bom(d / "bom.csv", [])) + ["--out-dir", d / "out"])
            self.assertTrue(any("no component rows" in p for p in out["input_problems"]), out)
            self.assert_no_outputs(d / "out")

    def test_only_blank_rows_is_blocked(self):
        with h.TempDir() as d:
            bom = self.write_bom(d / "bom.csv", [["", "", "", "", ""]] * 3)
            out = self.run_blocked(eval1_args(bom) + ["--out-dir", d / "out"])
            self.assertTrue(any("no component rows" in p for p in out["input_problems"]), out)

    def test_duplicate_row_is_costed_and_noted(self):
        with h.TempDir() as d:
            rows = self.cart_rows()
            bom = self.write_bom(d / "bom.csv", rows + [rows[0]])
            out = self.run_ok(eval1_args(bom) + ["--out-dir", d / "out"])
            self.assertEqual(out["materials"], 3429.75 + 2146.25)
            self.assertIn("row 8 repeats row 2 exactly; both lines were costed. If one is a double entry, remove "
                          "it and rerun.", out["input_problems"])

    def test_blank_component_name_is_costed_and_noted(self):
        with h.TempDir() as d:
            bom = h.mutate_csv(CART, d / "bom.csv", 0, "Component", "")
            out = self.run_ok(eval1_args(bom) + ["--out-dir", d / "out"])
            self.assertEqual(out["total_batch_cost"], 4680.75)
            self.assertTrue(any(p.startswith("row 2: column 'Component' is blank") for p in out["input_problems"]))
            self.assertIn("row2", [r["line"] for r in h.read_csv(d / "out" / "cogs_lines.csv")])

    def test_blank_required_cells_block_the_batch(self):
        expect = {"Qty": "row 2 (Distillate - bulk (lot D-0921)): quantity missing",
                  "UoM": "row 2 (Distillate - bulk (lot D-0921)): unknown unit '' or cost unit 'g'"}
        for column, problem in expect.items():
            with self.subTest(column=column), h.TempDir() as d:
                out = self.run_blocked(eval1_args(h.mutate_csv(CART, d / "bom.csv", 0, column, ""))
                                       + ["--out-dir", d / "out"])
                self.assertIn(problem, out["input_problems"])
        with self.subTest(column="Unit Cost"), h.TempDir() as d:
            out = self.run_blocked(eval1_args(h.mutate_csv(CART, d / "bom.csv", 0, "Unit Cost", ""))
                                   + ["--out-dir", d / "out"])
            self.assertEqual(out["missing_inputs"], ["cost:Distillate - bulk (lot D-0921)"])

    def test_blank_cost_unit_on_weight_line_asks_price_per_what(self):
        with h.TempDir() as d:
            out = self.run_blocked(eval1_args(h.mutate_csv(CART, d / "bom.csv", 0, "Cost UoM", ""))
                                   + ["--out-dir", d / "out"])
            self.assertTrue(out["missing_inputs"][0].startswith("cost_uom:Distillate - bulk (lot D-0921) (row 2)"))

    def test_mixed_unit_kinds_are_blocked(self):
        with h.TempDir() as d:
            out = self.run_blocked(eval1_args(h.mutate_csv(CART, d / "bom.csv", 0, "UoM", "ml"))
                                   + ["--out-dir", d / "out"])
            self.assertIn("row 2 (Distillate - bulk (lot D-0921)): qty unit 'ml' and cost unit 'g' are different "
                          "kinds (weight/volume/each); give the conversion", out["input_problems"])

    def test_unknown_unit_is_blocked(self):
        with h.TempDir() as d:
            out = self.run_blocked(eval1_args(h.mutate_csv(CART, d / "bom.csv", 0, "UoM", "grams-ish"))
                                   + ["--out-dir", d / "out"])
            self.assertIn("row 2 (Distillate - bulk (lot D-0921)): unknown unit 'grams-ish' or cost unit 'g'",
                          out["input_problems"])

    def test_cost_unit_written_as_price_per_is_read(self):
        with h.TempDir() as d:
            out = self.run_ok(eval1_args(h.mutate_csv(CART, d / "bom.csv", 0, "Cost UoM", "$/g"))
                              + ["--out-dir", d / "out"])
            self.assertEqual(out["total_batch_cost"], 4680.75)

    def test_ambiguous_cost_column_exits_with_message(self):
        with h.TempDir() as d:
            bom = self.write_bom(d / "bom.csv", [r + [r[3]] for r in self.cart_rows()],
                                 header=("Component", "Qty", "UoM", "Unit Cost", "Cost UoM", "Price"))
            res = self.run_cogs(eval1_args(bom) + ["--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("Cannot identify BOM column 'unit_cost'", res.stderr)
            self.assertIn("--map unit_cost=", res.stderr)


class FormulaInjection(CogsCase):
    def test_component_name_formulas_are_neutralised(self):
        for cell in h.FORMULA_CELLS:
            with self.subTest(cell=cell), h.TempDir() as d:
                bom = h.mutate_csv(CART, d / "bom.csv", 0, "Component", cell)
                out = self.run_ok(eval1_args(bom) + ["--out-dir", d / "out"])
                self.assertEqual(out["total_batch_cost"], 4680.75)
                h.assert_no_live_formulas(self, d / "out")
                self.assertIn("'" + cell, [r["line"] for r in h.read_csv(d / "out" / "cogs_lines.csv")])

    def test_csv_safe_matches_shared_text(self):
        self.assertIn("\n\n\n" + CSV_SAFE_TEXT, h.script_path(NAME).read_text())


class Determinism(CogsCase):
    def test_same_inputs_give_byte_identical_outputs(self):
        for label, args in (("eval1", eval1_args()), ("eval2", ["--bom", RESIN] + EVAL2_ARGS)):
            with self.subTest(run=label), h.TempDir() as d:
                first = self.run_ok(args + ["--out-dir", d / "a"])
                second = self.run_ok(args + ["--out-dir", d / "b"])
                self.assertEqual(first, second)
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


class SkillMdCommand(CogsCase):
    def test_required_options_are_documented(self):
        cmds = h.skill_md_run_commands(NAME)
        self.assertTrue(cmds)
        for opt in h.required_options(NAME):
            with self.subTest(option=opt):
                self.assertTrue(any(re.search(r"(?<![\w-])" + re.escape(opt) + r"(?![\w-])", c) for c in cmds),
                                f"{opt} is required but no SKILL.md command shows it")

    def test_documented_commands_run_and_write_documented_outputs(self):
        skill_md = (h.skill_dir(NAME) / "SKILL.md").read_text()
        for cmd in h.skill_md_run_commands(NAME):
            with self.subTest(cmd=cmd), h.TempDir() as d:
                values = {"--bom": CART, "--batch-name": "GEL-CART-1003", "--out-dir": d / "out"}
                values.update(EVAL1_FLAGS)
                argv = documented_args(cmd, skill_md, values)
                res = self.run_cogs(argv)
                self.assertEqual(res.returncode, 0, f"{shlex.join(map(str, argv))}\n{res.stdout}{res.stderr}")
                out = h.strict_json_load(res.stdout, is_text=True)
                if "--detect-only" in argv:
                    self.assertEqual(out["mapping"]["unit_cost"], "Unit Cost")
                    continue
                for name in OUTPUTS:
                    self.assertTrue((d / "out" / name).exists(), name)
                # The documented command must not pick up a silent default that changes the answer.
                self.assertEqual(out["total_batch_cost"], 4680.75)
                self.assertEqual(out["cost_per_unit"], 9.5137)


class NoTraceback(CogsCase):
    def test_odd_invocations_never_traceback(self):
        cases = [[], ["--bom"], ["--bom", CART, "--detect-only"], ["--bom", CART, "--map", "qty"],
                 ["--bom", CART, "--assume", "nonsense"],
                 eval1_args() + ["--overhead-per-batch", "5"]]
        for args in cases:
            with self.subTest(args=args), h.TempDir() as d:
                res = self.run_cogs(args + ["--out-dir", d / "out"])
                self.assertIn(res.returncode, (0, 1, 2))
                self.assertNotIn("Traceback", res.stdout)

    def test_non_utf8_file_exits_with_message(self):
        with h.TempDir() as d:
            (d / "bom.csv").write_bytes("Component,Qty\n\xe9\xff\xfe,1\n".encode("latin-1"))
            res = self.run_cogs(eval1_args(d / "bom.csv") + ["--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("UTF-8", res.stderr)


if __name__ == "__main__":
    unittest.main()
