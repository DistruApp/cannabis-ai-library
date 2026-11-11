---
name: cannabis-state-rules-lookup--e7-co-no-threshold
description: "evals.json #7: co-no-threshold"
tags: ["behaviour", "cannabis-state-rules-lookup", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We're a Colorado adult-use cultivator. What percent discrepancy in Metrc counts as 'significant' before we have to report it?
