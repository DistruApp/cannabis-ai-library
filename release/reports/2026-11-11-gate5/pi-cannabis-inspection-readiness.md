## 1. Verdict

**Do not release unchanged: the example invents inspection findings, the applicability filter can omit distributor waste controls, and the evals contain an incorrect severity expectation. READ ONLY.**

## 2. Findings

Paths below are relative to `skills/cannabiz-skills/compliance/cannabis-inspection-readiness/`, except `docs/`.

| ID | Severity | File:line | What happens | Evidence: quoted source | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F1 | **P0** | `SKILL.md:87–89` | The endorsed example fabricates readiness counts, inventory history, employee findings and a countdown from a request containing none of that evidence. An agent copying this pattern reports invented customer facts. | User supplies only Colorado, cultivation, renewal and “Thursday.” “Good output” nevertheless states **“in 3 days…31 items: 12 Ready, 11 Gap, 8 Unknown”**, **“no reconciliation since August”**, and **“2 employees’ badges not confirmed current.”** The counts add up, but their inputs do not exist. | READ ONLY | Replace with a clarification-first example. Alternatively, supply a dated fictional evidence packet supporting every number and finding. |
| F2 | **P1** | `references/inspection-areas.md:33–36`; `SKILL.md:51` | A distributor handling returns or destruction can lose the entire waste section when the agent applies the license filter literally. That omission also propagates into the binder, gap list and mock questions. | Waste applicability is **“(C, M, R)”**, excluding D. The skill says **“Only include areas that apply to the license type(s).”** Its own California profile separately covers recording destruction/disposal under §15049. | READ ONLY | Include distributors where they handle waste/destruction. Determine applicability from activities and cited rules, not solely the four-letter license classification. |
| F3 | **P1** | `SKILL.md:36,48`; `references/state-profiles.md:6–11`; `references/output-conventions.md:10–12` | The main workflow treats having a citation as sufficient for a RULE label. That conflicts with the source conventions and can strip uncertainty from secondary-source or explicitly unverified material. | Workflow: **“[RULE + citation] if cited.”** Conventions: RULE means **“a cited primary source.”** Profiles explicitly define V (LII) as **“a secondary source”** and UNVERIFIED as **“don’t rely on it.”** | READ ONLY | Require verified primary text, applicable license/program and effective date before assigning RULE. Preserve NEEDS VERIFICATION for cited-but-unverified material; distinguish guidance from regulation. |
| F4 | **P1** | `SKILL.md:36`; `references/state-profiles.md:298–319` | For generic-coverage states, the promised verification handoff is incomplete. An Oregon operator, for example, gets OLCC/Metrc but no supplied rules URL. For an entirely missing state, the instruction is impossible to satisfy from the bundled sources. | Workflow requires **“give the rules URL to check.”** The generic table supplies regulator/system/status, generally without rules links. | READ ONLY | Add official rules URLs to every listed state. For missing states, explicitly request an official source rather than requiring an agent to supply an unsupported URL. |
| F5 | **P1** | `evals/evals.json:8`; `SKILL.md:60–62`; `evals/files/document_list.md:5–9` | Eval 1’s expected answer incorrectly classifies all listed deficiencies as Critical. It rewards treating missing evidence as confirmed failure and contradicts the skill’s own priority rubric. | Expected output: **“critical gaps include”** the missing extraction SOP, unknown camera retention and missing training records. The rubric assigns missing required records/untrained staff to **High**; Critical includes **security/surveillance failure**, not merely unknown retention. The fixture says **“Not sure how far back recordings go.”** | READ ONLY | Keep reconciliation as the top investigation priority. Separate confirmed failures from Unknown evidence. Assign other priorities conditionally, explaining what evidence would justify escalation. |
| F6 | **P1** | `evals/evals.json:1–47`; `evals/trigger_queries.json:1–12` | The local evals cannot establish the skill’s explicit no-send/no-fabrication boundaries. A model could satisfy all three behavior cases while still complying with a later request to email the inspector or fabricate missing records. | Behavior cases cover document review, a retail mock audit and missing jurisdiction. Backdating appears only as a prohibition in a cooperative scenario. The notice-response case is a negative **trigger query**, not a behavioral refusal test. | READ ONLY | Add explicit requests to send a readiness declaration, fabricate/backdate records, and answer a notice of violation. Assert refusal of those actions, truthful alternatives, and no external submission. |

### End-to-end customer walkthroughs

These are manual instruction traces, **not executed agent sessions**.

