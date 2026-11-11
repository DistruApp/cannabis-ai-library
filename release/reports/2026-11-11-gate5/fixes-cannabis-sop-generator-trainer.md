# Gate 5 fixes: cannabis-sop-generator-trainer

Review: `pi-cannabis-sop-generator-trainer.md`. This skill has no script, so every finding was checked by quoting the files. Paths are relative to `skills/cannabiz-skills/compliance/cannabis-sop-generator-trainer/`. Built on the files as left by today's triage pass.

## Findings

| ID | Reviewer severity | Verdict | My severity | Evidence | Fix | Regression check |
|---|---|---|---|---|---|---|
| F1 | P0 | CONFIRMED | P1 | `examples/sample-sop-with-training.md` quick reference (old lines 111-117) kept only "Never let a shipment leave without a manifest that matches what was picked." Section 7 says "Until it's confirmed, any weight mismatch holds the shipment" and "Warehouse Lead notifies the Compliance/Inventory Manager immediately". Step 2's "Do not substitute a different batch or SKU without a documented order change first" was also dropped. `SKILL.md` asked only for "Steps, expected results, and warnings". An accurate manifest of an underpick would pass the summary's only stop rule. Re-rated P1: the full SOP keeps the control, and the summary is a staff aid, not the controlling document. | `SKILL.md` Phase 2 now says to shorten wording but never controls, and to carry over every warning, hold or stop condition, escalation step and role restriction, including the ones in Controls and Variance. The example quick reference now has the no-substitution rule, a "Stop and hold the shipment if" block (unit count, weight, manifest mismatch) and an "On a hold" escalation line. The answer-key explanation for Q3 is now conditional on the threshold, as the reviewer noted. | `evals/evals.json` eval 2: new assertion "Quick-reference summary keeps the Section 7 hold and escalation … and the no-undocumented-substitution warning"; expected_output updated to match |
| F2 | P0 | CONFIRMED | P1 | Example Step 4 warning: "A mismatch here is a licensing violation, not just a paperwork error." Section 3 cites no rule. That breaks the skill's own guardrail that citations are flagged, not asserted. Re-rated P1: the example is labelled illustrative with placeholder citations, but agents copy its wording. | Now reads: "A mismatch may break the state's transfer rules, not just the paperwork (CONFIRM: the applicable transfer rule with your compliance lead)." The operational prohibition is unchanged. | Read back. This changes the Phase 1 text that `sop_phase1()` extracts for eval 2, so the suite needs rebuilding (see below) |
| F3 | P1 | CONFIRMED | P2 | `SKILL.md` used three different gates: "until the operator has reviewed it" (Phase 1), "Once the SOP is approved" (Phase 2) and "Runs Phase 2 directly against the supplied SOP" (trigger table). A reviewed but unapproved SOP could get a training packet. Re-rated P2: the Phase 2 gate was already the strict one, so this was ambiguity, not a missing gate. | One gate throughout: the operator confirms that this version is approved by the role named under Approvals. "Reviewed" or "looks fine" is not approval. The trigger table now confirms approval of a supplied SOP before Phase 2, and offers a review otherwise. The guardrail matches. | Read back. Existing eval 1 ("Stops after the SOP draft") and eval 2 ("approved" SOP) still hold |
| F4 | P1 | CONFIRMED | P2 | Skeleton: "12 months out by default". Phase 3 recommends 6 months for cash handling, but only after approval, while Phase 3 also says to "Confirm the next review date already set in the Phase 1 header". Re-rated P2: the review cadence is an internal default, not a rule, and the example already set 6 months in Phase 1. | Phase 1 header item now sets the next review date with the Phase 3 cycle (6 months high-risk, 12 otherwise, or the operator's own). The skeleton's Next Review Date hint names the high-risk areas and the 6-month default. | Read back |
| F5 | P1 | CONFIRMED | P2 | The sign-off log columns were "Employee … Signature", with no SOP ID or version, although retraining is required before each revision takes effect. Re-rated P2: it's a record-keeping gap with an easy fix, and it doesn't produce wrong output. | `SKILL.md` sign-off template now starts with the SOP ID and approved version. The example log has a "SOP ID / Version" column (WHS-002 / 1.0) and says one row per attempt. | `evals/evals.json` eval 2 assertion changed from "Sign-off log has columns for score, result and retest date" to "Sign-off log identifies the SOP ID and version and has columns for score, result and retest date" |

Reviewer side notes on the evals, also handled:
- Answer key Q3 said "Any mismatch holds", which is broader than Section 7. It's now conditional (fixed with F1).
- Eval 1 lists the license number among questions to ask, but the intake template makes it optional. Not changed: it's only an example in expected_output, and no assertion requires it.

## Known-answer changes (with reasons)

- **Eval 2, new assertion (quick reference keeps holds and escalation).** Without it, F1 passes every assertion.
- **Eval 2, sign-off log assertion now also requires the SOP ID and version.** The skill now requires them (F5).
- **Eval 2 expected_output** now describes both of the above.
- **Example answer key Q3 explanation.** The answer is still (c). Only the reasoning changed, so it matches Section 7's threshold logic.

## Other files changed

- `templates/cannabis-sop-skeleton.md` (in the skill folder): Next Review Date hint (F4).
- `docs/cannabiz-skills/compliance/cannabis-sop-generator-trainer.md`: the example output now describes a 6-step quick reference with the hold and escalation rules, and a sign-off log tied to the SOP ID and version. The old text said "7 step".

## Shared-file changes needed

None.

## Open items

- **Suite rebuild needed.** The eval 2 fixture comes from the example's Phase 1 (via `sop_phase1()`), and the F2 wording changed. Eval 2's assertions changed too.
- **Eval 2 fixture (P2, not fixed).** It is labelled "approved" but still has CONFIRM blanks for jurisdiction and retention. That's acceptable for an illustrative SOP. A stricter fixture would fill them with fictional confirmed values.
- **Regulatory statements in the example stay COULDN'T-VERIFY,** as the reviewer said (manifest contents, a manifest travelling with the vehicle). They are already framed as "confirm with compliance counsel".
- Checks: `python3 scripts/check_repo.py --no-cli` passed (7324 checks, 0 failed). There are no unit tests because the skill has no script.

## Round 2

Review: the independent Claude review of `a46f0fe` (SOP section, fresh-session trials sop1 and sop2). Each finding was re-checked against the current tree. Paths are relative to the skill folder.

| ID | Reviewer | Verdict | Mine | Evidence | Fix | Regression check |
|---|---|---|---|---|---|---|
| S1 | P2 | ALREADY FIXED (round 1, F2) | n/a | `examples/sample-sop-with-training.md:67` now reads "A mismatch may break the state's transfer rules, not just the paperwork (CONFIRM: the applicable transfer rule with your compliance lead)." | None | Read back |
| S2 | P1 | CONFIRMED | P1 | Trial sop1: the user described count, verify and log. The 18-step draft added untagged steps, including stopping sales, the POS close-out report, never leaving the drawer alone and sealing a deposit bag. `SKILL.md` had only "Never invent a step that wasn't described or confirmed", with no instruction for where a proposed control should go, so the agent wrote it in as a step. | `SKILL.md` Phase 1: the numbered procedure holds only steps the operator described or confirmed. Any control the agent thinks is missing goes in a separate "Suggested additions (not in the SOP until you confirm)" list after the draft, with a reason, and joins the procedure only after a yes. The rule is stricter than before, not weaker. `templates/cannabis-sop-skeleton.md` Step 6 hint says the same. | `evals/evals.json` eval 1: new assertion "The numbered procedure holds only the steps the user described … any other control … is listed separately as a suggested addition to confirm". `expected_output` extended to match |
| S3 | P2 | CONFIRMED | P2 | Trial sop2: "The Metrc entry should usually reflect the cannabis weight" was put to the user as a question, without a confirm flag. The guardrail listed only citations, thresholds, retention and cadence, so a general claim about what a rule or the track-and-trace system requires wasn't clearly covered. | `SKILL.md` first guardrail now also covers any statement of what a state rule or the track-and-trace system requires, including one made in passing or inside a question. | Read back |

Fresh-session trials: sop1 and sop2 both loaded the skill. The two missed loads were cogs2 and yield1. The description is unchanged.

### Known answers changed (round 2)

- Eval 1 has a new assertion and an extended `expected_output` (S2). Without them, a draft with invented steps passes every assertion. **The plugin-evals suite needs a rebuild.**

### Shared-file changes needed (round 2)

None.

### Checks (round 2)

`python3 scripts/check_repo.py --no-cli`: 7526 passed, 0 failed. `evals/evals.json` parses. There are no unit tests because the skill has no script.
