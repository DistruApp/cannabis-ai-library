---
name: cannabis-sop-generator-trainer--e2-training-for-approved-sop
description: "evals.json #2: training-for-approved-sop"
tags: ["behaviour", "cannabis-sop-generator-trainer", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Here's our approved outbound order SOP. Build the training packet for pickers and leads.

(The attached files are in the `resources` folder: `approved_outbound_order_sop.md`.)
