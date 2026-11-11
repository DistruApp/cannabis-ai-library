---
name: staff-scheduling-optimizer--e1-weekly-schedule-with-gap
description: "evals.json #1: weekly-schedule-with-gap"
tags: ["behaviour", "staff-scheduling-optimizer", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Build the schedule for Example Valley Dispensary for the week of Monday 2026-11-16 to Sunday 2026-11-22. Roster, availability and caps are in the sheet. Projected sales: Mon 1900, Tue 2000, Wed 2200, Thu 2400, Fri 3400, Sat 3800, Sun 2500. Target labor 24%. Two shifts a day, 10-4 and 4-10. Always 2 people on, at least one vault-certified on every shift, and a front-desk ID checker Friday and Saturday close. Average ticket is $45, busiest hour is about 30% of a shift, and a budtender handles about 12 customers an hour. Worker credential expiry dates are in the sheet. We're one store in Example State (fictional); every employee needs a state worker credential, and we'll confirm labor rules with HR. This is a fresh schedule: nobody has other hours this week, and I'm not giving you a current schedule to compare against.

(The attached files are in the `resources` folder: `example-valley-roster.csv`.)
