# Cannabis SOP Generator & Trainer

Skill: [`cannabis-sop-generator-trainer`](../../../skills/cannabiz-skills/compliance/cannabis-sop-generator-trainer/SKILL.md)

## What it does

Turns a described cannabis business process into a draft Standard Operating Procedure for your compliance lead to review before it goes into a license application, inspection binder or audit file. Each SOP follows a fixed structure: header block with license info, purpose and scope, regulatory references, roles by title with segregation of duties, step by step procedure with expected results and warnings, a controls and variance section for anything touching cash, inventory or quality, records retention, training requirements and a review schedule. Once the SOP is approved, it generates the training packet: a one page quick reference, a 5 to 10 question comprehension check tied to the critical steps, with an answer key and a pass rule (every critical question right, 80% overall, or your own rule), and a sign-off log that records each attempt. Missing citations, thresholds and retention periods are flagged for confirmation, never invented.

## When to use it

- "Write an SOP for our outbound order fulfillment"
- "Turn these process notes into an SOP"
- "Generate training for this SOP"
- "Is this SOP missing anything?"
- "When should this SOP be reviewed again?"
- Preparing SOPs for a license application or inspection, or proving staff were trained

## How to use it

- **Inputs:** a description of the process and its goal, license type and state, the roles who perform and approve it, the systems involved (POS, Metrc, BioTrack, accounting), and whether it touches cash, inventory or product quality. An intake checklist and an SOP skeleton are included.
- **Tools / connectors:** none required.
- **Works in:** Claude or any LLM.
- **Limits:** not legal or compliance advice. Every citation, threshold and retention period is marked to confirm with a compliance lead or counsel.

## Example

**Input:** outbound wholesale order fulfillment and Metrc manifest verification at a fictional licensed distributor.

**Output:** a complete SOP with three separate roles for picking, verifying and finalizing the manifest, zero tolerance on unit count, and a 6 month review cycle because it is a high risk area. It is followed by a training packet with a 6 step quick reference that keeps the hold and escalation rules, a 5 question comprehension check with its answer key and pass rule, and a sign-off log, tied to the SOP ID and version, for each role.
