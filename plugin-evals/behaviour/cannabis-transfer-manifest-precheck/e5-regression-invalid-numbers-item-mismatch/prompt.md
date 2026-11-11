---
name: cannabis-transfer-manifest-precheck--e5-regression-invalid-numbers-item-mismatch
description: "evals.json #5: regression-invalid-numbers-item-mismatch"
tags: ["behaviour", "cannabis-transfer-manifest-precheck", "from-evals-json", "safety", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

SO-3061 goes out at 1pm. Order, draft manifest and today's Metrc active packages attached. TestPassed is our only passing status. Michigan processor shipping to a provisioning center. A few quantities were typed in by hand from a European spreadsheet.

(The attached files are in the `resources` folder: `regression_sales_order_SO-3061.csv`, `regression_draft_manifest_SO-3061.csv`, `regression_inventory_SO-3061.csv`.)
