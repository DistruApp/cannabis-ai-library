# Real-data trial, 2026-11-11

Question: do the skills give the right answer on real Distru data, checked against expected answers written down before the agent ran?

Account: the Distru test company "Peanut Butter Banana" (an anonymised copy: product, vendor and location names are random words). NY, Metrc, timezone America/Los_Angeles, admin user. Licences: one cultivator, one processor and one distributor licence (numbers omitted here). Today 2026-11-11.

## Method

1. **Survey (read-only).** Only `distru-get-*`, `distru-search-*`, `distru-report-*` and `distru-read-file` were called, by me and by the one live-MCP agent run. No Distru write of any kind. Large MCP results were saved to disk by the harness and processed with Python/jq, so the exports are exact copies of what Distru returned, not retyped.
2. **Expected answer first.** For each case, `expected.md` in the case folder was written before any agent ran: the MCP calls, row counts and arithmetic. Oracles were computed with my own short Python (`oracle/` in each data case) or by hand from the skill's documented method and the NY rows of `state-profiles.md`. No `skills/**/scripts/*.py` was run to make an oracle.
3. **Cases.** `plugin-evals/trial/<skill>/<case>/`, same format as `plugin-evals/behaviour`: `prompt.md` with front matter (tag `trial`), `case.yaml` + `setup.sh` (copies only the top-level CSVs from `resources/`, never `resources/raw/`), `graders/` with regexes for the exact expected figures and identifiers plus an `llm` rubric built from `expected.md`. Generator: `plugin-evals/trial/build_trial.py`.
4. **Data handling.** Raw exports and the CSVs built from them sit in `plugin-evals/trial/**/resources/` (plus `oracle/*.json`), gitignored: test-account data stays out of the public repo (decided 2026-11-11). The case folders under `plugin-evals/trial/` stay local too, because their prompts name the test account's licences. `expected.md` files and graders keep numbers, package tags, SKU/product names and batch IDs; vendor names are replaced by "Vendor A-E". Only this report is committed. No personal emails or tokens in any file.
5. **Run.** After the triage agent's confirm runs finished (`confirm2.sh`, then its follow-on `confirm3.sh`):
   `claude plugin eval . --eval-dir plugin-evals --tag trial --model sonnet --judge-model opus --ablation none --no-publish --trust-plugin --scaffold --allow-tools Bash --runs 2 -j 2 --threshold 0 --max-cost-usd 40 --json plugin-evals/results/trial/trial.json --report plugin-evals/results/trial/trial.html`
   `distru-expiring-inventory` can't attach the claude.ai Distru connector under `claude plugin eval`, so it ran once as a fresh general-purpose subagent with the Distru MCP tools, a customer-style request, the plugin-path line and the read-only rule. That run tests **behaviour, not triggering**.
6. **Failure classes.** SKILL DEFECT, GRADER WRONG, ORACLE WRONG, DATA LIMIT (and JUDGE ERROR for an API failure in the judge).

## Results at a glance

Eval run: 2026-11-11 15:36Z, 375 s, Claude Code 2.1.322, agent model sonnet, judge opus, 2 runs per case. Raw results: `plugin-evals/results/trial/trial.json`, `trial.html`, final replies in `plugin-evals/results/trial/evidence/` (gitignored).

| Skill | Case | Evidence | Run 0 | Run 1 | Verdict |
|---|---|---|---|---|---|
| cannabis-traceability-reconciliation | t1-ny-proc-distru-vs-metrc | RUN | 0.818 (FAIL: zero-qty-31, rubric) | 1.0 | 1 of 2 fully correct. SKILL DEFECT (minor) |
| cannabis-replenishment-planner | t1-merch-reorder-90d | RUN | 1.0 | 1.0 | PASS |
| distru-expiring-inventory | t1-live-mcp-expiring-60d | RUN (1 run, behaviour only) | PASS | n/a | PASS |
| cannabis-state-rules-lookup | t1-ny-discrepancy-threshold | RUN | 1.0 | 1.0 | PASS |
| cannabis-state-rules-lookup | t2-ny-distributor-to-dispensary-transfer | RUN | 1.0 | 1.0 | PASS |
| cannabis-inspection-readiness | t1-ny-ocm-routine-inspection | RUN | 1.0 | 1.0 | PASS |
| cannabis-sop-generator-trainer | t1-ny-waste-destruction-sop | RUN | 0.833 (rubric) | 0.833 (rubric) | PASS on behaviour; ORACLE WRONG |
| staff-scheduling-optimizer | t1-packaging-week | RUN | 1.0 | 1.0 | PASS |
| staff-scheduling-optimizer | t2-wednesday-callout | RUN | 1.0 | 1.0 | PASS |
| cannabis-manifest-precheck | none | NOT TESTED | | | DATA LIMIT |
| cannabis-harvest-yield (harvest outputs) | none | NOT TESTED | | | DATA LIMIT |
| batch COGS | none | NOT TESTED | | | DATA LIMIT |

