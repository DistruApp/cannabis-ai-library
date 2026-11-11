## 1. Verdict

**Do not release unchanged: the skill can combine different customers’ inventory, inflate orders, and report unsupported stockout and dead-stock facts.**

## 2. Findings

Paths below are relative to `skills/cannabiz-skills/operations/cannabis-replenishment-planner/`, unless otherwise stated. Evidence is quoted source and manual tracing—not execution.

| ID | Severity | File:line | What happens | Evidence | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| R1 | P0 | `scripts/replenish.py:351–354,377–384,512`; `evals/trigger_queries.json:5` | **Different retail accounts are merged.** The skill advertises account-specific replenishment, but neither matching nor output includes an account key. One account’s excess inventory can conceal another’s stockout. | Sales use `sales[sku_key(sku)]`; inventory uses `by_sku[sku_key(sku)]`; output iterates `set(sales) \| set(onhand)`. The positive trigger explicitly requests quantities for “12 dispensary accounts.” See walkthrough B. | READ ONLY | Require separate runs per account, or include account in every aggregation key and output. Stop combined-account inputs until partitioning is confirmed. |
| R2 | P0 | `scripts/replenish.py:359,519–523` | **An established, intermittent seller becomes a “new SKU,” inflating velocity.** First observed sale is treated as the start of availability. | `days = (as_of - s["first"]).days + 1`. An established SKU available throughout the 28-day window, selling one unit on September 30, gets rate **1/day**, not **1/28/day**. With zero stock, seven-day lead and 14-day cover, that means **21 units instead of 1**. | READ ONLY | Shorten the denominator only using a confirmed launch/availability date. Otherwise use the complete observation window and label limited history separately. |
| R3 | P0 | `scripts/replenish.py:81,589–595`; `SKILL.md:44` | **MOQ is incorrectly treated as an order multiple.** This can materially overbuy. | `"moq"` and `"min order qty"` map to `case_pack`, followed by `ceil(qty / cp) * cp`. With demand 1/day, lead 14, cover 14, stock 2 and MOQ 25, need is **26**; the script orders **50**. MOQ alone does not require multiples of 25. | READ ONLY | Separate minimum quantity from pack multiple. Apply the minimum, then any independently confirmed multiple. |
| R4 | P0 | `scripts/replenish.py:481–485,591–595` | **Fractional case packs produce invalid quantities.** All positive fractions are accepted, then the rounded result is truncated. | `qty = int(math.ceil(qty / cp) * cp)`. For need **6**, pack **2.5**, the intermediate result is **7.5**, but output is **7**—not a pack multiple. | READ ONLY | Reject fractional packs for count-based products. For supported weight-based products, preserve decimal quantities and round in the correct unit. |
| R5 | P0 | `scripts/replenish.py:462–505` | **A valid duplicate row overrides an unreadable cost or pack**, contradicting the reported treatment. Lead time has protection against this; cost and pack do not. | After recording `BAD_UNIT_COST` and “order cost left blank,” the parser executes `continue`; later, `rec[field] = vals[0][2] if vals else None`. Duplicate costs `'4,25'` and `'6'` therefore produce cost **6**, not blank. Likewise, an invalid pack plus valid pack still rounds. | READ ONLY | Track invalid status per attribute. An unreadable cost must keep cost unknown; an unreadable pack must prevent rounding unless the operator resolves it. Re-sync the docs’ blanket claim that unreadable duplicates hold orders. |
| R6 | P0 | `scripts/replenish.py:457–458,512` | **An inventory-only SKU with unreadable on-hand disappears from the SKU report and review lists.** | `if good_rows == 0: continue`, followed by output over only `sales` and retained `onhand`. SKU X with on-hand `'inf'` and no sales record gets an input-problem message, but no `NO_ONHAND_RECORD` row or held-SKU entry. | READ ONLY | Preserve invalid inventory records as held records. Build output from every observed SKU, including rejected rows. |
| R7 | P0 | `scripts/replenish.py:573–574`; `references/method.md:24` | **Insufficient history becomes a definitive dead-stock finding.** | `not s or s["last"] is None` immediately generates `DEAD(no sales 30d+)`. A seven-day export with an unsold SKU cannot establish 30 days without sales. Even the default 28-day window is shorter than the default dead-stock threshold. | READ ONLY | Require confirmed export coverage through the threshold. Otherwise report “no sales observed; history insufficient,” not `DEAD`. |
| R8 | P0 | `scripts/replenish.py:656–657`; `SKILL.md:81` | **Unknown dead-stock cost becomes zero dollars.** The required bottom line can substantially understate tied-up cash. | Dead-stock valuation multiplies by `(onhand[k]["unit_cost"] or 0)`. Ten dead units with blank cost contribute **$0**, without a missing-cost count for this metric. | READ ONLY | Report known-cost subtotal plus unvalued SKUs/units. Do not present the subtotal as the complete dead-stock value. |
| R9 | P0 | `references/method.md:22–23`; `SKILL.md:73,111` | **Current zero inventory is used to invent historical stockout duration and understated demand.** | The reference says “Out of stock for at least a week”; the example says “sold out 9/28.” Inputs contain sales dates and an ending count—not stockout timestamps. Selling the last unit just before today’s count also meets the flag condition, without any lost selling days. | READ ONLY | Say “zero on hand; possible stockout-related demand understatement.” Ask for availability history. Never equate last sale with sellout date or recommend increasing quantities solely from this inference. |
| R10 | P0 | `scripts/replenish.py:163–187,232–241,362–363,589–591` | **Finite inputs can still crash the script through arithmetic overflow.** Lead-time parsing also lacks a finite-value check. | Two sales cells of `1e308` each pass `math.isfinite(v)` individually; their sum becomes infinity. With zero stock and a lead time, the reorder path reaches `math.ceil(inf)`, raising `OverflowError`. An extremely long numeric lead-time cell can independently become infinity. | READ ONLY | Validate accumulated and derived values, bound planning parameters, and reject non-finite lead times. Return contextual input errors rather than tracebacks. |
| R11 | P1 | `scripts/replenish.py:424,445–456` | **Blank or absent open-PO information silently means zero.** That can generate duplicate purchasing suggestions. | Records start with `"open_po": 0.0`; blank input yields `(None, None)` and never changes it or records an assumption. At 2/day, stock 5, lead 7, safety 2 and cover 14, the script suggests **41** without rounding; an existing 50-unit PO would instead suppress the order. | READ ONLY | Distinguish confirmed zero from unknown. Ask whether blanks mean zero, or label the zero assumption and withhold a firm purchasing recommendation. |
| R12 | P1 | `scripts/replenish.py:445–456`; `references/method.md:45–47` | **Duplicate inventory rows can double-count a SKU-level open PO.** Summation is only correct when incoming quantities are allocated per row. | `rec["open_po"] += po`. Two bin rows each repeating the same 20-unit SKU-level PO become **40 incoming**, although only 20 were ordered. The instructions do not ask about the export’s grain. | READ ONLY | Confirm whether open PO is per bin/package or repeated per SKU. Aggregate using that meaning; request PO identifiers where necessary. |
| R13 | P1 | `scripts/replenish.py:90–91,159–180,244–251` | **US date and comma conventions are assumed without confirmation.** Some foreign-format values are accepted incorrectly rather than rejected. | `03/09/2026` parses as **March 9**, even if the export means September 3. `_THOUSANDS_RE` accepts `'0,125'` as **125**, although a decimal-comma export can mean **0.125**. | READ ONLY | Confirm export locale/date format before calculation. Reject ambiguous dates and three-digit comma fractions until that convention is known. |
| R14 | P1 | `evals/evals.json:38,45`; `SKILL.md:37` | **Eval 3 gives contradictory permission to assume lead times.** Its expected answer can reward behavior the skill forbids. | Expected output permits quantities once lead times are “provided or explicitly assumed and labeled”; the assertion prohibits “invented lead times.” The skill requires an operator-provided default. | READ ONLY | Replace this with “provided by the operator, including an explicitly authorized default.” Add an assertion rejecting assistant-selected lead times even when labeled assumptions. |

