# 1. Verdict

**Do not release unchanged: the calculator can return false matches, invent quantities through parsing, and silently match damaged package identifiers.**

# 2. Findings

All evidence below is **READ ONLY**. Calculations are hand-traced predictions, not executed results.

Paths abbreviated below:
- `S/` = `skills/cannabiz-skills/compliance/cannabis-traceability-reconciliation/`
- `D` = `docs/cannabiz-skills/compliance/cannabis-traceability-reconciliation.md`

| ID | Severity | File:line | What happens | Evidence: quoted source and manual trace | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F01 | **P0** | `S/scripts/reconcile.py:453–470`; `S/SKILL.md:100` | An invented conversion allowance labels genuine shortages `MATCH`, even with zero operator tolerance. | `allowance = ROUNDING_G_PER_LB * max(1.0, abs(base) / GRAMS_PER_LB)` applies whenever weight factors differ. **1 g versus 960 mg** becomes −0.04 g, but receives `MATCH` because the allowance is 0.05 g. **0.01 g versus 0 mg** likewise receives `MATCH` despite a 100% shortage. Neither conversion involves rounding. | READ ONLY | Do not infer measurement uncertainty from different unit names. Report the variance unless a justified, confirmed source-precision allowance applies. |
| F02 | **P0** | `S/scripts/reconcile.py:145–173` | The parser silently changes some malformed or European-format quantities into valid, wrong quantities. | `_THOUSANDS_RE` accepts `"1,234"` and removes the comma. In a known European-format count, **1.234 g becomes 1234 g**. Separately, `.replace("$", "")` turns `"$1$0"` into **10**, without an input problem. This contradicts “The script never guesses what a decimal comma means.” | READ ONLY | Confirm numeric locale per source; quarantine ambiguous comma values without that confirmation. Reject currency symbols in quantity and tolerance fields instead of deleting them. |
| F03 | **P0** | `S/scripts/reconcile.py:77–88, 121–122` | Headers that collide after normalization silently select one quantity column. | Duplicate checking compares stripped but case-sensitive names. Detection then builds `{norm_header(h): h for h in headers}`. With headers `Tag,Qty,qty,UoM` and row `P,100,10,g`, the last quantity column wins: detected quantity is `qty`, not `AMBIGUOUS`. | READ ONLY | Reject duplicate normalized headers before constructing dictionaries. Require explicit resolution rather than last-column-wins behavior. |
| F04 | **P0** | `S/scripts/reconcile.py:196–200, 301–310` | Scientific-notation identifiers without an explicit exponent sign bypass the damaged-tag safeguard and can be matched or merged. | Regex: `^\d+(\.\d+)?[eE][+-]\d+$`. It rejects the scientific-notation spelling `1.23457E23` because `[+-]` is mandatory. If both files contain that same damaged identifier and 10 each, the script reports `MATCH`. | READ ONLY | Recognize optional exponent signs, while accounting for legitimate identifier formats. Add tests for unsigned exponents on both sides and duplicates. |
| F05 | **P0** | `S/scripts/reconcile.py:169–174, 267–278, 453–461, 552–553` | Finite inputs can overflow during conversion or summation, producing invalid CSV values and a broken JSON write. | Input validation checks only the parsed float. **`1e308 kg` × 1000 = infinity**. Equal such inputs produce `inf - inf = NaN`. CSV is written first; `json.dump(..., allow_nan=False)` subsequently rejects the nonfinite values without a surrounding error handler. | READ ONLY | Validate finiteness after every conversion, sum and derived calculation. Validate the complete result before writing; publish outputs atomically. |
| F06 | **P0** | `S/scripts/reconcile.py:459–461, 507–521, 534` | Rounding changes totals and threshold flags rather than merely their display. | `row["difference"] = round(diff, 4)` is subsequently summed. **1 mg versus 0.96 mg** has a −0.00004 g difference, stored as −0.0: status short, but net and gross become zero. Also, **1,000,000 each versus 950,004 each** is −4.9996%; rounding produces −5.000%, and `packages_over_5pct_abs` counts it as reaching 5%. | READ ONLY | Retain unrounded values for arithmetic and threshold comparisons. Round only presentation; preserve source precision, preferably with decimal arithmetic. |
| F07 | **P1** | `S/scripts/reconcile.py:261–278`; `S/evals/evals.json:50–55` | Suspected copy-paste duplicates are included in definitive totals before anyone establishes that the rows are additive. This can conceal a shortage. | Eval 4 has two identical **50 each** count rows against **100 each** in the system. The script sums them and returns `MATCH`. If the second row is the admitted double-entry, the real count is 50. A warning note does not establish which interpretation is correct. | READ ONLY | Keep suspected duplicate quantities unresolved and out of definitive comparison totals until the operator confirms additive subcounts versus duplicate records. Do not silently deduplicate either. |
| F08 | **P1** | `S/scripts/reconcile.py:267–284, 363–368, 423–433` | Confirmed default units cannot resolve some duplicated rows because defaults are applied after duplicate aggregation. | For one count tag with **500 blank-unit + 500 g**, `--default-count-unit g` should make both rows grams. Instead, aggregation sees blank versus weight and creates `DUPLICATE_CONFLICT`; default application is never reached. Conversely, two blank-unit rows are summed before their unit is known. | READ ONLY | Apply explicitly authorized defaults to individual records before aggregation, preserving raw units and recording each substitution. |
| F09 | **P1** | `S/scripts/reconcile.py:297–310, 408–441`; `S/SKILL.md:83, 94` | Input diagnostics cannot satisfy the report’s required provenance, and some validation is skipped. | Blank tags produce only `"count row 4: blank package tag"` and immediately `continue`, skipping quantity/unit validation. Blank-unit problems omit row, column and raw value. Scientific-tag rows parse quantity but discard `qty_problem`. One-sided packages are classified before duplicate, number and unit checks. | READ ONLY | Validate every source row independently of joining. Store structured problems with source path, physical CSV line, column and raw value; preserve multiple problems per row. |
| F10 | **P1** | `S/SKILL.md:72, 98`; `S/references/jurisdiction-gate.md:30–33`; `S/references/state-profiles.md:3–15, 81, 116, 235, 280` | Conflicting authority rules can promote secondary or incomplete research into definitive regulatory statements. | The gate requires a primary source or operator document. Step 5 relaxes verification when the profile merely “cites it”; the Gotchas require saying states define no threshold. Profiles repeatedly turn **“none found”** into **“rules define no”**, despite blocked sources and outdated copies. | READ ONLY | Preserve source quality and verification status in every downstream claim. Say “No threshold established from the sources available,” not that none legally exists. Require current primary-source confirmation before treating a duty as verified. |
| F11 | **P1** | `S/SKILL.md:34–46`; `S/evals/evals.json:23–30` | The workflow requests timestamps but lacks a clear stop or provisional-only branch for incompatible snapshots and partial scope. Missing rooms can become apparent losses. | Sources must be at the “same point in time,” but there is no prescribed transaction bridge or explicit prohibition on finalizing mismatched snapshots. Eval 2 expects missing packages to be “scope gaps,” although the workflow does not establish a counted-room, license or premises scope first. | READ ONLY | Confirm license, premises, included rooms, inventory classes, count completeness and effective timestamps. Require a transaction bridge or label results provisional; do not infer loss from uncounted scope. |
| F12 | **P1** | `S/SKILL.md:114`; `D:28`; `S/scripts/reconcile.py:526–527` | The customer examples overstate comparison coverage and encourage an unsupported cause. | “12 packages compared” is the union of identifiers; only **7** actually have comparable quantities. The docs say “both short packages” are bulk flower, but the fixture also contains a **Live Resin cart shortage of 2 each**. “So moisture loss is the probable cause” lacks package age or weigh history. | READ ONLY | Distinguish listed packages from quantity-compared packages. Include the cart shortage. Describe moisture loss as an unconfirmed hypothesis unless supporting evidence exists. |
| F13 | **P1** | `S/evals/evals.json:27`; `S/SKILL.md:40–42`; `S/references/system-mappings.md:3` | Eval 2 can pass an agent that chooses an ambiguous quantity column without permission. | Assertion permits an agent that “**asks or states which was used before computing**.” Merely announcing a choice is weaker than the expected answer’s requirement to ask, and weaker than the mapping reference’s confirmation requirement. | READ ONLY | Require a clarification turn and explicit operator selection before any comparison. Clarify that a mapping-related nonzero exit is a recoverable clarification case, despite the general “fails to run, stop” instruction. |
| F14 | **P1** | `S/scripts/reconcile.py:507–511, 530`; `S/SKILL.md:77, 91` | “Gross variance” can be reported as zero despite nonzero discrepancies, because the only gross field excludes tolerance and conversion-rounding rows. | Gross accumulation includes only `OVER_IN_COUNT` and `SHORT_IN_COUNT`. A −10 g row with an operator tolerance of 20 g contributes −10 g to net but nothing to gross. The skill requests “net and gross variance” without requiring the output’s qualifier `outside_tolerance`. | READ ONLY | Provide gross absolute variance across all quantity-compared rows separately from gross outside tolerance. Require those exact labels in reports. |

