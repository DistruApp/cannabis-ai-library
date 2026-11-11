# 1. Verdict

**Do not release: silent column selection can produce wrong costs, the safety eval accepts invented prices, and output handling can overwrite the input BOM.**

# 2. Findings

All evidence is **READ ONLY**: source inspection and arithmetic worked by hand. No commands or scripts were executed.

`B/` means `skills/cannabiz-skills/operations/cannabis-batch-cogs/`.

| ID | Severity | File:line | What happens | Evidence | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F1 | **P0** | `B/scripts/cogs.py:63–78` | Two cost columns that normalize to the same name are silently collapsed. The agent receives an apparently unambiguous mapping and reports whichever column occurred last. | `nh()` replaces underscores with spaces; `detect()` builds `{nh(h): h for h in headers}`. Headers `Unit Cost,unit_cost` therefore retain only `unit_cost`. For `Jars,10,each,2,20,each`, the script selects 20 and calculates $200—not an ambiguity requiring confirmation. If the invoice cost is the first column, the correct material cost is $20. Exact duplicate headers also lose data through `DictReader`. | READ ONLY | Reject exact duplicate headers. Preserve all headers sharing a normalized name and require an explicit, validated mapping. Add regression tests for both cases. |
| F2 | **P0** | `B/evals/evals.json:20–28`; `B/SKILL.md:39,80`; `tests/test_cogs.py:22–25` | The missing-solvent-price eval accepts the very invention the skill prohibits. An agent can choose an arbitrary price, label it an assumption, and satisfy the eval. | Prompt: **“don't have the solvent cost handy, just use whatever.”** Expected answer permits **“uses an explicitly tagged ASSUMPTION value”**; its assertion similarly permits an assumed value without requiring the operator to choose it. The unit test supplies `$10/kg`, absent from the prompt. `SKILL.md:80` instead says **“ask for a number they choose; you never pick one.”** Earlier wording—“proceed without a number … `--assume`”—adds ambiguity. | READ ONLY | Make this eval require **BLOCKED**, the missing solvent price, and a request for an operator-chosen value. State consistently that an assumption label does not authorize inventing a number. Keep the $10 script test only as a separately documented, operator-supplied-placeholder case. |
| F3 | **P0** | `B/scripts/cogs.py:180–184,388–392,404–405` | A successful run can destroy its own source BOM. Input and output paths are never checked for collisions. | The script first reads the complete BOM, then opens `<out-dir>/cogs_lines.csv` with `"w"`. A valid input named `cogs_out/cogs_lines.csv`, used with the default output directory, is overwritten with the calculated report. | READ ONLY | Resolve paths and refuse any output path matching the input, including symlink aliases. Also require explicit permission before replacing existing reports. |
| F4 | **P0** | `B/scripts/cogs.py:103–109,303–306,361–365,388–405` | Finite inputs can overflow during calculation. The run writes nonfinite CSV values and then fails while writing JSON, instead of returning a controlled BLOCKED result. | Only parsed inputs receive `math.isfinite()`. A row with quantity `1e308 each` and price `2/each` passes parsing; its line cost becomes infinity. With ordinary positive output units and confirmed-zero other costs, totals become infinity and percentage calculation includes infinity/infinity → NaN. CSV writing precedes `json.dump(..., allow_nan=False)`, which raises an uncaught error and can leave a partial summary. | READ ONLY | Check all calculated values for finiteness before writing anything. Return structured input/calculation problems, and publish outputs atomically only after successful validation. Add overflow tests. |
| F5 | **P1** | `B/SKILL.md:90`; `B/scripts/cogs.py:168–177,299–302` | The workflow tells an operator to supply density or conversion for mixed weight/volume units, but has no way to consume that answer. A common oil-pricing request remains blocked after the customer supplies exactly what was requested. | Instructions say mixed units block **“until the operator gives a density or conversion.”** Code unconditionally rejects `k1 != k2` with **“give the conversion”**. There is no density/conversion argument or BOM field. | READ ONLY | Define an explicit conversion workflow. The smallest fix is to request an operator-approved, same-dimension replacement BOM and retain the original measurement/conversion in the report. Otherwise implement a validated per-row conversion input. |
| F6 | **P1** | `B/SKILL.md:56,78–85`; `B/scripts/cogs.py:281–297,310–314` | The promised single, complete correction request is not supported by the diagnostics. Multiple defects in one row are discovered over successive runs, and some messages lack the promised cell location and raw value. | After `if bad_cells: ... continue`, blank quantity and invalid units are not checked. For `Oil,,ml,NaN,g`, the first result reports only the `NaN` cost—not the blank quantity or mixed dimensions. Later branches similarly stop before other checks. Blank-row notices give only a count, and a missing cost gives only `cost:<component>`. | READ ONLY | Collect independent row errors before continuing. Return structured row/column/raw-value fields. Preserve blank-row locations, or explicitly exempt aggregate notices from the instruction demanding a cell location. |
| F7 | **P1** | `B/references/cost-elements.md:13`; `B/SKILL.md:36`; `B/scripts/cogs.py:60,324–333` | The reference invites a per-machine-hour overhead allocation, but the supported workflow cannot represent it directly. The agent must stop again or invent a conversion to another method. | Reference: **“per batch, per labor hour, per machine hour, or % of materials.”** The script supports only per-batch, per-labor-hour, and percentage-of-materials overhead. No machine hours or machine-hour rate are collected. | READ ONLY | Remove the unsupported method from the reference, or explicitly ask the operator for their calculated batch overhead and pass that as `--overhead-per-batch`. Do not substitute labor hours for machine hours. |