### First-time-customer walkthroughs

All figures below were worked by hand.

#### A. Dispensary: “What should I order this week?”

**Request:** Eval 1’s sales and inventory, counted September 30, 2026; three days safety; lead times and packs in the sheet.

1. **Intake:** Ask once for missing cover/window/threshold preferences and budget. Unspecified values must remain labeled defaults.
2. **Mapping:** Sales map to `Date`, `SKU`, `Units Sold`, `Net Sales`; inventory quantity maps to `Available`. Confirm the mapping.
3. **Calculation:** September 3–30 is 28 days.
   - Blue Dream: `168 ÷ 28 = 6/day`; need `6 × (7+3+14) − 40 = 104`; pack 24 → **120 × $14 = $1,680**.
   - Live resin: `104 ÷ 28`; need approximately **100.286**; integer ceiling then pack 10 → **110 × $18 = $1,980**.
   - Runtz: `22 ÷ 11 = 2/day`; need `2 × (5+3+14) − 10 = 34`; pack 10 → **40 × $24 = $960**.
   - Vendor draft total: **$4,620**. Chocolate needs lead time and vendor. The distillate’s open PO prevents another order. Pre-roll value is **35 × $10 = $350**.
4. **Where following the instructions goes wrong:** The agent is directed to recommend increasing the live-resin quantity and the example supplies a September 28 sellout date. Neither historical stockout duration nor lost demand is established by these files (**R9**).
5. **Final deliverable:** Vendor-grouped **DRAFT, NOT SENT**, missing-data list and assumptions. No vendor contact.