Every failed grader was read against the final reply. Every passing case was spot-checked by hand against `expected.md`: the numbers in the replies are the numbers in the oracle, not only regex hits.

## Per skill

### cannabis-traceability-reconciliation: t1-ny-proc-distru-vs-metrc

**Data.** `distru-search-metrc-packages` for the processor licence, 3 calls (2 pages ascending plus a descending page of 100 to get the tail onto disk), 243 unique active Metrc packages. `distru-search-packages` distruStatuses ACTIVE on the same licence, 96 rows. Both reshaped into the CSVs a customer would export (Metrc: tag, item, quantity, UoM, lab state, ...; Distru: package label, product, SKU, quantity, unit, location, batch, status). Raw pulls in `resources/raw/`.

**Expected.** 96 matched, all with 0 difference. 147 Metrc-only, 0 Distru-only. The 147 are 103 gram packages (787,137.8999 g), 13 each packages (9,825 units) and 31 zero-quantity packages (tags ...0153 to ...0183) that should be listed separately, not counted as missing inventory. Metrc total 1,043,726.6011 g and 19,205 units. 24-hour OCM notice if a significant discrepancy is confirmed (9 NYCRR 125.8(e)), threshold basis undefined, nothing submitted. Of the 147, 59 exist in Distru under a non-ACTIVE status (on sales orders or assembling) and 88 were never imported: a scope question before a shortage question.

**Results.**
- Run 1: every figure correct, zero-quantity packages separated, scope gap raised first. 1.0.
- Run 0: 96 / 147 / 787,137.9 g / 9,825 units / net 0 all correct, and it asked the right first question (re-pull Distru with all statuses). It did **not** separate the 31 zero-quantity packages: it described the 147 as "134 gram packages and 13 each packages" (134 = 103 + 31) and listed the zero-quantity tags inside the unexplained shortage group. Graders `zero-qty-31` and `rubric` failed.

**Classification: SKILL DEFECT (minor, intermittent).** `SKILL.md` line 107 tells the agent to list zero-quantity active packages separately, but `scripts/reconcile.py` has no zero-quantity flag or summary field, so the agent has to notice them by hand from `reconciliation.csv`. It did so in 1 of 2 runs. Suggested fix (not applied): have `reconcile.py` set a `zero_quantity` note on `IN_SYSTEM_NOT_COUNTED` rows with quantity 0 and count them in `summary.json`.

Also seen (not graded): both runs flagged that all 243 Metrc packages are `NotSubmitted` for lab testing, so under OCM's Metrc plan none can leave the processor. That is a real finding about this account. Run 1 inferred that "Distru stopped syncing after 11/02", labelled probable; the Distru data contradicts it (the later packages are on sales orders), but it was labelled as an inference, not a fact.

### cannabis-replenishment-planner: t1-merch-reorder-90d

**Data.** `distru-report-sales-orders` line items for 2025-11-11 to 2026-11-10 (446 lines kept for the 17 SKUs in scope), `distru-report-inventory-velocity` (2 calls) for on-hand and cross-checks, `distru-report-inventory-valuation` for unit cost (blank for every SKU in scope). Lead times are mine (21 days for one vendor, 14 for the rest), stated in the prompt.

**Expected.** 90-day velocity, 7 days safety stock, 30 days cover. 8 reorders, 798 units, 5 vendors: Aquamarine Pepper Gentle 260, Crimson Breezy Mustard 116, Cozy Magenta Tomato 101, Bronze Cherry Mellow 97, Plum Strange Chocolate 97, Bubbly Bronze Spaghetti 57, Cheerful Mango Purple 37, Purple Dreamy Ginger 33. Daring Azure Croissant not reordered (44 on hand above reorder point 42). Dead stock: Curry Gray Hearty, Pecan White Serene, Patient Onion Violet, Pineapple Cosmic Plum, Strawberry Sunny Plum. New SKUs: Avocado Focused Lilac, Violet Graceful Melon. No PO dollars because unit cost is blank. Cross-check: my 365-day line totals equal Distru's velocity report exactly, and my 90-day units/day equal Distru's `averageDailySold90` for every SKU except the two new ones.

