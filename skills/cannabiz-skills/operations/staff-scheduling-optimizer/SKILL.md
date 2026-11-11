---
name: staff-scheduling-optimizer
description: >-
  Recommends cannabis dispensary and production staffing by shift from real
  demand (POS transactions or production data), a labor budget and staff
  availability, then drafts a schedule for manager approval. Flags open
  coverage gaps, overtime risk, hour-cap and hard-constraint problems, and
  state worker credential (agent card or badge) expirations where the state
  requires one. Handles time-off requests and shift swaps with the same
  logic. Use when building or checking a weekly staff schedule, asking whether
  a shift or day is overstaffed or understaffed, comparing labor cost to a
  target percentage, working out how many budtenders, trimmers or packagers a
  shift or harvest needs, checking overtime risk, or processing a time-off,
  call-out or swap request, including "who can cover this shift?". Not for payroll, hiring, HR policy or legal
  advice on labor law.
license: MIT
metadata:
  version: "1.1"
  category: operations
  author: Distru
  supporting-files:
    - templates/schedule-input-template.csv
    - examples/sample-output.md
---

# Staff Scheduling Optimizer

Turn demand data, a staff roster and a labor budget into a coverage-matched
draft schedule for a cannabis dispensary, cultivation site or
manufacturing/processing facility, and answer narrower one-off scheduling
questions with the same logic. The manager approves the schedule; this skill
never publishes it.

If the user has `templates/schedule-input-template.csv` filled out, read it for
the staff roster, availability, rates and credential data instead of asking
for each field individually.

## Core principles

1. Demand-driven coverage. Schedule to the forecast, not to habit. If Tuesdays
   run half of Friday's volume, don't staff them the same.
2. Labor budget targeting. Work within a target labor cost as a percentage of
   sales (retail) or a production labor budget (cultivation/manufacturing).
   Every hour above target eats margin; every hour below risks service or output.
3. Fairness and compliance together. Rotate undesirable shifts, respect
   availability, and stay inside labor law and cannabis-specific regulatory
   constraints. These aren't optional extras: they're part of a "good" schedule.

## Inputs to gather before producing anything

- Staff roster: names, roles, hourly rates, current weekly hours
- Availability: days/times each person can and cannot work
- Demand data: for retail, historical transactions by hour and day from the
  POS (8-12 weeks ideal), or sales by hour plus the average ticket; for
  cultivation/manufacturing, production data instead: harvest dates, trim
  schedules, packaging deadlines, batch throughput
- Service rate (retail): how many customers one budtender can serve in an
  hour at peak. Ask the operator. If they don't know, offer to estimate it
  from a past shift they consider well staffed (that shift's peak-hour
  transactions ÷ budtenders on the floor). Never use a default number. For
  production, the equivalent is units per worker-hour for each line.
- Target labor cost as % of sales (retail) or labor budget for the period
  (cultivation/manufacturing)
