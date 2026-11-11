---
name: staff-scheduling-optimizer--e4-fixed-role-counts-toward-minimum
description: "evals.json #4: fixed-role-counts-toward-minimum"
tags: ["behaviour", "staff-scheduling-optimizer", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Quick one for Tuesday open at Example Valley (10-4). Peak hour is about 12 customers, and a budtender handles about 12 an hour. Our rule is at least 2 people on site at all times, and we want someone on the door checking IDs every shift. How many people do I need on that shift?
