# Staff Scheduling Optimizer

Skill: [`staff-scheduling-optimizer`](../../../skills/cannabiz-skills/operations/staff-scheduling-optimizer/SKILL.md)

## What it does

Turns demand data, a staff roster and a labor budget into a coverage-matched draft schedule for a dispensary, cultivation site or manufacturing facility. It calculates the hour budget from projected sales and a target labor percentage (or uses a production labor budget), then works out headcount shift by shift: peak-hour transactions divided by how many customers one budtender serves an hour (your number, never a default), plus fixed roles like an ID checker, and never below your own minimums (a fixed role counts toward a site-wide minimum rather than on top of it). It assigns staff by availability, hour caps, certification, hard constraints, cost and fairness. It never schedules anyone outside their availability or over their cap: a slot nobody can fill shows as an open gap with options. Before you approve the draft, it flags open gaps, overtime risk (labeled likely justified or worth reviewing), state worker credential expirations where your state requires one, and any broken hard constraint. Time-off and shift swap requests are checked with the same logic.

## When to use it

- "Build next week's schedule"
- "Check my labor cost"
- "Sam needs time off on Friday"
- "Swap two people on Saturday"
- "Am I overstaffed or understaffed tomorrow?"
- "Show me overtime risks"

## How to use it

- **Inputs:** staff roster with roles, rates and weekly hour caps; availability; 8 to 12 weeks of transactions by hour and day, or sales by hour and the average ticket (retail), or production data such as harvest, trim and packaging deadlines; how many customers one budtender serves an hour at peak; target labor percentage or labor budget; minimum staffing and hard constraints such as vault rules; worker credential expiration dates if your state requires them; location state; and upcoming demand drivers like 4/20 or promotions. Add your current schedule only if you want the draft compared with it. A CSV input template is included.
- **Tools / connectors:** none required.
- **Works in:** Claude or any LLM.
- **Limits:** not legal or HR advice. Overtime, break, predictive scheduling and worker credential questions are listed as items to confirm with HR or counsel. It drafts the schedule; a manager approves and publishes it.

## Example

**Input:** a fictional single-location recreational dispensary with 7 staff, two 6-hour shifts a day, a 10 week demand average, 18,200 dollars in projected weekly sales, a 24 percent labor target and an operator estimate of 12 customers an hour per budtender.

**Output:** a headcount table showing that only Friday and Saturday close need a second budtender, and 180 required hours for the week. The draft schedule assigns 174 of them (about $3,120, 17.1 percent of sales) and keeps everyone inside their availability and caps. It shows the other 6 hours, Sunday close, as an open gap because no vault-certified staff are available, with each option's effect on that person's hours; filling it with the one volunteer who'd stay under her cap would bring labor to about 17.8 percent. Because no current schedule was given, it makes no savings comparison. It keeps an employee off the schedule from the day his credential expires, reports the highest scheduled hours instead of declaring no overtime, and lists compliance items to confirm and notes on data confidence.
