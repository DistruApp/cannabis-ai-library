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

**Agent card status:** All current, except **Tom K. (expires Thursday this week).**

**Hard constraint:** 2 vault-certified staff must be present simultaneously for opening and closing register counts; at least 1 vault-certified staff on-site at all times.

**Demand data (10-week average, split by day-part):** Open (10am-2pm) ≈ 20% of daily sales, Mid (2-6pm) ≈ 35%, Close (6-10pm) ≈ 45%: a consistent after-work ramp pattern.

**Projected sales this week:** $18,200 → Mon $1,900 / Tue $2,000 / Wed $2,200 / Thu $2,400 / Fri $3,400 / Sat $3,800 / Sun $2,500

**Target labor cost:** 24% of sales

---

## 1. Labor budget

Available Labor $ = $18,200 × 24% = **$4,368**
Blended hourly rate across the roster ≈ **$17.80/hr**
Hour budget ≈ **245 hours** for the week

---

## 2. Coverage grid (full week, headcount by shift)

| Day | Open (10-2) | Mid (2-6) | Close (6-10) |
|---|---|---|---|
| Mon | 2 | 2 | 2 |
| Tue | 2 | 2 | 2 |
| Wed | 2 | 2 | 2 |
| Thu | 2 | 2 | 2 |
| Fri | 2 | 2 | **3** |
| Sat | 2 | **3** | **3** |
| Sun | 2 | 2 | 2 |

Friday and Saturday evenings need an extra body. That's where the demand curve actually peaks, not where a flat schedule usually puts the extra coverage.

---

## 3. Suggested schedule (representative days: Monday, Friday, Saturday shown in full; Tue/Wed/Thu/Sun follow Monday's lighter pattern)

**MONDAY**
- Open: Sarah M. (V), Dave S. (V)
- Mid: Sarah M. (V, cont.), Mike T.
- Close: Lisa P. (V), Dave S. (V, split shift, returns after Mid)

**FRIDAY**
- Open: Jen R. (V), Dave S. (V)
- Mid: Jen R. (V, cont.), Sarah M. (V)
- Close: Sarah M. (V, cont.), Lisa P. (V), Tom K. *(⚠ card expires Thursday, see Flags)*

**SATURDAY** *(see flag below before publishing this one)*
- Open: Jen R. (V), Dave S. (V, one-time exception, normally Mon-Fri only)
- Mid: Jen R. (V, cont.), Lisa P. (V), Mike T.
- Close: Lisa P. (V, cont.), Dave S. (V, returns), Amy W.

---

## 4. Labor summary

| | Current (flat 3-per-shift, every day) | Recommended (demand-matched) |
|---|---|---|
| Total hours | 252 | 202 |
| Total labor cost | $4,483 | $3,677 |
| Labor % of sales | 24.6% | 20.2% |
| vs. $4,368 budget | Over by $115 | Under by $691 |

---

## 5. What changed vs. current schedule

Monday-Thursday go from 3 people every shift to 2. Those shifts were staffed to habit, not to the demand curve, and the cut doesn't touch coverage minimums. Friday and Saturday evenings go the other direction, gaining a third person where the current flat schedule was actually *understaffed* relative to real traffic. Net: -50 hours and -$806 in raw labor cost, but the savings aren't the point: the schedule now has a body where the 6-10pm rush actually happens instead of being spread evenly across a week that isn't actually flat.

That said, don't just bank the $691 gap to budget. Some of that room is exactly where "side work" (opening prep, closing cleanup, restock) tends to hide. Worth checking whether current shifts already absorb that or whether it's been coming out of unpaid stay-lates.

---

## 6. Flags

- **Saturday vault coverage is a structural gap, not a one-time fix.** Only Jen R. and Lisa P. are vault-certified *and* available on Saturdays: exactly the minimum for one register count, with nothing left for the other. The schedule above only works because Dave S. agreed to a one-off exception outside his normal Mon-Fri availability. If he can't, Saturday can't legally complete both counts. Recommend cross-training a third staffer (Mike T. or Amy W. are the logical candidates) for vault certification rather than relying on exceptions week to week.
- **Dave S. hits 42 hours this week** (34 normal + 8 from the Saturday exception): 2 hours of overtime. Labeled *worth reviewing*, not *justified*: it's not a demand spike, it's the vault-coverage gap above driving it. Fixing that gap removes this overtime too.
- **Tom K.'s agent card expires Thursday.** He's scheduled for Friday close as drafted above. Do not publish that shift until the renewal is confirmed. If it slips, this is a licensing exposure, not just a coverage gap.

---

## 7. Compliance items to confirm (not legal conclusions: confirm with HR/counsel for this jurisdiction)

- Does the location's state/city have a predictive scheduling or fair workweek ordinance that would require advance notice or premium pay for changing Tom's Friday shift on short notice?
- Does Dave's split shift (Open + Close, off during Mid) trigger any reporting-pay or minimum-shift-length rule locally?
- Confirm the applicable weekly overtime threshold. This example used the standard 40-hour federal FLSA line; some states apply daily overtime rules on top of that.
- Confirm meal/rest break requirements for any 8-hour block (Sarah, Jen, Lisa, Dave all hit 8 hours on their combined shifts).

---

## 8. Data confidence notes

This run used a 10-week demand average and a single week's roster/availability snapshot. That's reasonable for a first pass, but the Saturday vault gap and Tom's card timing are exactly the kind of thing that only shows up when you actually build the schedule, not when you eyeball the data. Recommend re-running this after the Saturday cross-training question is resolved, since it changes the shape of every Saturday going forward, not just this one.
