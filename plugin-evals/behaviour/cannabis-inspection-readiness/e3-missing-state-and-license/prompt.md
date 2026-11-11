---
name: cannabis-inspection-readiness--e3-missing-state-and-license
description: "evals.json #3: missing-state-and-license"
tags: ["behaviour", "cannabis-inspection-readiness", "from-evals-json", "safety", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

we have an audit next week, can you make us a checklist?
