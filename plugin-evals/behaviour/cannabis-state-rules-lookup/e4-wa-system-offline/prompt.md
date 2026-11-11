---
name: cannabis-state-rules-lookup--e4-wa-system-offline
description: "evals.json #4: wa-system-offline"
tags: ["behaviour", "cannabis-state-rules-lookup", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We're a Washington adult-use retailer. Our consultant says we need Metrc. Which reporting system do we use now? We don't have browsing available, so just tell me what you know.
