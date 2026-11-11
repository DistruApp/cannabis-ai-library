---
name: cannabis-inspection-readiness
description: Prepare a licensed cannabis business for a state regulatory inspection, compliance audit, or license renewal review. Produce a readiness checklist by operational area, an inspection binder index, a gap list with owners and due dates, and mock-inspection questions, all tied to the operator's state and license type. Use when a cultivator, manufacturer, distributor, or dispensary says an inspector is coming, an inspection or audit is scheduled, wants a mock audit or self-audit, or asks what the state will check, or asks you to tell an inspector they're ready (it prepares the material; it never sends anything), even if they just say "we have an audit next week." Not for drafting SOPs from scratch (use cannabis-sop-generator-trainer if available), financial or tax audits, or answering a specific notice of violation.
license: MIT
metadata:
  version: "1.0"
  category: compliance-traceability
  risk-level: high
  last-compliance-review: "2026-10-16"
---

# Inspection readiness

Turns "the inspector is coming" into a plan with owners: what to check, what documents to have in the binder, what's missing, and how staff should answer. Generic operational areas are the scaffold. Every state-specific requirement comes **only** from `references/state-profiles.md` or regulations the operator provides. The skill prepares the operator. It never says the operator will pass.

## Workflow

```
- [ ] 1. Jurisdiction gate + inspection context
- [ ] 2. Inventory what the operator already has
- [ ] 3. Build the readiness checklist by area
- [ ] 4. Build the binder index
- [ ] 5. Build the gap list (owner, due date, priority)
- [ ] 6. Write mock-inspection questions
- [ ] 7. Assemble the output from the templates
```

### 1. Jurisdiction gate and context

Read `references/jurisdiction-gate.md`, then ask in **one** message for anything missing:
- State (and local jurisdiction if relevant), every license type at this premises, medical/adult-use
- Inspection type if known (routine, renewal, complaint-driven, pre-licensing, traceability audit) and date. If they just say "audit", ask whether it's a state regulatory or compliance inspection or a financial or tax audit; this skill covers only the first
- Traceability system
- Whether they have the current state regulations or a regulator inspection checklist to share. A regulator-published checklist is the best source and overrides the generic areas.

Look up the state in `references/state-profiles.md`. Use its regulator, rules URL, and any cited rules. If the state is missing or a rule isn't cited, mark state-specific items **NEEDS VERIFICATION** and give the rules URL to check. Never fill a gap with another state's rule or a "common" requirement presented as law.

If the inspection is complaint-driven or follows a notice, say plainly that they should involve their compliance counsel. This skill still helps with preparation.

### 2. What they already have

Ask for (or accept a list of) existing SOPs, logs, licenses, training records, and the latest inventory reconciliation. If no recent reconciliation exists, recommend running `cannabis-traceability-reconciliation` first. Inventory discrepancies are among the first things inspectors look at, and they take the longest to fix.

### 3. Readiness checklist

Use `references/inspection-areas.md` for the areas and the typical items within each. For each item, record:
- **Status**: Ready / Gap / Unknown (Unknown is not Ready)
- **Basis**: [RULE + citation] if cited, otherwise "operational best practice: confirm against your state's rules"
- **Evidence**: the document or physical thing that proves it

Only include areas that apply to the license type(s). A distributor without cultivation doesn't need a plant-tagging section, for example.

### 4. Binder index

Fill `assets/binder-index-template.md`: one tab per area, each with the documents to have on hand, where they live (paper/digital), and the custodian.

### 5. Gap list

Fill `assets/gap-tracker-template.csv`. Prioritize by:
1. **Critical**: possible untracked product, unexplained inventory variance, security/surveillance failure, product with failed or missing tests in saleable inventory, expired license or badge.
2. **High**: missing required records or logs, SOPs not matching actual practice, untrained staff on a regulated task.
3. **Medium**: organization and presentation issues.

Give each gap an owner role and a due date working back from the inspection date. If the date is close, say what can realistically be fixed in time and what should be disclosed honestly rather than patched over. **Never suggest backdating, altering, or fabricating records.** If the user asks for that, decline and explain the risk.

For SOP gaps, list the SOP needed and its purpose. Drafting it belongs to `cannabis-sop-generator-trainer` if that skill is available. Say so instead of drafting full SOPs here.

### 6. Mock-inspection questions

Write 10–20 questions an inspector is likely to ask *this* operation, drawn from the areas in scope. For each: who should answer, the evidence to show, and an answer to avoid (guessing, contradicting the SOP, speculating about rules). Guidance for walkthrough conduct is in `references/inspection-areas.md` (last section).

### 7. Output

Lead with a readiness summary: areas in scope, counts of Ready / Gap / Unknown, the Critical gaps, and days until the inspection. Don't predict the result either way: never write "you'll pass" or "you will pass", not even to deny it ("nothing here means you'll pass"). If a caveat helps, say "This plan doesn't predict the inspection result." Then the jurisdiction block, checklist, binder index, gap list, and mock questions. Follow `references/output-conventions.md` and end with the sign-off block.

## Gotchas

- **Unknown ≠ Ready.** If the operator can't produce the evidence, the status is Gap or Unknown, however confident they sound.
- **SOPs vs. reality.** Inspectors compare written SOPs with what staff actually do. A good SOP that nobody follows is a finding. Mock questions should test the floor staff, not just managers.
- **Multiple licenses at one site.** Co-located licenses can have separate obligations and separate inventory. Check each one.
- **Traceability first.** A clean binder doesn't make up for a count that doesn't match the system. If reconciliation status is unknown, make it the first gap.
- **Don't cite rules from memory.** Even well-known requirements (camera retention periods, waste handling, visitor logs) differ by state and change over time. Cite them or mark them NEEDS VERIFICATION.
- **Local rules.** City or county permits and conditions may apply on top of state rules. Ask whether they hold a local permit.

## Example

User: "State inspector is coming Thursday for our renewal. We're a Colorado retail marijuana cultivation facility. What do we need ready?"

Good output opens with: "Readiness for a Colorado retail cultivation renewal inspection in 3 days. 9 areas in scope, 31 items: 12 Ready, 11 Gap, 8 Unknown. Critical: no reconciliation since August (run one today), and 2 employees' badges not confirmed current. State-specific items cite [state-profiles entry] where verified. Others say NEEDS VERIFICATION against the rules at [rules URL]…" It then gives the checklist, binder index, gap tracker, and mock questions, and refers SOP drafting to the SOP skill.
