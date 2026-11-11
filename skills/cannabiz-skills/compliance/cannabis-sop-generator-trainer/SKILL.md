---
name: cannabis-sop-generator-trainer
description: >-
  Drafts a cannabis Standard Operating Procedure from a described process
  (header block, regulatory references to confirm, roles by title,
  step-by-step procedure, controls and variance handling for cash, inventory
  or quality, records retention, review schedule) for the operator's
  compliance lead to review, then builds a matching training packet: a
  quick-reference summary, a comprehension check with an answer key and pass
  rule, and a sign-off log. Use for "write an SOP for...", "turn these notes
  into an SOP", "make training for this SOP", "is this SOP missing
  anything?" or "when should we review this SOP?". Not for legal review, state-rule lookups or submitting anything
  to a regulator.
license: MIT
metadata:
  version: "1.1"
  category: compliance
  author: Distru
  supporting-files:
    - templates/sop-intake-checklist.md
    - templates/cannabis-sop-skeleton.md
    - examples/sample-sop-with-training.md
---

# Cannabis SOP Generator & Trainer

Turn a described business process into a draft Standard Operating Procedure
for the operator's compliance lead to review, then, once that SOP is
approved, build the training materials that show staff actually learned it.
Regulators, inspectors and auditors all read SOPs and training records, so
the draft is structured for them, but it is a draft: the operator's
compliance lead or counsel confirms every citation, threshold and retention
period before it's used.

If the user has `templates/sop-intake-checklist.md` filled out, read it
instead of asking each Phase 0 question individually. Use
`templates/cannabis-sop-skeleton.md` as the section structure for every SOP
you draft. See `examples/sample-sop-with-training.md` for a full worked
example of the SOP-plus-training-packet output.

============================================================
PHASE 0: INTAKE
============================================================

From the user's description, extract what's already available:
- The process to document, and what it's supposed to accomplish
- License type and state/jurisdiction (retail, cultivation, manufacturing,
  distribution, or multiple)
- Who performs this process (role, experience level, not a named person)
- Tools or systems involved (POS, METRC, BioTrack, accounting system, etc.)
- Whether the process touches cash, inventory, or product quality (this
  determines whether a Controls and Variance section is required)
- Any known compliance requirements, safety concerns, or past incidents tied
  to this process

Ask clarifying questions only for what's genuinely missing, using a
structured question tool if your app has one. Cap it at 5 questions, batched 2-3 at a time,
and stop as soon as you have enough to draft. Do not invent license numbers,
jurisdictions, or regulatory citations; ask for them.

============================================================
PHASE 1: DRAFT THE SOP
============================================================

Write at the reading level of the person who performs the task, not the
person who wrote the template. Default to plain, simple language (aim for a
5th-to-8th-grade level) unless the user tells you the audience needs
something more technical. One action per step. Every step starts with an
action verb. Include the expected result after critical steps. Add a warning
before any destructive, irreversible, or safety-critical action. Never invent
a step that wasn't described or confirmed: the numbered procedure holds only
steps the operator described or confirmed, split into one action each. A
control you think is missing (stopping sales first, running a report, never
leaving cash alone, sealing a bag, blind counts) is not a step. Put it in a
separate **Suggested additions (not in the SOP until you confirm)** list after
the draft, one line each with the reason, and add it to the procedure only
once the operator says yes.

Follow the structure in `templates/cannabis-sop-skeleton.md`:

1. Header block (title, ID, license type/number, dates, owner by role,
   version, revision history). Set the next review date now with the Phase 3
   cycle (6 months for a high-risk area, 12 otherwise, or the operator's own
   cycle), so the approved SOP and its training packet carry the same date.
2. Purpose and scope, including what's explicitly out of scope
3. Regulatory references (state statute/rule/license condition, track-and-
   trace system if relevant). Flag missing citations rather than inventing
   them.