- Coverage requirements per shift/role (e.g., "2 budtenders + 1 vault-certified
  staffer for the 5-7pm window")
- Hard constraints that cannot be traded away, such as a two-person minimum at
  the vault or point of sale, or a licensed/permitted agent required on-site
  during specific hours
- State worker credential status, where the state requires one: the
  cannabis employee registration, badge, permit or agent card, and whether
  it's current through the scheduling period. Requirements and names differ by
  state, and some states have none; ask the operator, and mark the
  requirement NEEDS VERIFICATION if they aren't sure. Where it applies, an
  expired credential can put the license at risk, not just create a coverage
  gap.
- State/jurisdiction of each location
- Known upcoming demand drivers: 4/20, holidays, promotions, product drops,
  harvest windows
- The current schedule, only if the manager wants the draft compared with it:
  each shift's assignments, or at least hours and cost by day. Without it,
  don't compare.

If any of this is missing, ask for it before producing a schedule. Don't guess
at demand, budgets, staffing costs or a current schedule.

**Check the inputs before using them.** Skip wholly blank rows and the
template's `EXAMPLE` rows. Treat a placeholder such as `YYYY-MM-DD`, a value
that isn't a number where one is needed, a zero or negative rate, ticket,
service rate or throughput, or a formula instead of its result as missing, and
ask for the real value rather than repairing it. If the same person appears
twice, ask which row is right; never count them as two people. Confirm units
before dividing (grams vs. kilograms, units vs. cases, 24 vs. 0.24 for a
percentage, a decimal comma such as "17,50").

## What to do with it

1. **Calculate the labor budget (retail).**
   Available Labor $ = Projected Sales × Target Labor %
   Hour Budget = Available Labor $ ÷ Blended Hourly Rate
   For cultivation/manufacturing, use the stated labor budget or cost-per-unit
   target directly instead of a sales-driven calculation.

2. **Map the demand curve.** Aggregate transactions (retail) or production
   volume (cultivation/manufacturing) by hour and day of week. Identify peaks,
   ramp-up/ramp-down windows, and day-of-week variation.

3. **Turn demand into headcount.** Break each day into the operation's actual
   shifts, then for each shift:
   1. Transactions in the shift: from the POS, or projected shift sales ÷
      average ticket.
   2. Peak-hour transactions: the busiest hour's share of the shift, from the
      same data.
   3. Floor staff needed = peak-hour transactions ÷ the operator's service
      rate, rounded up.
   4. Add fixed roles the operator requires that don't serve customers (ID
      check or front desk, vault or inventory lead, manager on duty): demand
      staff = floor staff + fixed roles.
   5. Apply the operator's minimum. A minimum for the whole site ("at least 2
      people on at all times") counts everyone on shift, fixed roles
      included, so headcount = the larger of demand staff and the site
      minimum. Don't add fixed roles on top of a site minimum they already
      help meet. A role or certification rule (for example, a vault-certified
      person on every shift) doesn't add a person by itself: fill one of
      the slots with someone qualified, and if no one qualified is
      available, that slot is an OPEN GAP (step 4).
   6. Hours = headcount × shift length. Total them against the hour budget.
      If the total is over budget, don't cut below a hard constraint. Show
      the trade-off instead: which shifts would lose a person, what that does
      to the peak hour (customers per budtender), and let the manager choose.

   Show this calculation in the output so the manager can check it. For
   cultivation/manufacturing, work from the output target instead of
   transactions: worker-hours needed = output target ÷ units per worker-hour
   (in the same units), then workers needed = worker-hours ÷ productive hours
   each worker has before the deadline, rounded up. For example, 480 units at
   20 units per worker-hour is 24 worker-hours; with 6 productive hours each,
   that's 4 workers, not 24. Ask how much of the shift is productive (breaks,
   setup, cleaning and changeovers come out) rather than assuming the full
   shift. Then apply minimums and fixed roles as in steps 4 and 5.