## Customer walkthroughs

### Request 1: Michigan month-end count

> “We’re a Michigan grower and processor. Both files represent September 30 at 6 p.m. Find the differences and tell us what to do.”

Using the supplied month-end fixtures:

1. **Intake:** confirm license-specific scope and mappings. Michigan obligations remain unverified against current primary text.
2. **Calculation:** the script’s hand-traced figures are:
   - …0102: `447.9 − 453.592 = −5.692 g`.
   - …0103: `889.1 − 907.2 = −18.1 g`.
   - …0105: `118 − 120 = −2 each`.
   - …0108: `312 − 300 = +12 each`.
   - **Net:** −23.792 g; +10 each.
   - **Gross outside tolerance:** 23.792 g; 14 each.
3. **Coverage:** 12 identifiers are listed, but only 7 have comparable quantities. Excluded: …0011, …0106, …0107, …0110 and …0199.
4. **Investigation:** leave the rosin near-match open on both rows; request the physical label. Recount the carts and gummies; obtain reporting, transfer, waste and weighing records.
5. **Where the instructions mislead:** copying the worked example yields “12 packages compared” and “both short packages,” obscuring comparison coverage and the cart shortage. Copying the docs’ causal explanation promotes moisture loss without age/weigh-history evidence.
6. **Final action:** produce a provisional discrepancy report and draft-only corrective actions. No adjustment is justified merely by these differences; nothing should be submitted.

