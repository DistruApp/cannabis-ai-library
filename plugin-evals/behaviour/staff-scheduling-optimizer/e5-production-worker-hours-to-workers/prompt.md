---
name: staff-scheduling-optimizer--e5-production-worker-hours-to-workers
description: "evals.json #5: production-worker-hours-to-workers"
tags: ["behaviour", "staff-scheduling-optimizer", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We need to package 480 units of pre-rolls by end of day Thursday. One packager does about 20 units an hour. The shift is 7 hours, and after breaks and cleanup each person gets about 6 productive hours. How many packagers should I schedule for Thursday?
