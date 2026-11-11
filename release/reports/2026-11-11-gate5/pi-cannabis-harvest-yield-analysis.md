## 1. Verdict

**Do not release unchanged: the skill can misstate the reporting period, silently lose input values, invent harvest status, and fail on finite-but-extreme numbers.**

## 2. Findings

Paths below are relative to `skills/cannabiz-skills/operations/cannabis-harvest-yield-analysis/`, except `docs/...`. Evidence is quoted source and manual tracing—not executed commands.

| ID | Severity | File:line | What happens | Evidence | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F01 | **P0** | `evals/files/harvests_2026_q3.csv:9`; `evals/evals.json:7–14`; `SKILL.md:99–103`; `docs/cannabiz-skills/operations/cannabis-harvest-yield-analysis.md:25–27` | The Q3 example and eval include an October harvest. An agent following the example reports the wrong period’s total and room yield. | Fixture contains `BD-F1-1004,...,2026-10-04,...,13376,...`. The eval nevertheless expects Flower 1 at `28.34` and four gaps, including this batch. Calendar Q3 excludes October 4: **7 batches, 76,208.1968 g ≈168.010 lb**, Flower 1 **28.57 g/sq ft**, and **three** gaps. The published 197.5 lb includes October. | READ ONLY | Check requested dates against the file before calculation. Ask whether the operator means calendar Q3 or all supplied rows; update fixture, expected answers, and both examples consistently. |
| F02 | **P0** | `scripts/yield.py:79–89,178–180` | Duplicate column headers silently discard a value instead of producing an ambiguity. Normalized-header collisions also select the last matching header. | `csv.DictReader(f)` reads rows before validation; detection builds `{norm_header(h): h for h in headers}`. With headers `Batch,Wet,Dry,Dry,Unit` and row `H1,5000,1000,2000,g`, only the second dry value survives. The script reports **2,000 g and 60% dry-down**, without warning that another dry value was lost. | READ ONLY | Reject exact and normalized duplicate headers before reading data into dictionaries. Require distinct column names and confirmed mapping. |
| F03 | **P0** | `scripts/yield.py:119–121,248–249,438–456` | Finite inputs can become infinity during conversion or aggregation. The script then fails while writing JSON, potentially leaving a CSV and a partially written JSON file. | Parsing checks `math.isfinite(v)` **before** `v *= g`. For `Wet=1e308, Dry=1, Unit=kg`, parsing succeeds, but wet grams become infinity. `json.dump(..., allow_nan=False)` cannot serialize the resulting total. Two individually finite `1e308` gram weights can likewise overflow their sum. | READ ONLY | Validate converted weights and all computed results; reject unsafe magnitudes with row-specific problems. Validate outputs before writing and replace output files atomically. |
| F04 | **P1** | `scripts/yield.py:322–351` | Missing breakdown columns are not treated like missing cells; entirely blank breakdowns escape the promised incomplete-breakdown warning. An existing excess can also be hidden behind “incomplete.” | `blank_parts = [... if k in m and parts[k] is None]` ignores absent columns. Dry **1,000 g**, A flower **1,000 g**, and no other breakdown columns produces `OK`, although the other categories are unknown. If all four mapped parts are blank, the result is `NO_BREAKDOWN` without an incomplete-breakdown problem. Dry **1,000**, A **800**, B **300**, trim blank, waste **0** produces only `INCOMPLETE_BREAKDOWN`, despite known parts already exceeding dry by **100 g**. | READ ONLY | Distinguish unknown, explicitly zero, and not applicable. Report incomplete coverage for absent columns and all-blank parts. Emit completeness and excess/gap checks independently. |
| F05 | **P1** | `scripts/yield.py:93,109–114`; `SKILL.md:53` | Three-decimal comma values are silently interpreted as US thousands, even though no numeric locale is collected. This can cause a 1,000-fold error. | `_THOUSANDS_RE` accepts `4,250`; the parser removes the comma. If the operator means **4.250 lb**, the script instead reads **4,250 lb**: **1,927.766 g** becomes **1,927,766 g**. The instructions say decimal commas are rejected but do not identify this exception or require locale confirmation. | READ ONLY | Confirm numeric format, not just weight units. Require an explicit locale/format choice when comma-containing values could have either interpretation. |
| F06 | **P1** | `SKILL.md:84`; `scripts/yield.py:421–428` | The required final response claims a per-plant comparison whenever canopy is absent—even when plant counts are absent too. When plant counts exist, the script’s ranking arrays still sort only by square-foot yield. | Instruction: “if canopy is missing … **you compared per plant only**.” But plant count is optional. With neither denominator, all normalized yields are blank. With no canopy, `res.sort(...)` uses identical empty square-foot keys and preserves input order rather than ranking per plant. | READ ONLY | Make fallback conditional on actual denominator coverage. If none is available, explicitly decline a normalized ranking. Have the script produce a correctly sorted fallback ranking and identify its metric. |
| F07 | **P0** | `SKILL.md:94` | A missing dry weight becomes an invented operational fact: the report labels the batch “still curing” even if its weight was merely omitted. | “The script leaves a batch with a blank dry weight out … **Label it as still curing in the report.**” The code itself only asks `still curing?`; no status field establishes that fact. | READ ONLY | Report “dry weight missing; status unconfirmed.” Say “still curing” only when the operator or source records establish it. |
| F08 | **P1** | `references/interpreting-yield.md:7` | The high-dry-down troubleshooting table gives a cause with the opposite mathematical effect. | Under **“Dry-down much higher”**, it lists “dry weight taken before the cure finished.” At wet **5,000 g**, dry **1,000 g** gives **80%** dry-down; an early, wetter dry weight of **1,200 g** gives **76%**, which is lower. | READ ONLY | Remove early dry weighing from the high-dry-down row; retain it under low dry-down. Check each directional explanation against the formula. |

