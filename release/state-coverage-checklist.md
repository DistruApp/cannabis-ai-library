# State coverage checklist (Gate 3)

Use this for every pilot state in `state-profiles.md` at each release and every 90 days. The goal is to find rules the profile gets **wrong** or **leaves out**.

## How to run it

1. **Answer first, compare second.** The researcher answers every question below from the regulator's own site, the state code or register, or an official form, *before* opening `state-profiles.md`. Cornell LII copies of state regulations are acceptable as a secondary text source; say which you used. If a site blocks automated access, mark it BLOCKED and give the URL a human should open.
2. For each answer record: citation, exact quoted operative text (40 words or fewer), URL, date accessed, confidence.
3. Then compare with the profile and the skills (`grep -rn "<citation>" skills docs`) and classify each question:

| Class | Meaning | Action before release |
|---|---|---|
| MATCH | Profile states it and agrees with the source | None |
| OMISSION | A binding rule the profile and skills don't mention | **Add it** (P0 if it carries a deadline or notice) |
| CONFLICT | Profile says something different from the source | **Fix it** |
| PROFILE-UNVERIFIED-OK | Profile already labels it UNVERIFIED / NEEDS VERIFICATION | Try to verify; keep the label if you can't |
| COULDN'T-VERIFY | No primary source reachable | Leave the profile's label; list it in the release notes |

4. Also check every quote in the profile appears verbatim at its cited source, and no review date is more than 90 days old.
5. Fix the canonical profile (`skills/cannabiz-skills/compliance/cannabis-state-rules-lookup/references/state-profiles.md`), copy it to the other compliance skills, and run `python3 scripts/check_repo.py`.
6. The compliance lead reviews the diff and signs the release report.

## Questions (per state)

| # | Question | Skills that rely on it |
|---|---|---|
| Q1 | Which track-and-trace system is required, and how quickly must activities be recorded in it? | state-rules-lookup, traceability-reconciliation, transfer-manifest-precheck |
| Q2 | How often must inventory be reconciled against track-and-trace? | traceability-reconciliation, inspection-readiness |
| Q3 | What counts as a "significant" inventory discrepancy (threshold and its base)? | traceability-reconciliation |
| Q4 | Who must be notified of a significant discrepancy, theft, loss or diversion, and within what deadline (regulator, law enforcement, form)? List every separate deadline. | traceability-reconciliation, inspection-readiness, state-rules-lookup |
| Q5 | Inventory adjustments: is a reason required, and what is the deadline for correcting data-entry errors? | traceability-reconciliation |
| Q6 | Transfers: what must be on or travel with the manifest, and what lab-testing status is required before a licensee-to-licensee transfer or sale? | transfer-manifest-precheck |
| Q7 | Records retention period for inventory and transfer records | inspection-readiness, sop-generator-trainer |
| Q8 | Cannabis waste and destruction: notice, holding period, witness or video requirements | inspection-readiness, sop-generator-trainer |
| Q9 | Worker credential, badge or agent card requirement for employees | staff-scheduling-optimizer, inspection-readiness |

Federal: check the "Federal status" line in `cannabis-state-rules-lookup/SKILL.md` against federalregister.gov (what was rescheduled, effective date, any pending rulemaking or hearing).

## When a new state becomes a pilot state

Answer all nine questions for it before it is added to "Pilot states (deep coverage)". Until then it stays under "Other states" with the system only.