#### B. Brand: “Suggest orders separately for our two retail accounts”

**Inputs:** Same SKU at Example Cedar and Example Harbor. Each sold one unit daily September 3–30. September 30 counts are **0** and **100**, respectively. Same vendor, $10/unit, seven-day lead, pack 1, no safety and 14-day cover.

1. **Intake:** The advertised brand/account use and trigger accept this request. The instructions do not require account partitioning.
2. **Mapping:** An `Account` column has no canonical mapping. Required SKU/date/quantity columns still pass.
3. **Calculation:** The script combines sales to **56/28 = 2/day** and inventory to **100**. Reorder point is **14**, so it suggests **nothing**.
4. **Actual separate-account calculation:** Cedar needs `1 × (7+14) = 21` units, **$210**. Harbor needs zero.
5. **Failure point:** Aggregation by SKU before account identity is retained (**R1**). A compliant-looking “suggested order” report omits Cedar’s need. The workflow must stop for partitioning before calculation.

#### C. Stop/refuse: “Use these exports and email the approved POs”

**Request:** No on-hand count date is supplied.

1. The prescribed invocation without `--as-of` reaches argparse’s required-argument error **before calculation**.
2. Ask for the count date, plus mapping/parameter questions visible from the headers. Do not substitute the last sale or filename date.
3. Refuse the emailing portion. Even after the date and approval arrive, this skill permits only a draft for the buyer to send.
4. No quantity, manually reconstructed comparison, email, portal submission or promise to send later should be produced.

### Additional adversarial-input traces

| Input | Source-level result |
|---|---|
| Sales units `NaN`, `inf`, `'4,25'`, blank or a numeric formula such as `=2+2` | Parser returns no number; the row is reported and omitted. Remaining rows still determine velocity. These are not evaluated as spreadsheet formulas. |
| Revenue `'1.234,56'` | Reported and excluded from revenue, without excluding valid units. |
| On-hand `-3` | SKU is held; no order. |
| Open PO `'TBD'` or negative | SKU is held. Blank instead becomes zero without warning (**R11**). |
| Duplicate sales rows | Both count. Repeating a 6-unit row changes 168 to **174 units**; there is no transaction-ID duplicate check. Identical rows cannot safely be deduplicated without knowing their grain. |
| Duplicate inventory with conflicting costs 12 and 15 | Held. An unreadable cost plus a valid cost instead uses the valid one (**R5**). |
| Blank SKU row | Reported and skipped. Entirely empty physical CSV rows are skipped by `csv.DictReader`. |
| Sales measured in grams; on-hand measured in kilograms | No script unit field or conversion protects the arithmetic. For 10 g/day versus 1 kg on hand, unconverted numbers produce `1 ÷ 10 = 0.1` days instead of **100 days**. The agent must apply the skill’s unit-mismatch stop/conversion instruction before running. |
| Text vendor/product beginning `=`, `+`, `-` or `@` | `csv_safe` prefixes nonnumeric formula-like text with an apostrophe in generated CSVs. No formula evaluation occurs in Python. Spreadsheet behavior itself was not tested. |
| Zero-byte input | Stops with an empty/no-header message. |
| Header-only sales | Detection can return mappings; full calculation stops because no readable sales dates exist. |
| Header-only inventory | Produces no orders, `NO_ONHAND_RECORD` entries for sales SKUs and an empty-inventory warning. |

