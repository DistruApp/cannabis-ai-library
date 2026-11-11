# Staff Scheduling Optimizer: Simulated Run

*All data below is fictional (Example Valley Dispensary, single recreational location), built to demonstrate what the skill's output looks like. Not real operator data.*

---

## Inputs fed to the skill

**Staff roster & availability**

| Staff | Role | Rate | Vault-certified | Availability | Weekly hour cap |
|---|---|---|---|---|---|
| Sarah M. | Lead Budtender | $19/hr | Yes | Mon-Fri | 34 |
| Dave S. | Compliance/Inventory Tech | $20/hr | Yes | Mon-Fri | 34 |
| Jen R. | Budtender | $18/hr | Yes | Tue-Sat | 34 |
| Lisa P. | Budtender | $17.50/hr | Yes | Mon, Wed, Fri, Sat, Sun | 28 |
| Tom K. | Budtender | $17/hr | No | Wed-Sun | 32 |
| Mike T. | Budtender | $17/hr | No | All days | 30 |
| Amy W. | Front Desk | $16/hr | No | All days | 25 |

**Location:** one store in Example State (fictional). Every compliance item below is a question for the operator's HR or counsel, not a conclusion.

**Other hours:** none. Nobody works anywhere else this week, so the hours below are everyone's full week.

**Current schedule:** not provided, so this run makes no comparison with it.

**State worker credential:** this operator's state requires a cannabis worker credential for every scheduled employee (confirm the rule for your own state). All are current except **Tom K., whose credential expires Sunday this week.**

**Shifts:** Open 10am-4pm and Close 4pm-10pm (6 hours each).

**Operator rules (hard constraints):**
- At least 2 staff on site at all times.
- At least 1 vault-certified staff member on every shift (register counts need a vault-certified person plus a second person).
- A front-desk ID checker on Friday and Saturday close.

**Demand data (10-week POS average):** Open ≈ 40% of daily sales, Close ≈ 60%. Average ticket $45. The busiest hour of a shift carries about 30% of that shift's transactions.

**Service rate (from the operator):** one budtender serves about 12 customers an hour at peak. The operator estimated this from a Friday they consider well staffed. The skill asked for it; it never assumes a number.

**Projected sales this week:** $18,200 → Mon $1,900 / Tue $2,000 / Wed $2,200 / Thu $2,400 / Fri $3,400 / Sat $3,800 / Sun $2,500

**Target labor cost:** 24% of sales

---

## 1. Labor budget

Available Labor $ = $18,200 × 24% = **$4,368**
Blended hourly rate across the roster ≈ **$17.79/hr**
Hour budget ≈ **245 hours** for the week

---

## 2. Headcount by shift

Budtenders needed = peak-hour transactions ÷ 12, rounded up. Demand staff = budtenders needed + any fixed role (the front-desk ID checker). Headcount = the larger of demand staff and the 2-person site minimum; the ID checker counts toward that minimum, so it isn't added on top of it. The vault rule doesn't add a person: one of each shift's people has to be vault-certified.

| Day | Shift | Projected sales | Transactions (÷ $45) | Peak hour (× 30%) | Budtenders needed | Fixed roles | Headcount |
|---|---|---|---|---|---|---|---|
| Mon | Open | $760 | 16.9 | 5.1 | 1 | | 2 (minimum) |
| Mon | Close | $1,140 | 25.3 | 7.6 | 1 | | 2 (minimum) |
| Tue | Open | $800 | 17.8 | 5.3 | 1 | | 2 (minimum) |
| Tue | Close | $1,200 | 26.7 | 8.0 | 1 | | 2 (minimum) |
| Wed | Open | $880 | 19.6 | 5.9 | 1 | | 2 (minimum) |
| Wed | Close | $1,320 | 29.3 | 8.8 | 1 | | 2 (minimum) |
| Thu | Open | $960 | 21.3 | 6.4 | 1 | | 2 (minimum) |
| Thu | Close | $1,440 | 32.0 | 9.6 | 1 | | 2 (minimum) |
| Fri | Open | $1,360 | 30.2 | 9.1 | 1 | | 2 (minimum) |
| Fri | Close | $2,040 | 45.3 | 13.6 | **2** | Front desk | **3** |
| Sat | Open | $1,520 | 33.8 | 10.1 | 1 | | 2 (minimum) |
| Sat | Close | $2,280 | 50.7 | 15.2 | **2** | Front desk | **3** |
| Sun | Open | $1,000 | 22.2 | 6.7 | 1 | | 2 (minimum) |
| Sun | Close | $1,500 | 33.3 | 10.0 | 1 | | 2 (minimum) |

Total: 30 shifts × 6 hours = **180 hours**. Only Friday and Saturday evenings need a second budtender; everywhere else the 2-person minimum sets the headcount, not demand.

---

## 3. Suggested schedule (draft for manager approval)

(V) = vault-certified.

