"""Gate 2 script tests for cannabis-harvest-yield-analysis/scripts/yield.py.

Run: python3 -m unittest discover -s tests -t . -v
"""
import csv
import json
import re
import shlex
import unittest

from tests import helpers as h

NAME = "yield"
FILES = h.skill_dir(NAME) / "evals" / "files"
Q3 = FILES / "harvests_2026_q3.csv"
NO_UNITS = FILES / "harvest_log_no_units.csv"
GAPS = FILES / "harvests_regression_gaps.csv"
BAD = FILES / "harvests_regression_bad_numbers.csv"
OUTPUTS = ("yield_by_batch.csv", "summary.json")
BATCH_FIELDS = ["harvest_id", "strain", "room", "harvest_date", "source_unit", "wet_g", "dry_g", "dry_down_pct",
                "dry_g_per_plant", "dry_g_per_sqft", "dry_g_per_light", "flower_a_pct", "flower_b_pct", "trim_pct",
                "waste_pct", "breakdown_total_g", "unaccounted_g", "sum_check", "cost_per_dry_g",
                "cost_per_flower_g", "flags", "excluded_from"]

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


class YieldCase(unittest.TestCase):
    """Every run goes through run_yield(): stderr must never hold a traceback."""

    def run_yield(self, args):
        res = h.run(NAME, args)
        self.assertNotIn("Traceback", res.stderr, res.stderr)
        return res

    def run_ok(self, harvests, out_dir, *extra):
        res = self.run_yield(["--harvests", harvests, "--out-dir", out_dir] + list(extra))
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        out = h.strict_json_load(res.stdout, is_text=True)
        self.assertEqual(h.strict_json_load(out_dir / "summary.json"), out)
        return out, {r["harvest_id"]: r for r in h.read_csv(out_dir / "yield_by_batch.csv")}

    def q3_rows(self):
        with open(Q3, newline="") as f:
            rows = list(csv.reader(f))
        return rows[0], rows[1:]

    @staticmethod
    def group(out, key, name):
        field = "by_room_ranked_by_g_per_sqft" if key == "room" else "by_strain_ranked_by_g_per_sqft"
        return next(g for g in out[field] if g[key] == name)