### Eval expected-answer audit

| Eval | Manual check |
|---|---|
| **1** | Numeric expectations reconcile to **$4,620** as shown above. The stockout-demand interpretation is not established by the data (**R9**). |
| **2** | August 27–September 30 is 35 days. Blue Dream **96 × $14 = $1,344**; live resin **100 × $18 = $1,800**; Runtz **30 × $24 = $720**. Total **$3,864**. Chocolate: `34/35 × 21 − 3 = 17.4`, ceiling **18**, **$162**, correctly outside the vendor draft. |
| **3** | Missing SKU mappings and `On Hand`/`Available` ambiguity are real. Without a count date, the agent must obtain them from header inspection because argparse stops first. Lead-time permission needs correction (**R14**). |
| **4** | Each SKU sells **56/28 = 2/day**. C: need 55 → **60 × $6 = $360**. E: need 41 → **42 × $20 = $840**. H: **41 × $9 = $369**. Total **$1,569**. F is **50 units/$700**, needing a vendor. Holds and six-day warning follow the code. |
| **5** | K and L each retain **54 units/28 days**. Need is approximately **39.357**, giving **40** each. K cost remains unknown; L contributes **$240**. This is a partial dollar subtotal, not complete cash required. N’s net **−5** becomes zero velocity; Q has **400 days** supply. |
| **6** | Required-argument handling supports exit code 2 and the stated missing-date message. The subsequent dated calculation is the same arithmetic as eval 1. |

The trigger eval’s positive multi-account request is unsupported by the calculator (**R1**). The supplied numeric fixtures do not exercise account separation, MOQ semantics, fractional packs, mixed valid/invalid duplicate attributes, or overflow.

## 3. What I could not check

- **Execution:** No commands or tests were run. Exit behavior and calculated outputs above are source-level predictions, labeled **READ ONLY**.
- **Commit identity and exhaustive inventory:** No `.git` metadata was available, and the read tool cannot list directories. I read the three referenced reference files, calculator, both eval JSON files, all eight named fixtures, both templates, docs page, and associated script tests/helpers. I cannot independently prove the snapshot is commit `a46f0fe` or that no unreferenced files exist.
- **Regulatory claims—COULDN’T-VERIFY:**
  - `SKILL.md:99` and the plan template discuss state-specific retesting and label-date limits. No jurisdiction, operative limit or primary text is supplied. Those require the applicable regulator’s current text; neither sales inactivity nor product age establishes legal unsaleability.
  - `references/system-mappings.md:27` asserts the Metrc endpoint `GET /packages/v2/adjust/reasons` and state-specific adjustment reasons. The exact endpoint, availability and claimed review date need official API documentation. An API reason list is not independently sufficient legal authority.
  - The `4 CCR §15xxx` entry in output conventions is a placeholder, not a usable regulatory citation.
- **Other factual boundaries:** Pound/ounce conversions are rounded physical conversions, not cannabis purchase-limit rules. No specific purchase limit or test-validity duration is stated. The metadata’s compliance-review date cannot establish that a primary-source review occurred.
- **Operational behavior:** Actual assistant adherence, spreadsheet formula handling, live POS schemas and vendor lead-time meanings were not tested. Nothing was modified, sent, submitted or posted.
