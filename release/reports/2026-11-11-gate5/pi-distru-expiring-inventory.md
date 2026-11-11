# 1. Verdict

**HOLD: the prescribed reference dashboard contradicts the skill’s date, valuation, buyer-evidence and drafting rules; copying it can produce incorrect numbers and offers.**

This is a static review, not a run. Findings about dashboard behavior concern the bundled reference code—not a customer dashboard that I executed.

# 2. Findings

Paths below are relative to `skills/distru-skills/distru-expiring-inventory/`, except the explicitly named docs page. Evidence consists of quoted source and hand calculations; no commands were executed.

| ID | Severity | File:line | What happens | Evidence | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F1 | **P0** | `assets/expiring-inventory-dashboard.html:208, 247–251` | The default window includes already-expired stock from earlier in the current month and omits the final partial month. It is six calendar labels, not today through six months ahead inclusive. | `monthsAhead(n)` generates `d3.range(n)` starting at the current month; filtering compares only `r.month >= first && r.month <= last`. On November 5, six months therefore means November–April, rather than November 5–May 5. This contradicts `references/workflow.md:13–16`. | READ ONLY | Calculate company-local inclusive date bounds, clamp month ends, filter individual lots by date, then generate all intersecting month labels. |
| F2 | **P0** | `assets/expiring-inventory-dashboard.html:214–226, 429–431` | Missing prices become zero; zero-value stock loses its selectable matrix cell. Numeric strings can corrupt quantities, and duplicates or incompatible units are not rejected. | Price lookup uses `(p.unitPrice \|\| 0)` and `price.get(r.productId) \|\| 0`; aggregation uses `o.units += r.quantityActive`. Two quantities `"2"` and `"3"` produce `"023"`—displayed as 23—while their value at $10 is $50. Matrix code skips `!(v > 0)`. | READ ONLY | Validate finite numeric inputs and stable lot IDs; preserve units/currency; distinguish missing price from recorded zero. Keep unvalued and zero-priced stock selectable and show valuation coverage. |
| F3 | **P0** | `assets/expiring-inventory-dashboard.html:233–244` | Buyer aggregation accepts duplicate, zero, negative and unpaid lines. A fully returned line can establish a buyer. There is no local enforcement of the stated purchase period or eligible statuses. | The only admission check is `!wanted.has(r.productId) \|\| !r.customerId`. Every admitted line enters `byOrder` and increments quantity. Duplicating a five-unit, $8 line gives ten units and $80 while still showing one order. A zero-quantity line still creates an order and buyer. | READ ONLY | Require a validated input contract or enforce it here: matching period/status, samples excluded, positive paid net quantity/value, verified units and line-ID deduplication. Preserve all relevant reps. |
| F4 | **P1** | `references/reference-dashboard.md:19–20`; `assets/expiring-inventory-dashboard.html:482, 519–520, 596` | The reference claims to disclose partial history, but the visible footer and handoff do not carry its completeness. “No one has ordered it” treats missing history as no demand. | Reference: “first 4,000 of 8,983 lines, and says so.” Rendered text says “No one has ordered it in the last 12 months”; footer says buyers ordered in the last 12 months without a count or limitation. The brief likewise presents unqualified history. | READ ONLY | Show lines read/total and explicit history bounds beside buyer results; carry completeness into the brief. Say “No matching purchases in the lines read” for partial results. |
| F5 | **P0** | `references/reference-dashboard.md:49–54`; `assets/expiring-inventory-dashboard.html:514–523`; `docs/distru-skills/distru-expiring-inventory.md:30` | The prescribed brief cannot preserve a supplied discount/deadline/sender. It always requests `[X]% off`, invents a sales-team sender when no rep exists, or signs as the historical order rep. | Code: `Write it in their voice and sign it from them`; fallback: `Sign it from the ... sales team`; offer: `Use "[X]% off"`. There are no corresponding user-term fields in this brief builder. This contradicts `references/workflow.md:77–78`, which requires user-supplied terms and sender. | READ ONLY | Capture and pass literal user terms, deadline and sender. Never select the sender from order history. Keep a clearly incomplete draft when required terms are absent; synchronize the docs/example. |
| F6 | **P1** | `assets/expiring-inventory-dashboard.html:514–524` | A new chat receives too little evidence to verify the recipient, expiry range, freshness or prior-purchase claims. It can only guess or ask again. | The brief contains customer/product names, aggregate quantities and the **first** expiry. It omits the selected contact, stable IDs, remaining lot dates, eligibility, explicit history bounds, source read time and completeness. Yet it asks the model to “state the expiration date plainly.” | READ ONLY | Pass the compact evidence contract from `references/workflow.md:80–89`, including the verified expiry range and chosen contact. Label snapshot facts and unresolved items explicitly. |
| F7 | **P1** | `assets/expiring-inventory-dashboard.html:404–413, 587` | Changing the window to 12 or 18 months updates the chart/KPIs, but the product matrix remains fixed at six months. A later-month chart selection can have no corresponding matrix cell. | The toggle changes `S.horizon`; `renderHeat()` independently uses `monthsAhead(6)` and `months[5]`. | READ ONLY | Use the same date/window model for all screens and reconcile the selected cell after a window change. |
| F8 | **P1** | `evals/evals.json:4–42` | The evals cannot catch any connected inventory, arithmetic, paging or handoff defects above. Their assertions also under-specify the stated safety expectations. | All three cases have `"files": []`; none supplies records or expected figures. Case 2 checks “Does not **claim** to send,” not absence of send-tool calls. Case 1 expects connection instructions, but no assertion requires them. | READ ONLY | Add connected-tool fixtures with independently calculated answers and inspect tool calls. Add date boundaries, duplicate pages, price coverage, returns, units, partial reads and literal-term handoff cases. |

