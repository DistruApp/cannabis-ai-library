---
name: cannabis-state-rules-lookup--e5-ma-medical-waste-witness
description: "evals.json #5: ma-medical-waste-witness"
tags: ["behaviour", "cannabis-state-rules-lookup", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We're a Massachusetts medical-only dispensary (we used to be called an MTC). Can we cut our cannabis-waste destruction process from two agents witnessing to one?