4. Definitions (only what's needed)
5. Roles and responsibilities, by title, with segregation of duties made
   explicit for anything touching cash, inventory, or METRC adjustments
6. Step-by-step procedure with expected results/checkpoints
7. Controls, thresholds, and variance handling, required for any process
   touching cash, inventory, or product quality. Use the threshold the
   operator gives you. If they don't have one, leave it as a blank marked
   "CONFIRM: [state rule or equipment tolerance]". Never suggest a number.
8. Records and retention (what, where, how long, who has access). Ask for
   the retention period. If the operator doesn't know it, leave it as a blank
   marked "CONFIRM: retention period for this record type in [state]". Don't
   suggest a range.
9. Training requirements (roles, method, retraining cadence, record
   location). Sets up Phase 2.
10. Review and revision (next date, plus trigger events for an off-cycle
    review)

Present the full draft and stop. Do not proceed to Phase 2 until the operator
confirms this version is approved by the role named under Approvals (for
example the compliance lead). "I've reviewed it" or "looks fine" is not
approval; ask who approved it. The training materials in Phase 2 are built to
match whatever the approved SOP actually says.

============================================================
PHASE 2: GENERATE THE TRAINING PACKET
============================================================

Once the operator confirms this version of the SOP is approved (or approved
with edits, and the edits are applied), build:

- **Quick-reference summary**: a one-page, plain-language version of the
  step-by-step procedure for posting near the workstation or pulling up
  mid-shift. Steps, expected results, and warnings only, no header block or
  regulatory citations. Shorten wording, never controls: carry over every
  warning, hold or stop condition, escalation step and role restriction in
  the SOP, including the ones in the Controls and Variance section, not
  just the numbered steps. Keep who does what: for each hold, keep the role
  the SOP names to escalate to, resolve or release it. If the SOP names none,
  keep its wording and list the gap for the compliance lead; don't assign one.
- **Comprehension check**: 5 to 10 questions tied directly to the SOP's
  critical steps, warnings, and quality checks, not generic questions about
  the topic. Mix formats based on what the step requires someone to know or
  do. Mark each question that tests a critical step or warning as
  **critical**. For a hands-on task (cultivation, extraction, equipment
  operation), recommend a practical demonstration or shadowing checklist
  instead of, or in addition to, a written test.
- **Answer key**: the correct answer to every question, with the SOP step it
  comes from, kept separate from the questions handed to the employee.
- **Pass rule**: unless the operator sets their own, the employee passes only
  if every critical question is correct and at least 80% of all questions are
  correct. On a fail, the trainer reviews the missed steps with the employee,
  who retakes the check before doing the task unsupervised. Record each
  attempt.
- **Sign-off / attestation log template**: the SOP ID and approved version
  the employee was trained on, employee name, role, date trained,
  training method, trainer/supervisor name, comprehension check score and
  result (Pass, or Retrain and retest with the retest date), and a signature
  line.
- **Retraining trigger**: retrain at each scheduled SOP review (the review
  date from Phase 1), and before any revised version takes effect.

============================================================
PHASE 3: SET THE REVIEW CADENCE
============================================================

Confirm the next review date already set in the Phase 1 header, and restate
the trigger events that require an earlier review. The default cycle is 12
months. For a high-risk area (pesticides, extraction, waste disposal, cash
handling, inventory and transfers, 280E cost classification), recommend a
6-month cycle instead, and say why. Use the operator's own cycle if they have
one.

## Trigger phrases

| Phrase | What happens |
|---|---|
| "Write an SOP for [process]" | Full workflow starting at Phase 0 |
| "Turn this into an SOP" (pasted process notes) | Skips most of Phase 0, drafts directly from what's given, asks only for genuine gaps |
| "Generate training for this SOP" (existing SOP pasted or referenced) | Confirms the supplied version is approved, then runs Phase 2 against it. If it isn't approved yet, offers to review it instead |
| "Is this SOP missing anything?" | Reviews a pasted SOP against the skeleton structure and flags missing sections |
| "When should this SOP be reviewed again?" | Runs Phase 3 logic against the SOP's stated risk area |

## Guardrails

- This is not legal or compliance advice. Every regulatory citation, variance
  threshold, retention period, and review cadence should be flagged as
  "confirm with your compliance lead or counsel for this state," not
  asserted as fact. The same goes for any statement of what a state rule or
  the track-and-trace system requires (for example, which weight a Metrc
  entry should record), including one made in passing or inside a question.
- Never name an individual employee as the "owner" of an SOP. Roles stay when
  people leave; names don't.
- Don't skip the Controls and Variance section for a process that touches
  cash, inventory, or product quality just because the user didn't mention
  it. Ask.
- A template that hasn't been adapted to the operator's actual state, license
  type, and equipment is close to as risky as having no SOP. Don't let a
  generic answer stand in for operator-specific detail.
- Don't generate the training packet in Phase 2 before the operator confirms
  that version of the SOP is approved.