class KnownAnswers(YieldCase):
    def test_every_eval_with_files_is_covered(self):
        evals = json.loads((h.skill_dir(NAME) / "evals" / "evals.json").read_text())["evals"]
        self.assertEqual({e["id"] for e in evals if e["files"]}, {1, 2, 4, 5})

    def test_eval1_q3_rooms_ranked_by_g_per_sqft(self):
        with h.TempDir() as d:
            out, _ = self.run_ok(Q3, d)
            ranked = [(g["room"], g["dry_g_per_sqft"]) for g in out["by_room_ranked_by_g_per_sqft"]]
            self.assertEqual(ranked, [("Flower 1", 28.34), ("Flower 2", 25.48), ("Flower 3", 24.29),
                                      ("Flower 4", 15.25)])
            f1 = self.group(out, "room", "Flower 1")
            self.assertEqual((f1["batches"], f1["dry_g"], f1["dry_down_pct"], f1["dry_g_per_plant"],
                              f1["dry_g_per_light"]), (3, 40805.2, 78.07, 141.68, 283.37))
            self.assertEqual(f1["coverage"]["dry_g_per_sqft"], "3 of 3 batches")

    def test_eval1_q3_totals_and_pound_batch(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(Q3, d)
            self.assertEqual((out["batches"], out["total_wet_g"], out["total_dry_g"], out["total_dry_lb"],
                              out["overall_dry_down_pct"]), (8, 412276.08, 89584.2, 197.5, 78.27))
            self.assertEqual(out["totals_coverage"], {"total_wet_g": "8 of 8 batches",
                                                      "total_dry_g": "8 of 8 batches",
                                                      "overall_dry_down_pct": "8 of 8 batches"})
            bd = batches["BD-F1-0906"]
            self.assertEqual((bd["source_unit"], bd["wet_g"], bd["dry_g"], bd["dry_down_pct"], bd["sum_check"]),
                             ("lb", "63276.08", "13789.2", "78.21", "OK"))
            self.assertEqual(out["input_problems"], [])
            self.assertEqual(out["duplicate_harvest_ids"], [])

    def test_eval1_q3_unaccounted_weight_cost_and_anomalies(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(Q3, d)
            unaccounted = {k: (b["sum_check"], b["unaccounted_g"]) for k, b in batches.items()
                           if b["sum_check"] != "OK"}
            self.assertEqual(unaccounted, {"GMO-F2-0913": ("UNACCOUNTED", "400.0"),
                                           "GEL-F3-0920": ("UNACCOUNTED", "125.0"),
                                           "PAP-F4-0927": ("UNACCOUNTED", "200.0"),
                                           "BD-F1-1004": ("UNACCOUNTED", "200.0")})
            self.assertEqual(batches["PAP-F4-0927"]["cost_per_dry_g"], "2.7049")
            self.assertEqual(batches["BD-F1-0712"]["cost_per_dry_g"], "1.3563")
            self.assertEqual(out["flagged_batches"], [
                {"harvest_id": "GEL-F3-0726", "flags": "dry_down_pct:LOW;"},
                {"harvest_id": "GMO-F2-0913", "flags": "UNACCOUNTED:400.0g;"},
                {"harvest_id": "GEL-F3-0920", "flags": "dry_down_pct:LOW;UNACCOUNTED:125.0g;"},
                {"harvest_id": "PAP-F4-0927", "flags": "dry_down_pct:HIGH;dry_g_per_plant:LOW;dry_g_per_sqft:LOW;"
                                                       "dry_g_per_light:LOW;trim_pct:HIGH;cost_per_dry_g:HIGH;"
                                                       "UNACCOUNTED:200.0g;"},
                {"harvest_id": "BD-F1-1004", "flags": "UNACCOUNTED:200.0g;"}])
            self.assertEqual(out["anomaly_fences"]["dry_g_per_sqft"], [19.1262, 33.3363])
            self.assertIn("1.5*IQR", out["anomaly_rule"])

    def test_eval2_no_unit_column_requires_weight_unit(self):
        with h.TempDir() as d:
            res = self.run_yield(["--harvests", NO_UNITS, "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("--weight-unit", res.stderr)
            self.assertFalse((d / "out").exists())

    def test_eval2_with_weight_unit_gives_per_plant_only(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(NO_UNITS, d, "--weight-unit", "lb")
            room_a, room_b = self.group(out, "room", "Room A"), self.group(out, "room", "Room B")
            self.assertEqual((room_a["dry_g_per_plant"], room_b["dry_g_per_plant"]), (252.78, 215.46))
            self.assertIsNone(room_a["dry_g_per_sqft"])
            self.assertEqual(room_a["coverage"]["dry_g_per_sqft"], "not computed: no canopy_sqft column")
            self.assertTrue(all(v is None for v in out["anomaly_fences"].values()), "3 batches: no fences")
            self.assertEqual(out["total_dry_g"], 32885.42)

    def test_eval4_gaps_zero_dry_and_duplicates(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(GAPS, d, "--weight-unit", "lb")
            r1, r2 = self.group(out, "room", "Room 1"), self.group(out, "room", "Room 2")
            self.assertEqual((r1["dry_g_per_sqft"], r1["dry_down_pct"]), (21.73, 78.21))
            self.assertEqual(r1["coverage"]["dry_down_pct"], "3 of 4 batches; 1 excluded: EX-R1-0829 (no dry weight)")
            self.assertEqual((r2["dry_g_per_sqft"], r2["dry_down_pct"]), (21.55, 78.46))
            self.assertEqual(r2["coverage"]["dry_g_per_sqft"], "1 of 2 batches; 1 excluded: EX-R2-0805 (dry weight 0 g)")
            self.assertEqual(out["overall_dry_down_pct"], 78.26)
            self.assertTrue(out["totals_coverage"]["overall_dry_down_pct"].startswith("4 of 6 batches"))
            self.assertEqual(out["total_dry_g"], 20609.12)
            self.assertEqual(out["duplicate_harvest_ids"], ["EX-R1-0801"])
            self.assertIn("ZERO_DRY;", batches["EX-R2-0805"]["flags"])
            self.assertIn("UNIT_FROM_WEIGHT_UNIT_ARG;", batches["EX-R2-0819"]["flags"])
            r0815 = batches["EX-R1-0815"]
            self.assertEqual((r0815["trim_pct"], r0815["unaccounted_g"], r0815["sum_check"]),
                             ("", "800.0", "INCOMPLETE_BREAKDOWN"))
            self.assertEqual(len(out["input_problems"]), 5)

    def test_eval5_unreadable_and_negative_numbers(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(BAD, d)
            self.assertEqual(out["total_dry_g"], 19800.0)
            self.assertTrue(out["totals_coverage"]["total_dry_g"].startswith("4 of 6 batches"))
            self.assertEqual(out["overall_dry_down_pct"], 78.02)
            self.assertTrue(out["totals_coverage"]["overall_dry_down_pct"].startswith("3 of 6 batches"))
            r3, r4 = self.group(out, "room", "Room 3"), self.group(out, "room", "Room 4")
            self.assertEqual((r4["dry_g_per_sqft"], r3["dry_g_per_sqft"], r3["dry_down_pct"]), (22.25, 21.8, 78.0))
            self.assertTrue(r4["coverage"]["dry_g_per_sqft"].startswith("2 of 3 batches"))
            self.assertTrue(r3["coverage"]["dry_g_per_sqft"].startswith("2 of 3 batches"))
            self.assertTrue(r3["coverage"]["dry_down_pct"].startswith("1 of 3 batches"))
            self.assertEqual(batches["EX-R3-0901"]["wet_g"], "25000.0")
            b = batches["EX-R4-0909"]
            self.assertEqual((b["trim_pct"], b["sum_check"], b["unaccounted_g"], b["cost_per_dry_g"]),
                             ("", "INCOMPLETE_BREAKDOWN", "750.0", ""))
            for row, col, raw in ((3, "Wet Weight", "NaN"), (4, "Dry Weight", "inf"), (5, "Dry Weight", "4,25"),
                                  (6, "Trim", "-150"), (6, "Cycle Cost", "1.234,56"), (7, "Plants", "-40")):
                with self.subTest(row=row, column=col):
                    self.assertTrue(any(p.startswith(f"row {row} ") and f"column '{col}' value '{raw}'" in p
                                        for p in out["input_problems"]), out["input_problems"])


# column -> how to check BD-F1-0712 (Flower 1, row 2) was left out of what needs that column
EXCLUSIONS = {
    "Wet Weight": lambda t, out, b: (t.assertTrue(out["totals_coverage"]["total_wet_g"].startswith("7 of 8")),
                                     t.assertTrue(out["totals_coverage"]["overall_dry_down_pct"].startswith("7 of 8")),
                                     t.assertEqual(b["dry_down_pct"], "")),
    "Dry Weight": lambda t, out, b: (t.assertTrue(out["totals_coverage"]["total_dry_g"].startswith("7 of 8")),
                                     t.assertTrue(YieldCase.group(out, "room", "Flower 1")["coverage"]
                                                  ["dry_g_per_sqft"].startswith("2 of 3")),
                                     t.assertEqual(b["dry_g_per_sqft"], "")),
    "A Flower": lambda t, out, b: (t.assertEqual((b["flower_a_pct"], b["sum_check"], b["cost_per_flower_g"]),
                                                 ("", "INCOMPLETE_BREAKDOWN", ""))),
    "Smalls": lambda t, out, b: (t.assertEqual((b["flower_b_pct"], b["sum_check"], b["cost_per_flower_g"]),
                                               ("", "INCOMPLETE_BREAKDOWN", ""))),
    "Trim": lambda t, out, b: t.assertEqual((b["trim_pct"], b["sum_check"]), ("", "INCOMPLETE_BREAKDOWN")),
    "Waste": lambda t, out, b: t.assertEqual((b["waste_pct"], b["sum_check"]), ("", "INCOMPLETE_BREAKDOWN")),
    "Plants": lambda t, out, b: (t.assertEqual(b["dry_g_per_plant"], ""),
                                 t.assertTrue(YieldCase.group(out, "room", "Flower 1")["coverage"]
                                              ["dry_g_per_plant"].startswith("2 of 3"))),
    "Canopy Sq Ft": lambda t, out, b: (t.assertEqual(b["dry_g_per_sqft"], ""),
                                       t.assertTrue(YieldCase.group(out, "room", "Flower 1")["coverage"]
                                                    ["dry_g_per_sqft"].startswith("2 of 3"))),
    "Lights": lambda t, out, b: (t.assertEqual(b["dry_g_per_light"], ""),
                                 t.assertTrue(YieldCase.group(out, "room", "Flower 1")["coverage"]
                                              ["dry_g_per_light"].startswith("2 of 3"))),
    "Cycle Cost": lambda t, out, b: t.assertEqual((b["cost_per_dry_g"], b["cost_per_flower_g"]), ("", "")),
}


class BadNumbers(YieldCase):
    def check_column(self, column):
        for label, raw in h.BAD_NUMBERS.items():
            with self.subTest(column=column, value=label), h.TempDir() as d:
                src = h.mutate_csv(Q3, d / "harvests.csv", 0, column, raw)
                out, batches = self.run_ok(src, d / "out")
                self.assertTrue(any(p.startswith("row 2 (BD-F1-0712)") and f"column '{column}' value '{raw}'" in p
                                    for p in out["input_problems"]), out["input_problems"])
                self.assertEqual(out["batches"], 8, "the batch is kept and reported, not dropped")
                EXCLUSIONS[column](self, out, batches["BD-F1-0712"])

    def test_wet_weight_bad_numbers(self):
        self.check_column("Wet Weight")

    def test_dry_weight_bad_numbers(self):
        self.check_column("Dry Weight")

    def test_a_flower_bad_numbers(self):
        self.check_column("A Flower")

    def test_smalls_bad_numbers(self):
        self.check_column("Smalls")

    def test_trim_bad_numbers(self):
        self.check_column("Trim")

    def test_waste_bad_numbers(self):
        self.check_column("Waste")

    def test_plant_count_bad_numbers(self):
        self.check_column("Plants")

    def test_canopy_sqft_bad_numbers(self):
        self.check_column("Canopy Sq Ft")

    def test_light_count_bad_numbers(self):
        self.check_column("Lights")

    def test_cycle_cost_bad_numbers(self):
        self.check_column("Cycle Cost")

    def test_negative_count_reported_even_when_dry_weight_is_blank(self):
        with h.TempDir() as d:
            src = h.mutate_csv(Q3, d / "h1.csv", 0, "Dry Weight", "")
            src = h.mutate_csv(src, d / "h2.csv", 0, "Plants", "-96")
            out, _ = self.run_ok(src, d / "out")
            self.assertIn("row 2 (BD-F1-0712): column 'Plants' value '-96': plant count is -96; dry_g_per_plant "
                          "left blank", out["input_problems"])

    def test_us_thousands_separator_is_read(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(h.mutate_csv(Q3, d / "h.csv", 0, "Wet Weight", "62,000"), d / "out")
            self.assertEqual(batches["BD-F1-0712"]["wet_g"], "62000.0")
            self.assertEqual(out["input_problems"], [])


class Structure(YieldCase):
    def test_empty_file_exits_with_message(self):
        with h.TempDir() as d:
            (d / "h.csv").write_text("")
            res = self.run_yield(["--harvests", d / "h.csv", "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("empty", res.stderr)

    def test_missing_file_exits_with_message(self):
        with h.TempDir() as d:
            res = self.run_yield(["--harvests", d / "nope.csv", "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("Cannot read", res.stderr)

    def test_header_only_writes_empty_outputs_and_says_so(self):
        with h.TempDir() as d:
            header, _ = self.q3_rows()
            h.write_csv(d / "h.csv", header, [])
            out, batches = self.run_ok(d / "h.csv", d / "out")
            self.assertEqual((out["batches"], out["total_dry_g"], batches), (0, 0, {}))
            self.assertIn("No harvest batches were analyzed: the file has no data rows. Ask for the harvest log "
                          "with one row per batch.", out["input_problems"])
            with open(d / "out" / "yield_by_batch.csv", newline="") as f:
                self.assertEqual(next(csv.reader(f)), BATCH_FIELDS)

    def test_only_blank_rows(self):
        with h.TempDir() as d:
            header, _ = self.q3_rows()
            h.write_csv(d / "h.csv", header, [[""] * len(header)] * 3)
            out, _ = self.run_ok(d / "h.csv", d / "out")
            self.assertEqual(out["batches"], 0)
            self.assertIn("Skipped 3 fully blank row(s).", out["input_problems"])

    def test_duplicate_rows_are_kept_and_flagged(self):
        with h.TempDir() as d:
            header, rows = self.q3_rows()
            h.write_csv(d / "h.csv", header, rows + [rows[0]])
            out, _ = self.run_ok(d / "h.csv", d / "out")
            self.assertEqual(out["batches"], 9)
            self.assertEqual(out["total_dry_g"], 89584.2 + 13640)
            self.assertEqual(out["duplicate_harvest_ids"], ["BD-F1-0712"])
            self.assertIn("harvest ID BD-F1-0712 appears on rows 2, 10 (identical rows). All rows were kept and "
                          "counted in totals and aggregates. If one is a re-entry, remove it and rerun.",
                          out["input_problems"])

    def test_blank_required_cells(self):
        cases = {"Wet Weight": ("BD-F1-0712", "MISSING_WET;"), "Dry Weight": ("BD-F1-0712", "MISSING_DRY;"),
                 "Harvest Name": ("Blue Dream|Flower 1|2026-07-12", "")}
        for column, (hid, flag) in cases.items():
            with self.subTest(column=column), h.TempDir() as d:
                out, batches = self.run_ok(h.mutate_csv(Q3, d / "h.csv", 0, column, ""), d / "out")
                self.assertEqual(out["batches"], 8)
                self.assertIn(hid, batches)
                self.assertTrue(batches[hid]["flags"].startswith(flag))

    def test_mixed_units_convert_per_row(self):
        with h.TempDir() as d:
            header, rows = self.q3_rows()
            col = {c: i for i, c in enumerate(header)}
            row = rows[0]
            for c, v in (("Wet Weight", "62"), ("Dry Weight", "13.64"), ("A Flower", "8.9"), ("Smalls", "2.1"),
                         ("Trim", "2.24"), ("Waste", "0.4"), ("Unit", "kg")):
                row[col[c]] = v
            h.write_csv(d / "h.csv", header, rows)
            out, batches = self.run_ok(d / "h.csv", d / "out")
            self.assertEqual(out["total_dry_g"], 89584.2)
            self.assertEqual(self.group(out, "room", "Flower 1")["dry_g_per_sqft"], 28.34)
            self.assertEqual((batches["BD-F1-0712"]["source_unit"], batches["BD-F1-0712"]["sum_check"]), ("kg", "OK"))

    def test_unknown_unit_row_is_skipped_and_reported(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(h.mutate_csv(Q3, d / "h.csv", 0, "Unit", "stone"), d / "out")
            self.assertEqual(out["batches"], 7)
            self.assertNotIn("BD-F1-0712", batches)
            self.assertTrue(any(p.startswith("row 2 (BD-F1-0712): column 'Unit' value 'stone': unknown unit")
                                for p in out["input_problems"]), out["input_problems"])

    def test_blank_unit_cell_without_weight_unit_is_skipped_and_reported(self):
        with h.TempDir() as d:
            out, batches = self.run_ok(h.mutate_csv(Q3, d / "h.csv", 0, "Unit", ""), d / "out")
            self.assertEqual(out["batches"], 7)
            self.assertTrue(any(p.startswith("row 2 (BD-F1-0712): unit cell is blank") for p in out["input_problems"]))

    def test_unknown_weight_unit_flag_exits_with_message(self):
        with h.TempDir() as d:
            res = self.run_yield(["--harvests", NO_UNITS, "--weight-unit", "stone", "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("Unknown --weight-unit 'stone'", res.stderr)


class FormulaInjection(YieldCase):
    def test_text_columns_with_formulas_are_neutralised(self):
        for column in ("Harvest Name", "Strain", "Room", "Harvest Date"):
            for cell in h.FORMULA_CELLS:
                with self.subTest(column=column, cell=cell), h.TempDir() as d:
                    self.run_ok(h.mutate_csv(Q3, d / "h.csv", 0, column, cell), d / "out")
                    h.assert_no_live_formulas(self, d / "out")
                    self.assertIn("'" + cell, list(h.csv_cells(d / "out" / "yield_by_batch.csv")))

    def test_csv_safe_matches_shared_text(self):
        self.assertIn("\n\n\n" + CSV_SAFE_TEXT, h.script_path(NAME).read_text())


class Determinism(YieldCase):
    def test_same_inputs_give_byte_identical_outputs(self):
        for label, src, extra in (("q3", Q3, []), ("gaps", GAPS, ["--weight-unit", "lb"]), ("bad", BAD, [])):
            with self.subTest(run=label), h.TempDir() as d:
                self.run_ok(src, d / "a", *extra)
                self.run_ok(src, d / "b", *extra)
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


class SkillMdCommand(YieldCase):
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
                argv = documented_args(cmd, skill_md, {"--harvests": Q3, "--out-dir": d / "out"})
                res = self.run_yield(argv)
                self.assertEqual(res.returncode, 0, f"{shlex.join(map(str, argv))}\n{res.stdout}{res.stderr}")
                out = h.strict_json_load(res.stdout, is_text=True)
                if "--detect-only" in argv:
                    self.assertEqual(out["mapping"]["uom"], "Unit")
                    continue
                for name in OUTPUTS:
                    self.assertTrue((d / "out" / name).exists(), name)
                self.assertEqual(out["by_room_ranked_by_g_per_sqft"][0]["dry_g_per_sqft"], 28.34)
                self.assertEqual(out["total_dry_g"], 89584.2)


class NoTraceback(YieldCase):
    def test_odd_invocations_never_traceback(self):
        cases = [[], ["--harvests"], ["--harvests", Q3, "--map", "wet_weight"],
                 ["--harvests", Q3, "--map", "wet_weight=Nope"], ["--harvests", Q3, "--map", "trim=Room"],
                 ["--harvests", Q3, "--weight-unit", "g"]]
        for args in cases:
            with self.subTest(args=args), h.TempDir() as d:
                res = self.run_yield(args + ["--out-dir", d / "out"])
                self.assertIn(res.returncode, (0, 1, 2))

    def test_non_utf8_file_exits_with_message(self):
        with h.TempDir() as d:
            (d / "h.csv").write_bytes("Harvest,Wet,Dry,Unit\n\xe9\xff,1,1,g\n".encode("latin-1"))
            res = self.run_yield(["--harvests", d / "h.csv", "--out-dir", d / "out"])
            self.assertEqual(res.returncode, 1)
            self.assertIn("UTF-8", res.stderr)


if __name__ == "__main__":
    unittest.main()