**Results.** Both runs 1.0. Run 0 checked by hand: all 8 quantities, the 5-vendor grouping, the Daring Azure Croissant near-miss, all 5 dead-stock SKUs, both new SKUs, "no dollars without unit cost", and no PO sent. It also raised two fair data questions (no sales in the last 7 days; one large SKU's demand rests on 11 order lines).

Note for Distru product: Distru's own reorder status disagrees with the skill on purpose (Distru blends 30/365-day rates and uses a 95% service-level reorder point, e.g. Daring Azure Croissant is ORDER_NOW with reorder point 190 in Distru). Neither is wrong; a customer comparing the two will see different answers.

### distru-expiring-inventory: t1-live-mcp-expiring-60d

**Data.** Live MCP, no files. Oracle from `distru-search-packages` ACTIVE sorted by expiry both ways (175 active, 60 dated) and `distru-search-batches` (388 batches, 353 stocked, 15 dated).

**Expected.** Already expired and still in stock: packages Gray Croissant Ancient 460 Unit (5 packages, 2026-08-11) and Stellar Ginger Garnet 3 Unit (2026-06-05); batches Oatmeal Plum Calm 750 Unit, Crimson Bagel Wild 10,000 Unit, Melon Black Royal 1,146 oz and 4,391.0007 oz, Sesame Cobalt Lucky 9,700.0044 g. Expiring within 60 days: Epic Gold Peanut 238.2 oz (2027-01-01) and Ruby Curious Vanilla 758.38 oz (2027-01-02). No package expires in the window. 115 of 175 active packages and 338 of 353 stocked batches have no expiry date, which means unknown, not safe.

**Results.** RUN, 1 run, PASS. This tests behaviour, not triggering: `claude plugin eval` cannot attach the claude.ai Distru connector, so it ran as a fresh subagent with the Distru MCP tools, a customer-style request, the plugin path and the read-only rule. 26 tool calls, all read-only (`get-me`, `search-packages` x2, `search-batches` x4, `search-products`). Every expired and expiring item matched, undated stock was flagged as not tracked, and its list-price value ($8,087.50) checks against `distru-report-inventory-valuation`. One wording issue, not a wrong number: it searched ACTIVE plus ON_HOLD, ASSEMBLING, SELLING and RETURNING (14,633 packages), so its "fewer than 1% of packages have an expiry date" uses a base that includes stock already on sales orders; within ACTIVE stock it is 60 of 175. Run record: `plugin-evals/trial/distru-expiring-inventory/t1-live-mcp-expiring-60d/resources/run-1-subagent-report.md`.

### cannabis-state-rules-lookup: t1 and t2

**Data.** No Distru data needed beyond the account's licences (`distru-search-licenses`). Oracle from the NY rows of `state-profiles.md`.

**Expected.** t1: a 3% count shortfall at a processor that also holds a cultivator licence is below the 5% processor threshold, but reportable within 24 hours if the cultivator licence is 2%-tier (Tier 3-5), so the answer is "depends, ask the tier"; the base (weight, count, package) is undefined; LII source marked NEEDS VERIFICATION. t2: distributor-to-dispensary transfer needs Retail Item ID QR on each unit, TestPassed/RetestPassed in Metrc, the manifest generated before the vehicle leaves, and the COA with the product; secondary sources marked for verification.

**Results.** Both cases 1.0 on both runs. Spot-checked: both answers give the conditional threshold and the 24-hour clock (t1) and all four transfer requirements with sources and verification labels (t2). Neither invented a citation.

### cannabis-inspection-readiness: t1-ny-ocm-routine-inspection

**Expected.** With no records supplied, nothing can be called Ready; every area Unknown until evidence is shown; monthly inventory audit (9 NYCRR 125.8(d)) flagged as a probable gap because the last full count was September; working-day countdown to 11/19; nothing sent to OCM.

**Results.** 1.0 on both runs. Spot-checked run 0: 8 calendar / 5 working days, 0 Ready, 1 probable gap (monthly audit), physical count by 11/13, NEEDS VERIFICATION on the LII cite.

### cannabis-sop-generator-trainer: t1-ny-waste-destruction-sop

**Expected (mine).** A NY waste-destruction SOP from the operator's notes plus the training packet (quick reference, comprehension check with key, pass rule, sign-off log) in the same reply.

**Results.** 0.833 on both runs; only the `rubric` grader failed, and only because the training packet was missing. Both runs drafted the SOP correctly (steps in order, a cannot-be-undone warning before mixing, CONFIRM on every citation, the 50% figure and the retention period, nothing invented) and then stopped to ask who approved it before building training.

**Classification: ORACLE WRONG.** The skill deliberately builds training only after the SOP is approved (`SKILL.md` lines 29 and 107). My expected answer and rubric demanded both in one turn. The case needs a second turn ("approved by the compliance manager, no edits") before the packet can be graded. Not a skill defect.

### staff-scheduling-optimizer: t1 and t2

**Data.** Synthetic roster (no scheduling data in Distru): `resources/packaging_roster_week_2026-11-16.csv`, 10 people.

**Expected.** t1: 6/6/8/8/4 packagers, 256 packager-hours, 288 assigned hours, Friday lead is an OPEN GAP (Ana on PTO, Ben Mon-Wed only), cost $5,312-$5,344 assigned, under the $6,000 budget, no NY worker permit invented. t2: Faye out Wednesday, Ben K. is the only legal cover (8 of 24 h), cost $5,568, $432 under budget.

**Results.** All four runs 1.0. Spot-checked: t1 run 0 is the cheapest valid plan ($5,312, Ben leads Mon-Wed). t1 run 1 used Ana for all four lead days ($768 instead of $744), inside the expected range, but its stated reason ("Ben's lead rate is above the packager rate") compares the wrong rates. Not a defect; worth a line in the skill's cost-optimisation guidance if it recurs. t2 runs both chose Ben, $5,568, and flagged that Wednesday then has no backup.

## What this account couldn't test

| Skill / area | Evidence (read-only calls) | Class |
|---|---|---|
| Manifest precheck | `distru-search-metrc-manifests`: 4 rows, 3 manifest numbers (...4546, ...4547, ...4548), all UNIMPORTED, none matched to a sales order; `distru-report-sales-orders` with `matchedWithComplianceTransfer=true`: 0 orders | DATA LIMIT |
| Harvest yield | `distru-search-harvests`: 100 harvests, all DRYING, 0 FINISHED; `distru-report-harvest-outputs` over 365 days: 0 rows | DATA LIMIT |
| Batch COGS / assembly cost | `distru-search-assemblies`: 0 COMPLETED (25 PENDING, cost null); `distru-report-cogs` 365 days: 101 lines, 3 with any cost, none cannabis (`plugin-evals/trial/not-testable/resources/raw/cogs_365.json`) | DATA LIMIT |
| PO dollars in replenishment | `distru-report-inventory-valuation`: unit cost blank for all 17 SKUs in scope | DATA LIMIT (quantities tested, dollars not) |
| Triggering of distru-expiring-inventory | Connector can't attach under `claude plugin eval` | Behaviour tested, triggering NOT TESTED |

## Things that changed during the trial

The NY state profile changed at about 12:20 local, after the oracles were written (about 11:20) and before the eval run (12:36). It added processor rows (9 NYCRR 123.6(h)(1) testing before distribution, and the OCM Metrc plan rule that processors need TestPassed/RetestPassed before anything leaves, from 2025-12-17). All four copies of the profile are identical. No expected figure changes; the trace runs used the new rule to flag that all 243 Metrc packages are `NotSubmitted`.

## Cost

| Item | Cost |
|---|---|
| `claude plugin eval`, 8 cases x 2 runs, agent (sonnet) | $3.78 |
| Judge (opus) | $1.32 |
| **Eval total** | **$5.10** (budget $40) |
| distru-expiring-inventory subagent run | about 197k tokens, 26 tool calls, 198 s; dollar cost not reported by the harness |
| Survey and oracle work (this agent) | not metered separately |

## Open questions

1. ~~May exports from the test account go into the public repo?~~ Decided 2026-11-11: no. `plugin-evals/trial/` stays local, so the trace and replenishment cases can't run on a fresh clone.
2. The SOP case needs a 2-turn format (draft, then "approved") to grade the training packet. Does `claude plugin eval` support a scripted second user turn, or should the packet be a separate case that supplies an approved SOP?
3. `oracle/build_replen.py` holds vendor names from the test account (random words). It stays local (see 1).
4. Should `reconcile.py` flag zero-quantity packages itself (the defect above), or is a stronger line in `SKILL.md` enough?
5. Distru exports "Unit" where Metrc says "Each"; the trace script treated them as equal and matched all 7 such packages. Worth adding to the skill's documented unit aliases so it doesn't depend on the script's current behaviour.