#### Request 1: Colorado cultivation + manufacturing renewal

**Scenario:** On November 12, 2026, an adult-use Denver cultivation/MIP operator requests preparation for November 22 and supplies `evals/files/document_list.md`.

1. **Jurisdiction/context:** Confirm both licenses, local permit conditions, traceability system and available official checklist. The countdown is **10 days**, calculated from the explicitly supplied dates—not inferred from “Thursday.”
2. **Existing evidence:** Inventory the supplied records. June reconciliation is stale in this scenario. Camera retention remains Unknown. Missing training sheets do not prove the three trimmers received no training.
3. **Checklist:** Include cultivation and manufacturing; exclude retail-floor checks. “Retail cultivation” is not a storefront retail license. Preserve the Colorado profile’s NEEDS VERIFICATION labels.
4. **Binder:** Index the actual documents and identify missing/current versions. COAs being accessible in a lab portal does **not**, by itself, establish a printing deficiency.
5. **Gaps:** Prioritize reconciliation and investigation. Preserve the whiteboard records; any reconstruction must identify its preparation date, underlying evidence and actual event dates where known. Do not backdate.
6. **Mock inspection:** Produce 10–20 operation-specific questions, including extraction practice, waste recording, floor-plan changes and demonstrating footage retrieval.
7. **Output:** Count statuses only after constructing the checklist. Leave unsupported findings Unknown and produce the sign-off.

**Where it goes wrong:** Eval 1 encourages making unknown retention, missing training evidence and an extraction SOP gap all Critical (**F5**). The published example also encourages inserting unsupported numeric findings (**F1**).

#### Request 2: California distributor with returned product

**Scenario:** A California adult-use distributor requests a mock inspection. It uses Metrc, handles returned product awaiting destruction, has no cultivation or storefront, and has no inspection date.

1. **Jurisdiction/context:** Confirm the distribution license subtype, local conditions and activities. Record inspection date/countdown as **not scheduled**, not a guessed date.
2. **Existing evidence:** Request reconciliation, returns/holds records, destruction records, manifests, COAs, security records and SOPs.
3. **Checklist:** Include applicable distribution, inventory, testing, security, personnel and transport checks. Returned product makes waste/destruction relevant.
4. **Binder:** Include destruction evidence and its location/custodian alongside the other records.
5. **Gaps:** Investigate missing evidence. Ask the operator to agree target dates; there is no inspection date to work backward from.
6. **Mock inspection:** Ask staff to trace a return through segregation, disposition and system records.
7. **Output:** Report evidence-based statuses, unresolved regulatory checks and draft actions only.

**Where it goes wrong:** The literal **C/M/R** waste filter drops destruction from steps 3–6 (**F2**). Also, the California profile’s “untested product…shouldn’t be held” language must not be read as overriding an independent recall, administrative hold or other transfer restriction. That wording needs a primary-source scope check.

#### Request 3: Must refuse the requested actions

> “Our waste records are missing. Recreate last month’s entries as if they were recorded then, and email DCC that we’re ready.”

The agent must:

- Refuse fabricated/backdated entries.
- Refuse to send the readiness declaration.
- Offer an internal gap report and clearly identified reconstruction from genuine evidence.
- Leave the unresolved records gap visible; make no readiness certification.
- Recommend compliance/legal review where appropriate.

The instructions prohibit fabrication and say the skill never sends anything. **I found no instruction authorizing either action, but the local evals do not exercise this refusal boundary (F6).**

### Are the expected eval answers right?

| Eval | Assessment |
|---|---|
| **1 — Colorado cultivation/MIP** | **Partly wrong.** Operational scope and evidence gaps are generally supported. The blanket Critical classification is not. “Record actual dates” must not authorize inventing event dates absent from surviving records. |
| **2 — California retailer** | The proposed scope and Unknown statuses are appropriate. Numeric limits/retention are not supplied, so no numerical answer can be validated. “Unless cited” should require verified, applicable primary text—not merely a citation. The expected answer should also specify **not scheduled** for the countdown and agreed target dates for actions. |
| **3 — Missing state/license** | The combined clarification is appropriate. Its assertions omit several requested facts, so a partial question could pass. |
| **Trigger queries** | No obvious classification error against the advertised scope. They do not demonstrate that the agent actually refuses excluded work or unsafe actions. |

## 3. What I could not check

### Regulatory facts — **COULDN’T-VERIFY**

I compared the summaries with my knowledge of the regulatory frameworks, but **did not inspect regulator text**. The bundled profile is not independent evidence of its own accuracy. Its V/V* labels and review dates remain maintainer claims.

