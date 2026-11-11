---
name: cannabis-replenishment-planner--e3-ambiguous-columns-missing-lead-times
description: "evals.json #3: ambiguous-columns-missing-lead-times"
tags: ["behaviour", "cannabis-replenishment-planner", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

what do i need to reorder? sales and inventory attached

(The attached files are in the `resources` folder: `sales_by_product_no_sku.csv`, `onhand_messy.csv`.)
