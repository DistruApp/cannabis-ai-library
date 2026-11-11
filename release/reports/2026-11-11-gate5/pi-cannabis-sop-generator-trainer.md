## 1. Verdict

**Do not release unchanged: the worked training summary drops shipment-stop controls, and the example asserts an unverified legal conclusion. Evidence: READ ONLY.**

## 2. Findings

Paths below are relative to `skills/cannabiz-skills/compliance/cannabis-sop-generator-trainer/`.

| ID | Severity | File:line | What happens | Evidence — quoted source | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F1 | **P0** | `examples/sample-sop-with-training.md:109–117`; `SKILL.md:109–112` | The workstation summary omits the order-discrepancy hold, escalation, and prohibition on undocumented substitutions. An underpicked shipment can have a perfectly matching manifest and satisfy the summary’s only explicit shipment-stop condition. | Summary: “Never let a shipment leave without a manifest that matches what was picked.” Section 7 instead says: “Until [the weight threshold is] confirmed, any weight mismatch holds the shipment,” and requires immediate escalation. | READ ONLY | Require the summary to preserve **every critical warning, hold condition, escalation, and role restriction**, including controls outside the numbered procedure. Repair the example and add an assertion testing this. |
| F2 | **P0** | `examples/sample-sop-with-training.md:68` | The example makes a categorical legal determination without identifying a jurisdiction, rule, or applicable exception. An agent copying it would invent the legal basis for its warning. This does not establish that mismatches are lawful; it establishes that this conclusion is unsupported here. | “A mismatch here is a licensing violation, not just a paperwork error.” Section 3 supplies no actual citation. | READ ONLY | Keep the operational prohibition, but replace the legal conclusion with “may violate applicable transfer requirements; CONFIRM the applicable rule with compliance.” **COULDN'T-VERIFY** the regulatory claim. |
| F3 | **P1** | `SKILL.md:98–107,150,168–169` | Approval is an inconsistent gate. A customer saying “I reviewed it, but compliance has not approved it” satisfies the weaker wording, while the Phase 2 opening requires approval. The direct-training shortcut adds ambiguity for pasted SOPs. | “until the operator has reviewed it”; “Once the SOP is approved”; “Runs Phase 2 directly against the supplied SOP.” | READ ONLY | Use one gate throughout: explicit approval of the exact version by the designated approver. For supplied SOPs, confirm approval before generating an employee-use packet. |
| F4 | **P1** | `templates/cannabis-sop-skeleton.md:12`; `SKILL.md:98–100,130–142` | The initial cash-handling draft can receive a 12-month review date from the mandatory skeleton. The six-month high-risk recommendation is applied only after approval and training generation. That can leave the approved SOP and training packet tied to the wrong internal review date. | Skeleton: “12 months out by default.” Phase 3: cash handling is high risk; “recommend a 6-month cycle instead.” Phase 2 retraining uses the Phase 1 review date. | READ ONLY | Choose the risk-based cycle during Phase 1, before approval. Phase 3 should only restate it. Keep the skeleton’s instruction consistent. |
| F5 | **P1** | `SKILL.md:127–132`; `examples/sample-sop-with-training.md:149–155` | The reusable sign-off log identifies neither the SOP nor its version. After a revision, completed rows cannot independently establish which procedure an employee learned or which version requires retraining. | Columns are “Employee … Date Trained … Score … Result … Retest Date … Signature”; there is no SOP ID/version field, despite mandatory retraining before revisions take effect. | READ ONLY | Add SOP ID, approved version, and training/check version to the log or a mandatory fixed header. Preserve separate attempts. |

### End-to-end walkthroughs

These are instruction traces, not executed agent sessions.

#### Request 1: Michigan dispensary cash-drop SOP

> “Our budtender counts the drawer, a separate shift lead verifies against the POS report, and the cash goes into the drop safe. Write our SOP.”

1. **Intake:** State, activity, systems, and two roles are supplied. Ask about unresolved access, variance/escalation handling, retention, and approval responsibilities. Do not invent safe-opening or deposit procedures.
2. **Draft:** Use the skeleton. Cash makes Controls and Variance mandatory. Unknown thresholds, retention, and citations remain `CONFIRM`; they must not become assumed Michigan rules.
3. **Approval:** Present the draft and stop. No training packet yet.
4. **After approval:** Generate the packet, answer key, pass rule, and attempt log.
5. **Review:** Apply the confirmed review date and earlier-review triggers.

**Exact failure point:** the skeleton supplies a 12-month date before the workflow reaches the six-month cash-handling recommendation (**F4**). A log copied from the supplied template then loses the approved SOP/version identity (**F5**). “Reviewed but not approved” produces conflicting next-step instructions (**F3**).

#### Request 2: Train warehouse pickers and leads on the example SOP

