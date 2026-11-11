---
name: cannabis-inspection-readiness--e1-co-cultivation-mip-with-doc-list
description: "evals.json #1: co-cultivation-mip-with-doc-list"
tags: ["behaviour", "cannabis-inspection-readiness", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

State inspection for our renewal is in 10 days. We're Example Gardens in Denver, retail cultivation + MIP (infused products manufacturer). Here's a list of what we have. What do we need to get ready?

(The attached files are in the `resources` folder: `document_list.md`.)