| Day | Open (10am-4pm) | Close (4pm-10pm) |
|---|---|---|
| Mon | Sarah M. (V), Mike T. | Dave S. (V), Lisa P. (V) |
| Tue | Jen R. (V), Mike T. | Sarah M. (V), Dave S. (V) |
| Wed | Dave S. (V), Tom K. | Jen R. (V), Lisa P. (V) |
| Thu | Sarah M. (V), Tom K. | Jen R. (V), Dave S. (V) |
| Fri | Dave S. (V), Mike T. | Sarah M. (V), Jen R. (V), Amy W. (front desk) |
| Sat | Jen R. (V), Tom K. | Lisa P. (V), Mike T., Amy W. (front desk) |
| Sun | Lisa P. (V), Amy W. | Mike T., **OPEN GAP: vault-certified staff needed** |

Everyone is inside their stated availability and weekly hour cap:

| Staff | Shifts | Hours | Cap | Cost |
|---|---|---|---|---|
| Sarah M. | 4 | 24 | 34 | $456 |
| Dave S. | 5 | 30 | 34 | $600 |
| Jen R. | 5 | 30 | 34 | $540 |
| Lisa P. | 4 | 24 | 28 | $420 |
| Tom K. | 3 | 18 | 32 | $306 |
| Mike T. | 5 | 30 | 30 | $510 |
| Amy W. | 3 | 18 | 25 | $288 |
| **Assigned** | **29** | **174** | | **$3,120** |
| Open gap (Sun close) | 1 | 6 | | not filled; see Flags |

---

## 4. Labor summary

| | Hours | Labor cost | % of $18,200 sales | vs. $4,368 budget |
|---|---|---|---|---|
| Required by the headcount table | 180 | | | |
| Assigned in this draft | 174 | $3,120 | 17.1% | under by $1,248 |
| Open gap (Sunday close) | 6 | | | |
| If the gap is filled by Sarah M. at $19/hr (conditional: only if she volunteers) | 180 | about $3,234 | about 17.8% | under by about $1,134 |

Blended rate across the roster ≈ $17.79/hr; hour budget ≈ 245 hours.

---

## 5. What changed vs. current schedule

The current schedule wasn't provided, so there's no comparison and no savings figure. Share it (each shift's assignments, or hours and cost by day) to see net hours added or removed by day.

Don't treat the gap to budget as savings to bank. If the manager sees long waits on Friday or Saturday close, adding a third budtender there costs about $210 a week and still lands well under budget. Some of the room may also be covering side work (opening prep, closing cleanup, restock) that this draft doesn't schedule.

---

## 6. Flags

- **Open gap: Sunday close has no vault-certified staff.** Only three people can work Sunday this week (Lisa, Mike and Amy; Tom is off because his credential expires that day) for four slots, and Lisa, the only vault-certified one, already opens. The skill did not schedule anyone outside their availability or over their cap to close it. Options for the manager:

  | Option | Hours after | What still blocks it |
  |---|---|---|
  | Sarah M. volunteers | 30 of 34 | Sunday is outside her stated availability: only if she agrees |
  | Dave S. or Jen R. volunteers | 36 of 34 | Over cap, and Sunday is outside their availability: not an option unless one of their weekday shifts moves to someone else |
  | Lisa P. also closes (a double) | 34 of 28 | Over cap and a 12-hour day: not an option unless the manager changes her cap; a double may also trigger daily overtime or break rules |
  | Get Mike T. vault-certified | Mike 30 of 30 (no change; he already closes Sunday) | Doesn't fill this Sunday by itself: the slot still needs a second person. If Tom's renewal is also confirmed, a week like this one could run Sunday as Lisa + Amy open and Mike + Tom close, inside everyone's availability and caps (Tom 24 of 32) |
  | Change the Sunday rule or hours | | Only if the operator's own policy allows it |

- **Tom K.'s credential expires Sunday.** He's scheduled Wednesday, Thursday and Saturday, all before it expires, and not on Sunday, the expiry day. Confirm the renewal before scheduling him next week.
- **Overtime:** no one is scheduled above 30 hours in this draft (Dave, Jen and Mike are at 30). Whether any overtime applies depends on Example State's daily and weekly thresholds and the operator's workweek; see the compliance items.
- **Mike T. is at his 30-hour cap.** Any swap that adds a shift for Mike needs a different person.

---

## 7. Compliance items to confirm (not legal conclusions: confirm with HR/counsel for this jurisdiction)

- Do any local predictive scheduling or fair workweek rules require advance notice or premium pay if the Sunday gap is filled late?
- Close-then-open turnarounds: Dave (Tue close → Wed open, and Thu close → Fri open), Jen (Fri close → Sat open) and Lisa (Sat close → Sun open) each get 12 hours between shifts. Confirm that meets any local rest-between-shifts rule.
- Confirm the meal and rest break rules for a 6-hour shift.
- Confirm the daily and weekly overtime thresholds and when the operator's workweek starts and ends.
- Confirm whether a worker credential is still valid on its expiry date. This draft leaves Tom off Sunday either way.
- Confirm whether your state requires a worker credential, and what it's called. This example assumed it does.

---

## 8. Data confidence notes

The headcount rests on two operator numbers: 12 customers an hour per budtender, and the 30% peak-hour share. If either is off, Friday and Saturday close are the shifts most likely to change. Recommend checking actual Friday and Saturday wait times after the first week, and re-running once the Sunday vault-certification question is settled.