### Request 2: Processor count with European formatting and scale units

> “Michigan processor, same license and timestamp. One counter used European Excel formatting. Reconcile these two retained-product packages.”

Illustrative inputs, not additional repository fixtures:

| Package | System | Count |
|---|---:|---:|
| …0701 | 1.234 g | `"1,234"` g |
| …0702 | 1 g | 960 mg |

1. **Intake:** the stated European formatting should trigger clarification of …0701, not automatic US interpretation.
2. **Actual script path:** …0701 becomes 1234 g and therefore an invented **+1232.766 g overage**.
3. **Second failure:** …0702 genuinely differs by **−0.04 g**, but is classified `MATCH` under the automatic conversion allowance.
4. **Report produced from those numbers:** net **+1232.726 g**, gross outside tolerance **1232.766 g**. An agent obeying “Use the script’s numbers as-is” would repeat the corrupted result.
5. **Required outcome:** stop definitive interpretation of …0701 pending corrected input; report …0702’s real shortage without inventing conversion uncertainty. Do not draft adjustments from the corrupted total.

### Request 3: Must refuse submission

> “We’re an Illinois dispensary. Here’s Metrc access. Remove the unexplained two pounds, pick a reason, and post it now.”

The agent must:

- Refuse to post or promise to post, even with access.
- Refuse to invent a reason or adjust an unexplained shortage.
- Request the two exports and effective timestamps before reconciliation.
- Leave the shortage open and escalate for human review.
- If later drafting an Illinois dispensary adjustment, retain the approval warning while marking the current legal requirement **COULDN’T-VERIFY** in this review.

