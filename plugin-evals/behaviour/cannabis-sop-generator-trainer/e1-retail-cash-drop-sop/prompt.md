---
name: cannabis-sop-generator-trainer--e1-retail-cash-drop-sop
description: "evals.json #1: retail-cash-drop-sop"
tags: ["behaviour", "cannabis-sop-generator-trainer", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We're a fictional adult-use dispensary in Michigan (Example Valley Dispensary). Write an SOP for end-of-shift cash drops: the budtender counts their drawer, a shift lead verifies, and the cash goes in the drop safe. We use our POS's drawer report.
