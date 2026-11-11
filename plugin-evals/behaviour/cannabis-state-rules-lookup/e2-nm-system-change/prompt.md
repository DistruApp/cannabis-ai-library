---
name: cannabis-state-rules-lookup--e2-nm-system-change
description: "evals.json #2: nm-system-change"
tags: ["behaviour", "cannabis-state-rules-lookup", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

new mexico retailer here - our POS integrates with biotrack, anything we need to know about traceability right now?
