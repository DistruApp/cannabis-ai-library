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

Look up the state in `references/state-profiles.md`. Use its regulator, rules URL, and any cited rules. If the state is missing or a rule isn't cited, mark state-specific items **NEEDS VERIFICATION** and give the profile's rules URL to check. If the profile has no rules URL (generic-coverage states) or no entry for the state, name the regulator if the profile lists one and ask the operator for the current rules or the regulator's checklist; don't supply a URL from memory. Never fill a gap with another state's rule or a "common" requirement presented as law.

If the inspection is complaint-driven or follows a notice, say plainly that they should involve their compliance counsel. This skill still helps with preparation.

### 2. What they already have

Ask for (or accept a list of) existing SOPs, logs, licenses, training records, and the latest inventory reconciliation. If no recent reconciliation exists, recommend running `cannabis-traceability-reconciliation` first. Inventory discrepancies are among the first things inspectors look at, and they take the longest to fix.

### 3. Readiness checklist

Use `references/inspection-areas.md` for the areas and the typical items within each. For each item, record:
- **Status**: Ready / Gap / Unknown (Unknown is not Ready)
- **Basis**: [RULE + citation + verified date] only for a profile entry marked V or V\*, or regulation text the operator supplied, that applies to this license type. A cited entry with any other profile label (V (LII), NEEDS VERIFICATION, UNVERIFIED, Vendor-only) keeps that label and says to confirm the current text. Anything else: "operational best practice: confirm against your state's rules"
- **Evidence**: the document or physical thing that proves it

Include an area when the operation does that activity, not only when the license letter in `references/inspection-areas.md` matches. A distributor without cultivation doesn't need a plant-tagging section, but a distributor that holds returned, recalled or failed product for destruction does need the waste section. If you're not sure whether they do an activity, ask or keep the area as Unknown.

### 4. Binder index

Fill `assets/binder-index-template.md`: one tab per area, each with the documents to have on hand, where they live (paper/digital), and the custodian.

### 5. Gap list

Fill `assets/gap-tracker-template.csv`. Prioritize by:
1. **Critical**: possible untracked product, unexplained inventory variance, security/surveillance failure, product with failed or missing tests in saleable inventory, expired license or badge.
2. **High**: missing required records or logs, SOPs not matching actual practice, untrained staff on a regulated task.
3. **Medium**: organization and presentation issues.

Give each gap an owner role and a due date working back from the inspection date. If the date is close, say what can realistically be fixed in time and what should be disclosed honestly rather than patched over. **Never suggest backdating, altering, or fabricating records.** If the user asks for that, decline and explain the risk. Missing records stay on the gap list. Any reconstruction uses only genuine evidence (traceability records, video, notes made at the time) and is marked as a late entry with the date it was written and its source. Don't send anything to a regulator or inspector, and don't tell them the operator is ready; recommend compliance review before the operator says anything to the regulator about missing records.

For SOP gaps, list the SOP needed and its purpose. Drafting it belongs to `cannabis-sop-generator-trainer` if that skill is available. Say so instead of drafting full SOPs here.

### 6. Mock-inspection questions

Write 10–20 questions an inspector is likely to ask *this* operation, drawn from the areas in scope. For each: who should answer, the evidence to show, and an answer to avoid (guessing, contradicting the SOP, speculating about rules). Guidance for walkthrough conduct is in `references/inspection-areas.md` (last section).

### 7. Output

Lead with a readiness summary: areas in scope, counts of Ready / Gap / Unknown, the Critical gaps, and days until the inspection. Every count and finding must come from what the operator told you or shared in step 2. With no records shared, every item is Unknown: say so and ask for the records, and never report a Ready or Gap you have no evidence for. Work out the days from a calendar date the operator gave you; if they only gave a weekday ("Thursday"), ask for the date. With no inspection scheduled, say "not scheduled" and ask the operator to agree target dates for the gaps. Don't predict the result either way: never write "you'll pass" or "you will pass", not even to deny it ("nothing here means you'll pass"). If a caveat helps, say "This plan doesn't predict the inspection result." Then the jurisdiction block, checklist, binder index, gap list, and mock questions. Follow `references/output-conventions.md` and end with the sign-off block.

## Gotchas

- **Unknown ≠ Ready.** If the operator can't produce the evidence, the status is Gap or Unknown, however confident they sound.
- **SOPs vs. reality.** Inspectors compare written SOPs with what staff actually do. A good SOP that nobody follows is a finding. Mock questions should test the floor staff, not just managers.
- **Multiple licenses at one site.** Co-located licenses can have separate obligations and separate inventory. Check each one.
- **Traceability first.** A clean binder doesn't make up for a count that doesn't match the system. If reconciliation status is unknown, make it the first gap.
- **Don't cite rules from memory.** Even well-known requirements (camera retention periods, waste handling, visitor logs) differ by state and change over time. Cite them or mark them NEEDS VERIFICATION.
- **Local rules.** City or county permits and conditions may apply on top of state rules. Ask whether they hold a local permit.

## Example

User: "State inspector is coming Thursday for our renewal. We're a Colorado retail marijuana cultivation facility. What do we need ready?"

The user has shared no records and no date, so good output invents no counts, findings or countdown. It asks in one message for: the inspection date (a calendar date, so the countdown isn't guessed from "Thursday"), every license at the premises (for example a co-located MIP), any local permit, the traceability system, whether they have a regulator checklist, and what they have on hand (date of the last Metrc reconciliation, SOP list, waste log, surveillance retention, training and badge records). While waiting it may preview the cultivation areas from `references/inspection-areas.md`, labeled operational best practice, and says that if they can't point to a recent reconciliation, running `cannabis-traceability-reconciliation` comes first. Once they answer, the summary opens with areas in scope and Ready / Gap / Unknown counts built only from what they shared ("Readiness for a Colorado retail cultivation renewal inspection on [date], [N] days out…"), cites Colorado items from `references/state-profiles.md` with their labels, and marks the rest NEEDS VERIFICATION against the rules URL there. Then come the checklist, binder index, gap tracker and mock questions, and SOP drafting goes to the SOP skill.
