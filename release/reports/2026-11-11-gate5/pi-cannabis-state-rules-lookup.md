## 1. Verdict

**Not ready for dependable regulatory answers: missing source evidence, conflicting verification rules, and incomplete medical/adult-use separation can produce unsupported operational advice.**

## 2. Findings

Paths below are relative to `skills/cannabiz-skills/compliance/cannabis-state-rules-lookup/`, unless otherwise stated. All evidence is from reading files; no commands or code were executed.

| ID | Severity | File:line | What happens | Evidence | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F1 | P1 | `references/state-profiles.md:300–320`; `SKILL.md:36–48` | Most generic-state entries cannot support the required cited answer offline. An agent must either omit mandatory evidence or invent a source URL, effective date, or quotation. Washington is a customer-facing example of this gap. | WA’s entire evidence entry is `CCRS… V. Replacement not funded as of 2026-05-06.` It contains no URL or operative quotation. The template requires `SOURCE… [URL] — effective [date]` and `EXACT TEXT`. | READ ONLY | Store a source URL, source date, supporting excerpt, and verification date for each system claim. Permit “not available” fields and an explicit verification-only answer. |
| F2 | P1 | `references/state-profiles.md:143,172–173` | A medical Massachusetts operator can receive the adult-use waste-witness instruction. The profile distinguishes Chapters 500 and 501 but supplies the changed witness rule only for Chapter 500. It gives no explicit instruction to stop rather than extend it to medical operations. | `935 CMR 500 (adult use) and 501 (medical)`; later: `The 2026-09-11 text requires one agent. Earlier versions required "No fewer than two". Don't use old SOPs.` Only `500.105(12)` supports that instruction. | READ ONLY | Label every MA item by program. For medical waste, require current `501.105(12)` before recommending a witness-count change. Whether the claimed amendment is correct is **COULDN'T-VERIFY**. |
| F3 | P1 | `SKILL.md:28–32`; `references/jurisdiction-gate.md:26–29`; `references/research-method.md:22–24` | The instructions disagree on whether secondary-source deadlines may be stated. The same Colorado or Michigan request can produce a cited deadline, a refusal, or an “unverified” deadline depending on which instruction the agent follows. | Main workflow: `V (LII) can be cited as a secondary source`. Gate: `Never state a deadline… unless it's cited from a primary source or the operator's own documents.` Research method: give a blocked-site answer as `UNVERIFIED until they confirm it`. | READ ONLY | Define one precedence rule. Distinguish “historical secondary-source text says X” from “your current obligation is X,” and apply that policy consistently. |
| F4 | P1 | `SKILL.md:28–32`; `references/state-profiles.md:3,84,143–146,314` | The freshness check uses the profile’s review date rather than the underlying rule version. Recently reviewing an old copy can make stale material appear usable. The offline fallback also fails to specify whether an expired answer must stop short of operational instructions. | `If the profile's review date is more than 90 days old… verify it live`. CO text is amended only through `2024-12-04`; MA medical text has history through `2024-11-22`; NJ uses a `2022 source`. | READ ONLY | Track source-version currency separately from access date. Make known-stale, expired, and pending-change items verification-only when current text cannot be obtained. |
| F5 | P1 | `SKILL.md:51,60`; `evals/evals.json:36–42` | Federal legal status must be repeated as verified even though the bundle contains no exact document URL or independently inspectable source artifact. The eval rewards repeating that assertion rather than establishing it. | `give the federal status from the Gotchas`; Gotchas asserts Schedule III placement under `FR Doc 2026-08176`, effective `2026-04-28`, and labels it `V`. Eval 3 requires that document number and date. | READ ONLY | Supply exact Federal Register/govinfo URLs and retained operative text; date-gate the claim and allow abstention when it cannot be checked. The placement, scope, registration path, hearing and pending-status assertions are **COULDN'T-VERIFY**, not established false. |
| F6 | P1 | `references/research-method.md:5–11` | Live research can stop at an older FAQ or guidance page without checking the controlling code. That can turn an accurate quotation of outdated guidance into an incorrect current requirement. | `Source priority (stop at the first one that answers it)` puts regulator `guidance documents, FAQs, industry advisories` ahead of official administrative code. | READ ONLY | For legal requirements, confirm the controlling provision and its current effective version. Use FAQs and bulletins to explain implementation, not to end the currency check. |
| F7 | P1 | `references/state-profiles.md:15,96,116–117` | An unsuccessful search becomes a universal legal conclusion. An agent may assure an operator that no numerical threshold exists despite incomplete or outdated coverage. | `Where a state section says it defines no numeric… threshold, say so.` CO says `CO rules define no numeric… threshold (none found in 3-805, 3-905 or 3-920)`. MI makes the same categorical claim while acknowledging blocked statutes and bulletins. | READ ONLY | Say “No threshold was found in the sources reviewed; current requirements remain unverified.” Never convert incomplete research into proof that an obligation does not exist. |
| F8 | P1 | `evals/evals.json:7–16,22–28,36–42` | The evals accept temporally unconditional regulatory answers and omit the main failure branches. An answer can pass while relying on expired material or offering to file a notice. | All three evals have `"files": []`. NM expects the “current” system without an evaluation date. No assertions test stale/offline abstention, medical waste, conflicting sources, or the prohibition on sending/submitting. | READ ONLY | Add explicit as-of dates and source fixtures. Test blocked sources, missing quotations, program boundaries, and refusal to draft/file/send submissions. Require answers to preserve source uncertainty. |

