# Staff Scheduling Optimizer

Skill: [`staff-scheduling-optimizer`](../../../skills/cannabiz-skills/operations/staff-scheduling-optimizer/SKILL.md)

## What it does

Turns demand data, a staff roster and a labor budget into a coverage-matched schedule for a dispensary, cultivation site or manufacturing facility. It calculates the hour budget from projected sales and a target labor percentage (or uses a production labor budget), maps the demand curve by hour and day, builds a coverage grid, and assigns staff by availability, certification, hard constraints, cost and fairness. Before anything is published it flags over and understaffing, overtime risk (labeled likely justified or worth reviewing), agent card expirations and any broken hard constraint. Time-off and shift swap requests are checked with the same logic.

## When to use it

- "Build next week's schedule"
- "Check my labor cost"
- "Sam needs time off on Friday"
- "Swap two people on Saturday"
- "Am I overstaffed or understaffed tomorrow?"
- "Show me overtime risks"

## How to use it

- **Inputs:** staff roster with roles, rates and weekly hour caps; availability; 8 to 12 weeks of sales by hour and day (retail) or production data such as harvest, trim and packaging deadlines; target labor percentage or labor budget; coverage requirements per shift; hard constraints such as vault minimums; agent card expiration dates; location state; and upcoming demand drivers like 4/20 or promotions. A CSV input template is included.
- **Tools / connectors:** none required.
- **Works in:** Claude or any LLM.
- **Limits:** not legal or HR advice. Overtime, break, predictive scheduling and agent card questions are listed as items to confirm with HR or counsel.

## Example

**Input:** a fictional single-location recreational dispensary with 7 staff, a 10 week demand average showing an evening rush, 18,200 dollars in projected weekly sales and a 24 percent labor target.

**Output:** a demand-matched schedule that cuts weekday shifts from 3 people to 2 and adds a third person on Friday and Saturday evenings, bringing labor from 24.6 to 20.2 percent of sales. It flags a structural Saturday vault coverage gap, 2 hours of overtime worth reviewing, and an agent card that expires the day before a scheduled shift, then lists compliance items to confirm and notes on data confidence.