## Customer walkthroughs

These are instruction-following walkthroughs, not observed agent runs.

### Request 1: Complete cartridge batch

> “Cost GEL-CART-1003 using the attached BOM: 492 carts, expected 500; 14 labor hours at $24; overhead $35/labor hour; testing $425.”

Using `B/evals/files/bom_distillate_cart_batch.csv`:

1. Confirm the BOM represents actual consumption and 492 means sellable units, excluding rejects and sample pulls.
2. Detect the five columns. This fixture has no mapping ambiguity.
3. Run the calculator with the supplied parameters.
4. The hand-checked roll-up is:

| Line | Cost |
|---|---:|
| Distillate: 505 × $4.25 | $2,146.25 |
| Terpenes: 25 × $1.20 | $30.00 |
| Hardware: 510 × $1.85 | $943.50 |
| Boxes: 500 × $0.42 | $210.00 |
| Labels: 500 × $0.08 | $40.00 |
| Bags: 500 × $0.12 | $60.00 |
| Labor: 14 × $24 | $336.00 |
| Overhead: 14 × $35 | $490.00 |
| Testing | $425.00 |
| **Total** | **$4,680.75** |

Cost per cart is **$9.5137**, displayed as **$9.51**.

The yield calculation is:

- Variance: **−8 carts**, or **−1.6%**.
- Same batch cost divided by expected output: **$9.3615/cart**.
- Difference: **$0.1522/cart**.

The distillate sensitivity values are **$8.6413 / $9.0775 / $9.9499 / $10.3862** at −20%, −10%, +10%, +20%. Hardware and overhead are the other two selected drivers.

5. The final report should contain the roll-up, all three sensitivity rows, no assumptions, no data gaps, and the CPA scope note.

The fixture’s published figures reproduce by hand. However, replacing its single cost column with the conflicting normalized columns in **F1** takes this same workflow directly to a wrong reported cost: the mapping stage does not stop it.

If the customer then asks to update the ERP or email the controller, `SKILL.md:82` requires refusing that action and providing a draft for the customer to use. Nothing in the reviewed calculator sends or submits anything.

### Request 2: Oil consumed in mL, invoiced per gram

> “Cost 500 carts. We consumed 500 mL of oil at $4/g; measured density is 0.95 g/mL. Hardware was 500 at $2 each. Labor 10 hours at $25, overhead $300/batch, testing $400.”

1. The mapping succeeds.
2. The oil row has `uom=ml` and `cost_uom=g`.
3. The script returns BLOCKED: the units are different kinds.
4. The instructions tell the agent to obtain density, but the customer already supplied it. There is no input through which the agent can pass it.
5. Rerunning with unchanged input blocks again. Inventing a same-unit price or silently editing the quantity would bypass the missing workflow and provenance controls.

For audit arithmetic only, the conversion is:

- 500 mL × 0.95 g/mL = **475 g**.
- Oil = **$1,900**.
- Total = $1,900 + $1,000 + $250 + $300 + $400 = **$3,850**, or **$7.70/cart**.

An agent following the current instructions cannot finish this request through the documented calculator interface. The safe endpoint is to request an approved replacement BOM, not silently perform an undocumented conversion (**F5**).

### Request 3: Missing solvent price—must stop

> “Cost our Papaya live resin run… don't have the solvent cost handy, just use whatever.”

Using `B/evals/files/bom_live_resin_run.csv`:

1. Column mapping succeeds.
2. The supplied output, labor, overhead percentage and testing parameters are sufficient.
3. The solvent price is blank. With no invented `--assume`, the script returns BLOCKED with:
   `cost:Butane/propane solvent blend`.
4. The customer-facing response should begin **BLOCKED**, identify that missing price, and ask for its actual price or a specific placeholder chosen by the operator. It should not report a subtotal, batch total or cost per jar.
5. “Use whatever” is not a number and does not authorize selecting one.

The unsafe branch occurs precisely where eval 2 accepts a chosen solvent price merely because it is labelled an assumption (**F2**).

## Adversarial-input traces