### Customer walkthroughs

These are manual instruction traces, not model runs.

#### Request 1: Washington system lookup

> “We’re a Washington adult-use retailer. Our consultant says we need Metrc. Which reporting system do we use now? We don’t have browsing available.”

1. **Jurisdiction:** State, license, program and activity are supplied.
2. **Profile lookup:** The WA row says CCRS and labels it V.
3. **Research:** Unavailable; the workflow directs the agent back to the profile.
4. **Answer:** The agent can repeat the stored CCRS claim with a qualification, but cannot complete the required source URL, effective date and exact-text fields from this entry.

**Failure point:** Step 4, **F1**. A fabricated citation or quotation would be wrong; silently presenting the row as currently verified would also overstate the evidence. The correct offline result is a dated profile claim plus an explicit inability to verify current status—not a newly “checked” answer.

The additional claim that replacement funding was unavailable on May 6, 2026 is **COULDN'T-VERIFY**.

#### Request 2: Massachusetts medical waste SOP

> “We’re a Massachusetts medical-only MTC. Can we reduce our cannabis-waste destruction process from two agents to one?”

1. **Jurisdiction:** The gate correctly identifies medical-only operations.
2. **Profile lookup:** The rules introduction distinguishes Chapter 500 from Chapter 501.
3. **Relevant subsection:** Waste and destruction supplies only `500.105(12)` and emphatically says the new text requires one agent.
4. **Answer:** Applying that instruction to this MTC would extend an adult-use provision to a different program without evidence.

**Failure point:** Step 3, **F2**. The exact point requiring a stop is the absence of the applicable current Chapter 501 waste provision. The agent must not recommend changing the medical SOP based on the Chapter 500 summary.

Even for adult-use operations, the claimed one-agent amendment and whether “witness” means an additional person require a primary-source check: **COULDN'T-VERIFY**.

#### Request 3: Submission request that must stop

> “We’re a California distributor and discovered a significant discrepancy. Draft DCC-LIC-028 and email it to DCC and the police now.”

1. Identify the California notification provisions.
2. **Stop the requested drafting and sending.** The description excludes drafting regulatory submissions; `SKILL.md:50` expressly prohibits filing, sending or notifying anyone.
3. Give only the supported rule explanation and source limitations. The operator handles the submission and law-enforcement notification.
4. Do not offer to send it later after receiving access.

There is no instruction authorizing the requested action. An agent that drafts the submission or sends either notification violates the skill. **The eval suite does not test this boundary.**

### Are the evals’ expected answers right?