### First-time customer walkthroughs

All figures below are manually traced.

#### Request 1: “Q3 harvests attached. Which rooms perform best, and what does each gram cost?”

Using `harvests_2026_q3.csv`:

1. The agent confirms mappings, dry-weight definition, and row units. The pound batch converts to **63,276.084 g wet** and **13,789.1968 g dry**.
2. Nothing in the workflow requires checking the requested reporting period against harvest dates.
3. The calculator includes all eight rows and returns approximately **89,584.20 g / 197.500 lb**, **78.27%** overall dry-down, and Flower 1 at **28.34 g/sq ft**.
4. The example and eval encourage calling that a Q3 result.

**Failure point:** accepting the file’s scope without resolving its October row, then presenting the resulting totals as Q3. The correct next action is a scope question—not silently dropping the row or treating the example as authority. See F01.

The all-file arithmetic otherwise reproduces the eval’s room yields, Papaya’s **$2.7049/dry g**, and the four listed gaps.

#### Request 2: “Which room should we expand? Here’s our harvest log; we don’t track plants or canopy.”

Suppose the customer supplies:

| Batch | Strain | Room | Wet | Dry | A Flower | Unit | Cycle Cost |
|---|---|---|---:|---:|---:|---|---:|
| H-A | Example Kush | A | 5000 | 1000 | 1000 | g | 2000 |
| H-B | Example Haze | B | 5000 | 1000 |  | g | 1800 |

1. Collection instructions say to ask for missing fields, but allow proceeding with available data.
2. After mapping confirmation, the calculator produces **2,000 g dry**, **80% overall dry-down**, and costs of **$2.00/g** and **$1.80/g**.
3. It cannot calculate yield per plant, square foot, or light.
4. H-A receives `OK` for its breakdown despite absent B/trim/waste columns. H-B receives `NO_BREAKDOWN`, without the promised incomplete-breakdown problem.
5. The final-response instruction nevertheless says to claim a per-plant comparison.

**Failure points:** the unsupported comparison in F06 and the overstated breakdown completeness in F04. Neither lower cost nor equal total output establishes which room deserves expansion.

#### Request that must stop: “Finish these harvests in Metrc, and tell me the legal waste-recording deadline.”

Using the regression-gap fixture, with the customer confirming the blank unit means pounds:

1. The agent must refuse **the system action**, not merely ask for credentials. `SKILL.md:79` expressly prohibits closing, finishing, or submitting.
2. It may continue the analysis after confirming mappings and weight definitions.
3. Hand-traced results are Room 1 **21.73 g/sq ft**, **78.21%** dry-down on **3/4** rows; Room 2 **21.55 g/sq ft**, **78.46%** on **1/2**; overall **78.26%** on **4/6**.
4. It must report the duplicate, zero dry weight, blank-unit substitution, and **800 g** incomplete-breakdown residual.
5. It must not invent a deadline: jurisdiction and primary authority are absent.

There is no instruction authorizing submission. However, the eval suite contains no end-to-end close-out or legal-deadline refusal case to test this boundary.

### Adversarial-input trace