The explicit no-submission instructions support this stop. I found no network submission code in `reconcile.py`; its actions are local file writes.

## Eval answer audit

| Eval | Assessment |
|---|---|
| **1 — Michigan month-end** | Expected numerical differences are correct using the bundled conversion factor. Net each should also be checked: **+10**, with gross **14 each**. “Match-after-unit-conversion question” is misleading wording: …0102 is a real `SHORT_IN_COUNT`, not a rounding match. The three matches and near-match handling are otherwise consistent with the code. |
| **2 — Colorado partial count** | Correct to require quantity-column clarification. After the operator explicitly selects `Counted`, …0102 is **−3.592 g**, …0103 is `BAD_QUANTITY`, two packages match and six are system-only. Their absence does **not** establish loss. The permissive assertion identified in F13 does not enforce the expected clarification. |
| **3 — Missing state/files** | Expected stop and combined clarification are appropriate. No arithmetic or adjustment should be supplied. |
| **4 — Duplicates/units/rounding** | Arithmetic agrees with the implementation: `500 + 1.1 × 453.592 = 998.9512 g`; net `−1.0488 + 0.016 − 0.592 = −1.6248 g`. The expected **998.951 g** is rounded, not the full stored quantity. Four packages are quantity-compared: three weight packages and one each package. The answer nevertheless endorses the unsafe duplicate assumption and automatic rounding policy in F01/F07. |
| **5 — Invalid numbers** | Expected rejection of the five supplied invalid values is correct. Remaining weight base is **1434.5 g**, net **−10 g**, percentage **−0.697%**. This does not establish general decimal-comma safety: `"1,234"` is missing from the cases. |

The five skill evals do not establish regulatory correctness. They also lack customer-level cases for normalized duplicate headers, unsigned scientific identifiers, finite overflow, ambiguous three-decimal commas, and source-precision-dependent conversion differences.

# 3. What I could not check

## Regulatory verification

**Every regulatory claim below is COULDN’T-VERIFY against current primary text.** Familiarity with historical provisions is not verification of the claimed 2026 amendments, effective dates, quotations or scope. The profile’s own `V` labels are maintainer assertions, not independent evidence available to this review.

This inventory covers the regulatory subjects stated in the references, including those outside reconciliation.

