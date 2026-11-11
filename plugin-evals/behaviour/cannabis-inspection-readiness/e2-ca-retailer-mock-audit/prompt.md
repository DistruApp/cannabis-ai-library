---
name: cannabis-inspection-readiness--e2-ca-retailer-mock-audit
description: "evals.json #2: ca-retailer-mock-audit"
tags: ["behaviour", "cannabis-inspection-readiness", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Run a mock audit for our California storefront retailer. No inspection scheduled, just want to be ready. We use Metrc and Dutchie POS.