| Input | Source-derived behavior |
|---|---|
| `NaN`, `inf`, `4,25`, `1.234,56` | Rejected and reported. `25,000` is accepted as 25,000. Three-decimal comma ambiguity remains: F05. |
| Negative trim/cost; zero or negative denominators | Negative trim/cost become blank. Invalid counts are excluded from their ratios. Zero dry weight is excluded rather than reported as 100% dry-down. |
| Blank and duplicate rows | Fully blank dictionary rows are counted and skipped. Duplicate IDs remain in totals and are flagged; removing them requires operator confirmation. Duplicate **columns** are not protected: F02. |
| Missing/unknown units | No unit column and no argument stops execution. Blank row units without fallback and unknown row units are skipped with problems. A valid but incorrect unit label is accepted; plausibility cannot establish the correct unit. |
| Formula cells | Numeric `=SUM(...)` is rejected. Literal formula-starting text is apostrophe-prefixed in the output CSV through `csv_safe`. Formula text remains literal in JSON; there is no evaluation step in this script. Spreadsheet-consumer behavior was not tested. |
| Empty files | A zero-byte file exits with an explanatory error. Recognized headers with zero data rows produce zero totals, empty rankings, and “No harvest batches were analyzed.” Those zeros must not be described as actual production. |
| Extreme finite numbers | Initial numeric validation does not prevent conversion, division, or summation overflow: F03. |

### Are the eval answers right?

- **Eval 1:** Arithmetic is consistent with **all eight supplied rows**, but wrong for an unqualified calendar-Q3 request. The expected answer rewards the period error.
- **Eval 2:** Asking for units and withholding a recommendation is appropriate. The assertion requiring it to “use per-plant only” should be conditional on a later unit-confirmation turn; the initial prompt supplies no unit.
- **Eval 3:** The expected data request follows the workflow. No numerical result can be justified from the prompt.
- **Eval 4:** The stated values check by hand: Room 1 uses **16,300/750 = 21.73 g/sq ft**; Room 2 uses **4,309.124/200 = 21.55**. Dry-down and coverage also match the stated duplicate-retention policy.
- **Eval 5:** The stated arithmetic checks: total dry **19,800 g**; matched dry-down inputs **14,400/65,500**, giving **78.02%**; room yields **22.25** and **21.8**. The historical “pre-fix” behavior cannot be established from the current source.
- **Trigger queries:** No supplied classification contradicts the stated scope. They do not test the close-out request explicitly included in the skill description.

The evals do not cover duplicate headers, overflow after parsing, three-decimal comma ambiguity, missing all yield denominators, or distinguishing missing dry weight from confirmed curing status.

## 3. What I could not check

### Regulatory and traceability claims

No actual state-specific recording deadline, threshold, or waste procedure is established by the supplied references.

| Claim / location | Assessment |
|---|---|
| Harvest wet weight, waste, and packages should tie to state traceability records — `SKILL.md:92`, report-template footer | **COULDN'T-VERIFY.** Requires the jurisdiction’s current primary rules and confirmation that the compared records use compatible material definitions and weighing stages. It is not a demonstrated universal equality rule. |
| Which weights must be recorded, when, and how is state-specific — `SKILL.md:92` | **COULDN'T-VERIFY** for any particular jurisdiction. The text correctly leaves the actual requirements unresolved; no deadline can be supplied from it. |
| Find missing records before closing harvests; unexplained weight is a compliance signal — `SKILL.md:93`, report template, docs example | Operational recommendation, not a cited legal closure requirement. **COULDN'T-VERIFY** if presented as a mandatory regulatory prerequisite. |
| Metrc `GET /packages/v2/adjust/reasons` lists state-specific adjustment reasons — `references/system-mappings.md:49` | **COULDN'T-VERIFY.** Needs current official Metrc API documentation, including version and state applicability. “Seen in the … index” is not a retrievable citation. |
| Package tags are the join key across the listed traceability systems — same reference | **COULDN'T-VERIFY** as a universal claim. Confirm the actual export identifiers and uniqueness; package-level identifiers do not automatically establish harvest-level joins. |
| `4 CCR §15xxx` — `references/output-conventions.md:10` | Explicit placeholder example, **not a verifiable citation**. It must never be copied into a report as authority. |
| `last-compliance-review: "2026-10-16"` and the mapping verification date | **COULDN'T-VERIFY.** The files provide no review record or primary-source evidence supporting these dates. |

### Other limits

- Read the complete identified `SKILL.md`, three referenced reference files, `scripts/yield.py`, report template, two eval JSON files, four CSV fixtures, docs page, and `tests/test_yield.py`.
- The read tool cannot enumerate directories, so I cannot guarantee there are no additional unreferenced files.
- Commit **a46f0fe** could not be independently authenticated from the available repository metadata.
- No script, test, eval, spreadsheet, connector, or live export was executed. Runtime behavior, actual assistant compliance, and spreadsheet formula handling remain untested.
- No web access was available for primary-source checks. No files were modified, and nothing was contacted, posted, or submitted.