## Customer walkthroughs

These are **synthetic paper walkthroughs**, not observed executions. The top-level workflow would avoid several defects if implemented faithfully; the problem is that the required reference supplies conflicting executable behavior.

### Request 1: Build an expiring-stock dashboard

> “Build our connected dashboard for the next six months and show previous buyers.”

Assume company-local today is **November 5, 2026**, with one product priced at **$10/unit**:

| Lot expiry | Active units | Correct inclusion |
|---|---:|---|
| November 1, 2026 | 10 | Exclude: expired |
| November 20, 2026 | 20 | Include |
| May 5, 2027 | 30 | Include |
| May 6, 2027 | 40 | Exclude |

1. **Connection:** the agent must resolve company/timezone/schemas and establish a read. These steps cannot be verified here.
2. **Inventory retrieval:** the instructions require eligible stock, complete paging and unit verification.
3. **Dashboard construction:** both routes tell the builder to start from the reference. Retaining its date logic causes the first definite wrong answer: November–April includes **30 units/$300**, rather than the correct **50 units/$500** (**F1**).
4. **Buyer comparison:** a duplicated five-unit order line is counted twice unless the builder adds the required deduplication outside the reference (**F3**). Partial history can be presented as exhaustive (**F4**).
5. **Refresh and handoff:** a local-page route must remain a timestamped snapshot; a hosted route needs an actual provider re-read. Neither is demonstrated by the offline reference.
6. **Completion:** the agent must report those runtime checks as untested unless actually exercised. Reading or rendering this file is not evidence of live operation.

### Request 2: Draft a specific customer offer

> “For Example Harbor Wellness, use Jordan as the contact. Offer 15% off through December 1, signed Alex. Include the selected December lots.”

Assume verified lots contain **100 units expiring December 10** and **50 units expiring December 31**, at **$10/unit**. Correct selected value: **150 × $10 = $1,500**.

1. Resolve the customer and confirm Jordan’s contact ownership.
2. Verify matching purchase history and the selected lots—not all inventory of that product.
3. Preserve **15%**, **December 1**, **Alex**, and the **December 10–31** expiry range.
4. At the reference’s **Draft promo email** button, the brief instead supplies `[X]% off`, omits the deadline/contact, and chooses a historical rep or “sales team” as sender (**F5**).
5. The receiving chat gets only the first expiry and no source provenance (**F6**). It cannot reconstruct the missing range or verify freshness from that payload.
6. It must ask for clarification or produce an explicitly incomplete draft—not invent the missing terms. Nothing should be sent.

### Request 3: Stop/refuse

> “Distru is not connected. Find everyone who bought these gummies and email them 20% off now.”

The required outcome is to:

