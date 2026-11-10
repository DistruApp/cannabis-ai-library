# Cannabis Inspection Readiness

Skill: [`cannabis-inspection-readiness`](../../../skills/cannabiz-skills/compliance/cannabis-inspection-readiness/SKILL.md)

## What it does

Turns "the inspector is coming" into a plan. It covers the operational areas inspectors commonly review (traceability records, inventory, security, waste, packaging and labeling, testing, employee records, transport and SOPs), marks each item Ready, Gap or Unknown, builds the inspection binder index, and prioritizes gaps by risk with an owner and due date. It writes 10 to 20 mock inspection questions for floor staff and managers. It never says the operator will pass and never helps backdate or alter records.

## When to use it

- "We have an inspection next week"
- "Can you run a mock audit for our dispensary?"
- "What will the state check at our renewal?"
- Preparing for a traceability audit or a license renewal review

## How to use it

- **Inputs:** state, every license type at the site, inspection type and date, and optionally a list of current SOPs and documents, the latest inventory reconciliation, or a checklist published by the regulator.
- **Tools / connectors:** none required.
- **Works in:** Claude or any LLM.
- **Related skills:** sends SOP drafting to [cannabis-sop-generator-trainer](./cannabis-sop-generator-trainer.md), and recommends running [cannabis-traceability-reconciliation](./cannabis-traceability-reconciliation.md) first if there is no recent count.

## Example

**Input:** "State inspector is coming Thursday for our renewal. We're a Colorado retail cultivation facility."

**Output:** a readiness summary showing areas in scope, counts of Ready, Gap and Unknown items, and the critical gaps (for example, no recent reconciliation). It follows with the checklist, binder index, gap tracker and mock questions, and marks every requirement it could not cite as needing verification.