| Eval | Assessment |
|---|---|
| **1 — CA reconciliation** | Internally consistent with the profile’s 30-calendar-day review, audit, significant-discrepancy definition and separate notification explanation. The expected answer appropriately retains the percentage-base ambiguity. However, the official wording, current applicability and form are **COULDN'T-VERIFY**. The assertion bundles the form with both notification recipients; it should explicitly distinguish the DCC form submission from notification to local law enforcement. |
| **2 — NM system change** | Matches the bundled profile. NMS2S, the transition dates and current applicability are **COULDN'T-VERIFY**. “Right now” requires an evaluation date. Without that, unconditional identification of the current system is not a durable expected answer. |
| **3 — federal/280E** | Asking for jurisdiction/program and declining an operator-specific tax conclusion follow the skill. The mandatory federal document/date assertion is **COULDN'T-VERIFY**. The expected answer calls it “verified” without requiring accessible supporting evidence. |

## 3. What I could not check

### Regulatory facts requiring primary-source checks

**Every external regulatory claim remains COULDN'T-VERIFY in this review.** A V/V* label records the bundle’s assertion about prior verification; it is not independent evidence available to me.

| Material | Primary-source checks still required |
|---|---|
| **California** | All stated recording, reconciliation, correction and outage windows; significant-discrepancy definition and reporting recipients; DCC-LIC-028; manifest/rejection rules; testing and COA conditions; retention; cultivation waste requirements; badge scope; compilation version and pending rulemaking. |
| **Colorado** | Current version of 1 CCR 212-3; daily reconciliation; crime, health-event and fire reporting; outage/adjustment rules; transport/testing conditions; retention; waste rendering and video requirements; employee-badge scope. The absence of a discrepancy threshold is not established. |
| **Michigan** | Current R 420 text and applicable statutes/bulletins; tagging, loss/theft and other reporting; transfer/testing/hold rules; transporter custody limit; retention; destruction deadline and mixing requirements; employee registration and credential claims. |
| **Massachusetts** | Both Chapters 500 and 501 and their effective dates; inventory and incident duties; testing/transfer rules; continued validity of 2021 guidance; retention; waste-witness amendment and program scope; registration-card duties. |
| **New York** | Current Part 125; threshold tiers and measurement basis; reporting and outage rules; manifests, retention, waste and badges; Metrc implementation dates, retail identifiers/testing statuses and Bulletin 18. |
| **Illinois** | Agency/program scope; Metrc transition; claimed 2026 Subpart K amendment; dispensary and cultivation reconciliation/reporting; adjustment approval; manifests/testing; retention; destruction notices and credentials. |
| **Oklahoma** | Emergency-rule version and pending rulemaking; transaction/reconciliation duties; loss/theft, tag and monthly reporting; outage restrictions; manifests/testing; retention; waste deadlines/logs and employee credentials. |
| **Other-state table** | Every regulator/system pairing, medical-only qualifier, transition/procurement claim and Washington funding claim. Most rows lack source evidence sufficient for independent checking. |
| **Federal** | Both FR documents, publication/effective dates, quoted scope, CFR amendments, DEA-registration provisions, hearing status, claimed absence of a later final rule and quoted tax disclaimer. |
| **Technical references** | Metrc API endpoint availability, documentation hostnames, bulletin archive and reason-list behavior. |

### Access and execution limits

- Read in full: `SKILL.md`, the three referenced files under `references/`, `evals/evals.json`, and `docs/cannabiz-skills/compliance/cannabis-state-rules-lookup.md`.
- Reading the skill’s `scripts` path returned **`ENOENT`**. No bundled script was available to trace; bad numbers, blank/duplicate rows, wrong units, decimal commas, formula cells and empty-file parsing are therefore **not applicable to an inspected script**, not tested behavior.
- The read tool cannot enumerate directories. I could not prove there are no additional unreferenced files under `references/` or `evals/`.
- No web access, execution, eval runs, repository checks or live operator-system checks were performed.
- `.git/HEAD` was unavailable, so I could not independently establish that these files exactly match commit `a46f0fe`.
- No files were changed, and nobody was contacted.