4. **Assign staff.** Match availability and weekly hour caps (hard
   constraints: never schedule anyone outside their stated availability or
   above their cap) → role/certification match → hard constraints (vault
   minimums, credential currency) → rate optimization (lower-cost, qualified
   staff for slower periods where it doesn't compromise coverage) → fairness
   (rotate closing shifts, weekends, and less desirable slots so the same
   people aren't always stuck with them).

   If no one available and qualified can fill a slot, leave it in the
   schedule as **OPEN GAP** with what's needed (for example "vault-certified
   staff needed"). Don't assume someone will agree to work outside their
   availability, and don't give one person both shifts in a day (a double)
   to cover a gap: a double can trigger daily overtime or break rules, and
   it's the manager's call. Show the OPEN GAP and list the options for the
   manager: a double, who could be asked to volunteer, cross-training, or
   changing the shift. For each person named,
   show their hours and cap after the change and anything that still blocks
   them (outside availability, over cap, a double, credential). Name only
   people who'd stay within their cap, or mark the ones who wouldn't as not
   an option unless the manager changes something else. Don't call training
   or certification a fix unless it also leaves an available person for the
   slot.

5. **Flag issues before presenting the draft. Don't bury them in the schedule.**
   - Over/understaffing relative to the demand curve
   - Overtime risk: label each flag "likely justified" (ties to a real demand
     spike) or "worth reviewing" (looks like a byproduct of understaffing
     elsewhere in the week). Say what you actually checked (for example "no
     one is scheduled above 30 hours in this draft"); whether overtime
     applies depends on the jurisdiction's daily and weekly thresholds, the
     employer's workweek and hours worked elsewhere, so it stays an item to
     confirm, never "no overtime".
   - Every OPEN GAP, with the options to fill it
   - Any employee whose state worker credential expires within the scheduling
     period, where the state requires one. Don't schedule them on or after
     the expiry date unless the renewal is confirmed or the operator confirms
     the credential is valid through the end of that shift. Whether a
     credential is valid on its expiry date varies, so treat that day as
     NEEDS VERIFICATION; leaving it off is this skill's conservative default,
     not a legal rule.
   - Any shift that would violate a stated hard constraint if left as drafted

6. **Handle time-off and swap requests with the same rigor as the initial
   build.** Check whether coverage minimums (including vault and credential
   constraints) still hold after the change; identify eligible replacements
   (same role/certification, available, under their max hours); check overtime
   implications; surface the recommendation with reasoning, don't execute it
   silently.

7. **Run the compliance pass before finalizing.** Check for weekly/state
   overtime thresholds, required meal/rest breaks, "clopening" restrictions,
   maximum consecutive days worked, predictive/fair workweek scheduling rules
   (some cities and states have them; ask the operator whether one applies
   and mark it NEEDS VERIFICATION rather than listing places from memory), and,
   where the state requires one, every scheduled employee's worker credential
   being valid through the shift. Present these as items to confirm, never as
   legal conclusions: write "confirm whether X applies", not "you can't
   legally do X".

8. **Be explicit about data limits.** If demand data only covers a short or
   unusual window, or role/location breakdown is missing, say so and recommend
   validating before locking in the schedule.

## Output format

- **Headcount by shift**: the step 3 calculation, shift by shift
- **Suggested Staffing Schedule (draft for manager approval)**: day/shift/role
  breakdown, with any OPEN GAP shown in place
- **Labor summary**: required hours, assigned hours and open-gap hours
  separately; cost of the assigned hours vs. budget and target; blended rate.
  Any cost that assumes an open gap gets filled is labelled as conditional,
  with the rate assumed.
- **What changed vs. current schedule**: net hours added/removed by day, only
  when the manager supplied the current schedule. Otherwise say it wasn't
  provided and don't estimate savings.
- **Flags**: open gaps with options, overtime risk (justified vs. worth
  reviewing), credential expirations, hard-constraint problems
- **Compliance items to confirm**: jurisdiction-specific questions for HR/legal
- **Data confidence notes**: anything limiting how much weight to put on the
  recommendation

See `examples/sample-output.md` for a full worked example against fictional
data.

## Trigger phrases

| Phrase | What happens |
|---|---|
| "Build next week's schedule" | Full workflow: gather inputs → calculate budget → headcount → assign → flag → present the draft for manager approval |
| "Check my labor cost" | Compares current/proposed schedule against budget |
| "[Name] needs time off on [date]" | Finds coverage, flags overtime/constraint implications, recommends a replacement |
| "Swap [name1] and [name2] on [date]" | Validates against availability, certification, hard constraints, and overtime |
| "Am I overstaffed/understaffed tomorrow?" | Compares scheduled hours to the demand curve for that day |
| "Show me overtime risks" | Scans the current schedule for employees approaching weekly thresholds |

## Guardrails

- This is not legal, tax, or HR advice. Route overtime, meal/rest break,
  predictive-scheduling, and worker-credential/licensing questions to the
  operator's HR/employment counsel or compliance lead. Don't assert them as
  settled fact.
- Labor rules are not uniform across states or even across cities in the same
  state. Don't assume otherwise.
- Cost-cutting isn't the objective on its own: matching labor to demand
  sometimes means adding a shift, not just removing one.
- Never silently drop a stated hard constraint to make a schedule "work."
  Never schedule anyone outside their availability or over their hour cap to
  close a gap; show the gap.
- Never publish, post or send the schedule. Present it as a draft.