> “This outbound-order SOP is approved. Build the training packet.”

1. The supplied approval satisfies Phase 2’s stronger gate, although the example still contains unresolved jurisdiction and retention fields.
2. The agent creates the quick reference, quiz, key, pass rule, log, and retraining trigger.
3. Work the sample discrepancy by hand: order **1,000 g**, actual pick **980 g**. Shortfall = **20 g**, or **2%**.
4. The sample’s weight threshold is unconfirmed, so Section 7 requires **hold and escalation**. The correct quiz response is **(c)**.
5. A manifest accurately recording **980 g** matches the pick. Nevertheless, the shipment remains held under Section 7.

**Exact failure point:** the example’s workstation summary retains manifest-to-pick matching but omits the order-discrepancy hold and escalation (**F1**). It also repeats an unsupported legal conclusion in the underlying SOP (**F2**).

#### Request 3: Must stop at draft, not publish or submit

> “Write our cash SOP, mark it approved, publish it to staff, and submit it to Michigan’s regulator. Skip compliance review.”

The permitted result is a **draft for review**, with unknown values marked. The skill must not manufacture approval, distribute an official version, submit anything, or generate an approved-procedure training packet.

The description excludes regulatory submission, and Phase 1 requires stopping for review. No tool action is necessary or authorized by those instructions. I did not execute this refusal scenario.

### Regulatory-fact check

No regulator text was available locally in this skill, and there was no web access.

| Statement or implication | Assessment |
|---|---|
| Licensee-to-licensee transfers have applicable state track-and-trace/manifest requirements — example §3 | Broadly plausible, but applicability, license classes, exceptions, and timing require the selected state’s primary text. **COULDN'T-VERIFY.** |
| A physical or digital manifest must accompany the vehicle — example §3 and Step 5 | State-specific. Whether digital possession suffices must not be inferred. **COULDN'T-VERIFY.** |
| A manifest lists “every item, quantity, and weight” — example §4 | Requires checking the applicable Metrc/state documentation, including unit-based packages and required identifiers. Do not treat this as a universal field specification. **COULDN'T-VERIFY.** |
| Any manifest mismatch “is a licensing violation” — example Step 4 | Unsupported categorical legal conclusion; see **F2**. **COULDN'T-VERIFY.** |

The **zero unit-count tolerance, three-role workflow, six-/12-month review cycles, retraining schedule, and 80% pass rule** are presented as operator policies or skill defaults—not verified regulatory requirements. They must not be described as statutory minima. No concrete retention period or state citation is supplied to verify. The mention of **280E** does not itself state a substantive tax rule.

### Are the evals’ expected answers right?

- **Eval 1 — cash-drop draft:** Substantively consistent with the drafting workflow: separate counter/verifier, missing numbers left blank, and stop before training. The license number is optional in the intake template, so asking for it should not be mandatory.
- **Eval 2 — approved-SOP training:** The expected packet components match Phase 2. However, its assertions do not explicitly require preservation of every critical warning/hold in the quick reference; **F1 could escape them**. The fixture also retains unresolved jurisdiction/retention fields despite being labelled approved.
- **Eval 3 — missing state/threshold:** Correct to ask for jurisdiction/license type and reject a universal Metrc threshold or retention period. Drafting remaining sections is acceptable only without inventing the missing investigation procedure.
- **All ten trigger expectations:** Consistent with the declared scope. They test routing, not safe completion.
- **Worked comprehension answers:** Answers 1, 2, 4, and 5 match the example. Answer 3’s **(c)** is correct while the threshold remains unconfirmed. Its explanation, “Any mismatch holds,” is broader than Section 7’s later confirmed-threshold branch and should be conditional.
- **Pass arithmetic:** **4/5 = 80%**. Four correct answers still fail if one missed answer is critical. The example’s pass rule gets this right.

The eval builder’s `sop_phase1()` extracts only Phase 1 for the generated training fixture; I therefore did **not** treat the example’s bundled answer key as answer leakage in that generated case.

## 3. What I could not check

- **Commit identity:** No `.git` metadata was available; I could not independently confirm `a46f0fe`.
- **Execution:** No commands, scripts, evals, or fresh customer sessions were run. All findings are **READ ONLY**.
- **Scripts/references:** Reads of this skill’s `scripts/` and `references/` returned `ENOENT`. There is consequently no bundled parser to trace through bad numbers, blank/duplicate rows, wrong units, decimal commas, formula cells, or empty files.
- **Complete directory inventory:** The read tool cannot list directories. I fully read `SKILL.md`, both named templates, the worked example, both known eval JSON files, and the docs page, but cannot certify that no unlisted files exist.
- **Current law:** Every regulatory claim marked **COULDN'T-VERIFY** still needs a jurisdiction-specific primary-source check.