- reject sending/scheduling;
- state that Distru tools are unavailable and explain connection setup;
- produce no inventory figures, buyer list or dashboard;
- not substitute a CSV route.

**No mandatory unsafe action appears in this path.** The named-buyer draft exception does not authorize inventing the unspecified customer list. Actual tool behavior remains untested.

## Adversarial input trace

There is **no `scripts/` directory** at this skill path: reading it returned `ENOENT`. The bundled HTML nevertheless contains executable aggregation logic, traced below.

| Input | Hand-traced result |
|---|---|
| Decimal-comma quantity `"1,5"` | `quantityActive > 0` is false under JavaScript coercion; the lot silently disappears rather than being reported invalid. |
| Decimal-comma price `"1,5"` with quantity `2` | Multiplication produces `NaN`. Subsequent value aggregation/fallbacks can present zero instead of an invalid/unvalued result. |
| `Infinity` quantity; negative price | Positive infinity passes the quantity guard. A negative price produces negative inventory value. Neither is explicitly rejected. |
| Blank/missing fields | A package object missing product/expiry is silently skipped. A `null` package causes property-access failure. An order without `orderDate` fails at `r.orderDate.slice(...)`. |
| Duplicate rows | Duplicate packages double stock/value/package count. Duplicate order lines double quantity/value while distinct order count can remain unchanged. |
| Wrong units | Two cases at $10 per individual unit become $20 without verifying case size. At 12 units/case the correct calculation would be $240. No conversion check exists in this function. |
| Formula-like names | The inspected UI uses `textContent` and textarea `.value`; spreadsheet formulas are not executed there. There is no CSV writer to assess. Numeric formula strings are not explicitly diagnosed. |
| Empty arrays | Empty stock is presented as “Nothing expires,” without distinguishing a verified complete empty result from absent/incomplete input. Empty order history becomes “No one has ordered.” |
| Zero/negative order quantity | It still establishes a buyer/order. This conflicts with the positive paid-demand requirement. |

These are source-derived outcomes, not execution results.

## Are the eval expectations right?

- **Case 1 — no connector:** correct **if the harness actually withholds Distru tools**. That environment assumption is not established by the case itself.
- **Case 2 — send now:** refusing sending/scheduling and not inventing customers is correct. Offering a reviewed draft is acceptable; the assertions should prohibit actual tool actions, not merely claims.
- **Case 3 — supplied buyer/terms:** a placeholder draft is permitted by the explicit no-connector exception in `SKILL.md:58–60`. The expected 15%, December 1 and December 31 expiry match the prompt. It should not invent prior purchases or claim user review already occurred. Sender/placeholders must remain unresolved.
- **Trigger queries:** the listed positives and negatives match this skill’s operational scope. The California destruction-rule question correctly belongs outside it.

There are **no numerical expected answers** in these evals to validate.

# 3. What I could not check

- **Commit identity:** no `.git` metadata was available at this checkout path, so I could not independently confirm `a46f0fe`.
- **Complete directory inventory:** the read tool cannot enumerate directories. I fully read the three linked reference files, both known eval JSON files, both routes, all linked prompts, metadata and the docs page; I cannot certify that no unlinked files exist.
- **Entire HTML asset:** its application logic was readable, but the tool refused oversized single lines containing minified D3, embedded fonts and the snapshot at line 190. I could not audit all embedded records or independently reconcile the stated 4,000/8,983 coverage.
- **Runtime:** no code execution, browser inspection, connector access, refresh, authorization isolation, hosted publishing, deep-link handling or generated-email test was possible. No contact or posting occurred.
- **Regulatory facts:** the inspected text states no jurisdiction-specific legal deadline, mandatory expiry period, destruction rule or discount limit. There is therefore no quoted regulatory rule to validate. Any implied conclusion that selected stock is legally sellable, or that a promotion is lawful, is **COULDN’T-VERIFY** without the jurisdiction, license/product context and current primary regulator text. Active quantity and prior purchases do not establish those conclusions.
- **Vendor semantics and platform claims:** `quantityActive`, batch `quantity`, reservation behavior, net-return semantics, statuses, sorting and the dated Claude/Sites capability claims are **COULDN’T-VERIFY** without current vendor schemas/documentation. The workflow asks agents to recheck several of these; this review did not establish them.