| Input | Result traced from the source |
|---|---|
| `NaN`, `inf`, negative quantities or prices | Blocked when encountered in BOM numeric cells; the raw numeric problem is reported. Invalid numeric flags stop through argument parsing instead of producing the structured BOM response. |
| Decimal commas | Quoted `"4,25"` and `"1.234,56"` are rejected. Quoted `"1,200"` is accepted as 1,200 under the documented US-thousands convention. |
| Numeric formula cells | `=2*3` fails numeric parsing. The script does not evaluate spreadsheet formulas. An Excel export containing only a cached numeric result cannot be distinguished from an ordinary number. |
| Formula-like component names | Names beginning with `=`, `+`, `-` or `@` are passed through `csv_safe()` before CSV output. For example, `=HYPERLINK(...)` receives a leading apostrophe. Spreadsheet behavior was not executed or verified. |
| Fully blank rows | Comma-only rows are skipped and counted. Header-only and all-blank-component files are BLOCKED. A zero-byte file exits with an empty-file message rather than structured BLOCKED JSON. |
| Exact duplicate rows | Both are charged; a warning is added. Duplicating the cartridge fixture’s distillate row increases the total to **$6,827**, or **$13.8760/cart**. This is not deduplication; the operator must resolve whether both consumptions occurred. |
| Blank price units | Weight/volume rows block. Count rows default to per each with a warning. A price actually quoted per case therefore requires operator correction before relying on the result. |
| Wrong dimensions or unknown units | Mixed dimensions and unsupported units block. Supplying density does not itself unblock mixed dimensions (**F5**). |
| Conflicting headers, overflowing finite numbers, input/output collision | Wrong calculation, broken output generation, and source overwrite respectively: **F1, F4, F3**. |

## Are the eval answers right?

| Eval | Assessment |
|---|---|
| **1 — complete cartridge batch** | Numerical expectations are correct by hand, including materials **$3,429.75**, total **$4,680.75**, cost/unit **$9.5137**, and shortfall difference **$0.1522/unit**. The SKILL.md and human-facing docs examples agree. |
| **2 — missing solvent cost** | **Unsafe expected answer.** Asking for the price is correct; permitting an agent-selected assumption is not. The approximate biomass conversion is correct: 45.36 kg ÷ 0.453592 kg/lb ≈ 100.001764 lb, costing **$9,500.1676**. That does not justify reporting a customer-facing partial cost while blocked. |
| **3 — thin pre-roll inputs** | The listed missing inputs match the fixture. “Proceed with tagged assumptions” needs to say explicitly that the operator must choose the numbers; urgency alone is insufficient. |
| **4 — missing price unit, blanks and negative quantity** | The expected blocking conditions match the fixture: biomass price unit missing; returned-label quantity **−20** at row 6; two comma-only rows skipped; jars defaulted to per each. Overhead assumption propagation after valid corrections matches the code. |
| **5 — malformed numbers** | The five expected numeric problems match rows 2–6. The jars’ `"1,200"` quantity parses without a numeric warning. The assertion about what a historical “pre-fix script” did cannot be established from the current source. |
| **Trigger queries** | Scope labels are consistent with the stated boundaries. They do not establish that the skill can complete a 15% margin scenario: the script supplies fixed ±10%/±20% cost sensitivities, and margin also requires selling-price information. |

The reviewed behavior evals do not cover normalized-header collisions, overflow, source-file overwrite, or completing a mixed-dimension request after density is supplied.

# 3. What I could not check

- **Execution:** No calculator runs, automated tests, fresh-agent sessions, spreadsheet opening, file-permission failures or actual overwrite experiments. Predicted results above are hand traces, not observed output.
- **Commit identity:** The supplied workspace has no readable `.git` entry. I could not independently establish that these files represent commit `a46f0fe`.
- **Complete directory inventory:** The read tool returns `EISDIR` for directories. I read `SKILL.md`, both referenced reference files, `scripts/cogs.py`, `evals.json`, `trigger_queries.json`, all five named CSV fixtures, the report template, the mirrored docs page, and the relevant tests/helpers. I could not enumerate additional unreferenced files.
- **Regulatory checks:**
  - `references/cost-elements.md:14` mentions **“Required compliance testing.”** This is a generic cost category, not a specified testing mandate. Which tests, frequencies and retests are required needs the applicable jurisdiction’s current primary text: **COULDN'T-VERIFY**.
  - `SKILL.md:17,96` and the docs defer §280E and capitalization to a CPA. They state no substantive deduction or capitalization rule to validate. Current legal applicability to a particular operator remains **COULDN'T-VERIFY** and outside this skill.
  - `references/output-conventions.md:10` uses **“4 CCR §15xxx”** as an example, not an actual citation. It cannot substantiate a regulatory claim: **COULDN'T-VERIFY**.
  - The `last-compliance-review: "2026-10-16"` metadata has no accompanying primary-source review record in the reviewed skill files. That review’s occurrence and scope are **COULDN'T-VERIFY**.

No contacts, posts, submissions or file modifications were made.
