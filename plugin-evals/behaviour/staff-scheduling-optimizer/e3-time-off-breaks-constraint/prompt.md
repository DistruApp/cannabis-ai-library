---
name: staff-scheduling-optimizer--e3-time-off-breaks-constraint
description: "evals.json #3: time-off-breaks-constraint"
tags: ["behaviour", "staff-scheduling-optimizer", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Lisa P. needs Saturday off. Who can cover her Saturday close shift?

(The attached files are in the `resources` folder: `example-valley-current-schedule.md`.)