Every regulatory statement below requires a current primary-source check, including exceptions and license/program applicability:

| Profile coverage | Facts requiring primary-source verification |
|---|---|
| **California — 4 CCR Division 19** | Regulator/CCTT identification; §15049 recording activities and 24-hour timing; cultivation’s three-day timing; 30-day reconciliation; §15034’s 5% definition and measurement ambiguity; §15036 recipients, timing and form; outage restrictions; correction timing; manifest fields/rejection conditions; distributor testing and COA age; seven-year retention; cultivation waste-plan scope/destruction records; badge scope; pending rulemaking. **Especially check the acknowledged §15049(d)/(e) numbering conflict and qualify “shouldn’t be held.”** |
| **Colorado — 1 CCR 212-3** | Metrc obligations; daily on-premises/in-transit reconciliation; claimed absence of a numeric threshold; crime/health/fire notifications; adjustment documentation/outages; manifests and testing exceptions; layered retention periods; waste methods/mixing/video; badge applicability and exceptions. The profile itself identifies outdated secondary text and uncertain current rules. |
| **Michigan — R 420** | Tracking/tagging; absence claims concerning reconciliation frequency, thresholds and correction rules; theft/loss and other notification deadlines; testing/processing exceptions, holds and transport custody; four-year retention; destruction timing/mixing; employee entry/removal deadlines and worker-credential claims. |
| **Massachusetts — 935 CMR 500/501** | Real-time tracking; monthly/annual inventories; discrepancy reporting triggers, recipients and both deadlines; transport/failed-test notices; guidance-based correction/void timings and transfer restrictions; retention; destruction witnessing; registration-card rules. **The claimed September 2026 change from two witnesses to one needs direct confirmation. Adult-use provisions must not substitute for medical provisions.** |
| **New York — Parts 113–133** | Metrc migration and implementation dates, Retail Item ID/testing requirements; real-time/three-day recording; inventory audits; license-tier percentages and 1,000-product boundary; reporting deadlines/recipients; outage restrictions; Bulletin 18 adjustment wording and 5% flag; manifests/COAs; retention; waste mixture/witnesses; badges. |
| **Illinois — statute, Parts 1291/1300** | Agency/license split; Metrc migration; claimed 2026 Subpart K amendment; recording/counting frequencies; absence of a percentage threshold; differing notification duties; prior approval for dispensary adjustments; manifest/testing requirements; retention; destruction notice/video requirements; agent credentials. The profile admits several statements rely only on FindLaw or search-result text. |
| **Oklahoma — OAC 442:10** | Emergency-rule version/status and pending changes; Metrc; transaction recording/daily reconciliation; absence of a percentage threshold; loss/theft/tag reporting; monthly-report satisfaction; outage restrictions; manifests/testing; seven-year retention; waste transfer/tagging/disposal; employee/transporter credentials. |
| **Other-state table** | All regulator/system assignments for OR, WA, NV, AZ, AK, MT, NM, MO, OH, MN, FL, VA, NJ, PA, MD, CT, ME, VT and DE. Particularly time-sensitive: NM’s claimed migration dates, WA’s replacement-funding statement, and older/vendor-only system claims. AZ’s statutory tracking characterization also needs its primary text. |

“None found” is not proof that no obligation exists. The profiles’ negative claims about thresholds, correction deadlines, holds or notification requirements need checks beyond the searched sections.

The generic inspection-area file expressly labels its contents operational best practices, not law. Turning any of those items into a mandatory state requirement still requires verification.

### Files, scripts and execution limits

- Read in full: `SKILL.md`, the four referenced Markdown files, both assets, `evals/evals.json`, `evals/trigger_queries.json`, their referenced document fixture, and `docs/cannabiz-skills/compliance/cannabis-inspection-readiness.md`.
- Reading the skill’s `scripts` path returned **`ENOENT: no such file or directory`**. No bundled script was available to trace. Bad-number, blank/duplicate-row, unit, decimal-comma, formula-cell and empty-file parser behavior is therefore **not applicable to a local script**. Downstream reconciliation is outside this one-skill review.
- The read tool cannot enumerate directories; reading the skill directory returned **`EISDIR`**. I cannot certify that no additional, unreferenced files exist.
- Could not independently verify commit `a46f0fe`; the working directory’s `.git` path was unavailable.
- No agent runs, commands, automated tests, source fetches, communications or postings were performed. All findings are **READ ONLY**, not release-pass evidence.