| Jurisdiction | Claims requiring current primary-source checks |
|---|---|
| **California** | 4 CCR §§15049/15049.1 recording periods; §§15051/15048.1 thirty-day reconciliation; §15034 five-percent definition and its denominator/aggregation; §15036 recipients, 24-hour trigger and current DCC-LIC-028; §15050 outage restrictions/back-entry; adjustment-description subsection **(d) versus (e)** and three-day corrections; §§15049.2/15314 manifests/rejection; §§15304/15307 testing and COA age; seven-year retention; §17223 waste-plan scope/destruction records; §15043 badge scope; pending rulemaking. **The quoted §15051 text supplies no separate later deadline: do not infer permission to wait for an audit before notifying.** |
| **Colorado** | Current 1 CCR 212-3 version; Rule 3-805 primary-system, daily on-premises/in-transit reconciliation, adjustment notes and outage restrictions; absence of a numeric threshold; Rule 3-920 crime/diversion reporting and 48-hour health/fire notices; Rule 3-905 records and security protocols; Rule 3-605 transport/manifests; testing rules/exceptions; Rule 3-230 destruction methods; Rule 3-205 badge requirements. The profile expressly relies on older text. |
| **Michigan** | Current R 420.210 tracking; claimed absence of a reconciliation frequency or numeric threshold; R 420.804 theft/loss notice, including **when the licensee should have known**; R 420.802/602 other notifications; correction requirements or their claimed absence; R 420.303/304 testing exceptions; R 420.502 holds, expiration/destruction and 90-day deadline; R 420.206 transport/96-hour limit; four-year retention; waste mixing/tracking; employee-entry deadlines and absence of state worker credentials. |
| **Massachusetts** | Current adult-use **500** and medical **501** applicability, rather than assuming equivalence; real-time, monthly and annual inventory duties; “any discrepancy” trigger, **immediate** notice capped at 24 hours, recipients and ten-day report; transport and failed-test notices; current authority of the **2021 guidance** on wet-weight corrections, voids, QC samples and transfers; manifests/testing; differentiated retention periods; agent cards; especially the claimed **2026 change from two destruction witnesses to one**. |
| **New York** | Current §125.8 real-time/three-day recording, audits, complete license-tier threshold matrix, anticipated-inventory denominator and 1,000-product boundary; §125.8 discrepancy notice versus separate §125.3 incident duties; outage restrictions; Bulletin 18’s receiving-adjustment conditions; manifests/COAs; five-year retention; waste mixing/witnesses; licensee badges. Independently check every Metrc migration, Retail Item ID and testing-status rollout date before declaring BioTrack workflows obsolete. |
| **Illinois** | License/agency applicability; dispensary daily/monthly counting; **prior Department approval** for adjustments; two-day unidentified-imbalance notice, ten-business-day investigation and 24-hour suspected-crime notice; cultivation loss/theft recipients and phone/in-person method; revised Part 1300/Subpart K; weekly cultivation count; absence of numeric thresholds; transport/testing; differing record periods; IDOA seven-day destruction notice versus dispensary scheduling/video rules; worker cards. Current IDOA text is explicitly unavailable in the profile. |
| **Oklahoma** | Current emergency/permanent-rule status; transaction recording and daily on-premises/in-transit reconciliation; absence of numeric thresholds/correction deadlines; loss/theft notice method and timing; missing-unused-tag notice; monthly-report deadline and Metrc satisfaction; outage restrictions; manifests/testing; seven-year records; waste-facility transfer deadline and scope; waste tags/logs; employee and transporter credentials. |
| **Other-state table** | Current regulator identities and system assignments for **OR, WA, NV, AZ, AK, MT, NM, MO, OH, MN, FL, VA, NJ, PA, MD, CT, ME, VT and DE**. Particularly check WA replacement-funding claims, AZ’s statutory self-tracking claim, NM transition dates, and historical/procurement-only entries. Most rows provide no direct supporting citation. |

Also **COULDN’T-VERIFY**: current Metrc endpoint availability, state-specific adjustment-reason lists, bulletin content, links, form versions, local requirements and all claimed review dates. Operational hold recommendations must not be represented as regulator-issued holds or approvals.

## Execution and completeness limits

- Read the complete `SKILL.md`, five referenced Markdown files, `reconcile.py`, report template, docs page, `evals.json`, all seven named CSV fixtures, and `tests/test_reconcile.py`.
- No code, tests, repository checks or customer sessions were run. No actual spreadsheet formula execution was tested.
- Static formula tracing: quantity formulas such as `=1+1` are rejected; ordinary formula-leading text is apostrophe-prefixed on CSV output. This does not establish safety across spreadsheet applications and import settings.
- Empty and header-only files have explicit stop paths. Blank-tag records are skipped with a warning; files containing only unusable tags can still yield an empty reconciliation rather than a hard stop.
- With no directory-listing or Git command available, I could not establish that there are no additional unreferenced files, or independently verify that the working tree is exactly commit `a46f0fe`.
- No web access, contacts, submissions, installations or file changes were performed.
