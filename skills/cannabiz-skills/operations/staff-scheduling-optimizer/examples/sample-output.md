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

Budtenders needed = peak-hour transactions ÷ 12, rounded up. Headcount = the larger of budtenders needed and the 2-person minimum, plus any fixed role.

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
| **Filled** | **29** | **174** | | **$3,120** |
| Open gap (Sun close) | 1 | 6 | | about $108 if filled at $18/hr |

---

## 4. Labor summary

| | Current (flat 3 per shift, every day) | Recommended (demand-matched, gap filled) |
|---|---|---|
| Total hours | 252 | 180 |
| Total labor cost | $4,483 | about $3,228 |
| Labor % of sales | 24.6% | about 17.7% |
| vs. $4,368 budget | Over by $115 | Under by about $1,140 |

---

## 5. What changed vs. current schedule

Every shift except Friday and Saturday close drops from 3 people to 2. The demand data says one budtender covers the peak hour on those shifts, so the 2-person minimum is what sets their headcount. Friday and Saturday close stay at 3: two budtenders for the evening peak plus the front-desk ID check. Net: 72 fewer hours and about $1,255 less labor.

Don't treat the gap to budget as savings to bank. If the manager sees long waits on Friday or Saturday close, adding a third budtender there costs about $210 a week and still lands well under budget. Some of the room may also be covering side work (opening prep, closing cleanup, restock) that the current schedule absorbs.

---

## 6. Flags

- **Open gap: Sunday close has no vault-certified staff.** Sarah, Dave and Jen aren't available Sundays, and Lisa already opens. The skill did not schedule anyone outside their availability or over their cap to close it. Options for the manager:
  - ask Sarah, Dave or Jen whether one of them will volunteer outside their usual availability, or Lisa (for her it would be a 12-hour day and 2 hours over her 28-hour cap);
  - get Mike T. or Amy W. vault-certified, which also fixes every future Sunday;
  - change the Sunday rule or hours, if the operator's own policy allows it.
- **Tom K.'s credential expires Sunday.** He's scheduled Wednesday, Thursday and Saturday, all before it expires, and not Sunday. Confirm the renewal before scheduling him next week.
- **Overtime:** none this week. The highest is 30 hours (Dave, Jen, Mike).
- **Mike T. is at his 30-hour cap.** Any swap that adds a shift for Mike needs a different person.

---

## 7. Compliance items to confirm (not legal conclusions: confirm with HR/counsel for this jurisdiction)

- Do any local predictive scheduling or fair workweek rules require advance notice or premium pay if the Sunday gap is filled late?
- Close-then-open turnarounds: Jen (Fri close → Sat open), Dave (Thu close → Fri open) and Lisa (Sat close → Sun open) each get 12 hours between shifts. Confirm that meets any local rest-between-shifts rule.
- Confirm the meal and rest break rules for a 6-hour shift.
- Confirm whether your state requires a worker credential, and what it's called. This example assumed it does.

---

## 8. Data confidence notes

The headcount rests on two operator numbers: 12 customers an hour per budtender, and the 30% peak-hour share. If either is off, Friday and Saturday close are the shifts most likely to change. Recommend checking actual Friday and Saturday wait times after the first week, and re-running once the Sunday vault-certification question is settled.
