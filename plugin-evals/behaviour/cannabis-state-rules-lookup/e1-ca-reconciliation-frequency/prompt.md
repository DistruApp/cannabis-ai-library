---
name: cannabis-state-rules-lookup--e1-ca-reconciliation-frequency
description: "evals.json #1: ca-reconciliation-frequency"
tags: ["behaviour", "cannabis-state-rules-lookup", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We're a California distributor. How often are we required to reconcile Metrc and what happens if we're off?
