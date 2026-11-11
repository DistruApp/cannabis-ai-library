---
name: cannabis-transfer-manifest-precheck--e4-regression-blank-units-duplicate-inventory
description: "evals.json #4: regression-blank-units-duplicate-inventory"
tags: ["behaviour", "cannabis-transfer-manifest-precheck", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Truck leaves at 3. SO-2051, the draft manifest and today's Metrc active packages are attached. TestPassed is our only passing status. Michigan processor shipping to a provisioning center. Some cells in these exports are blank, sorry.

(The attached files are in the `resources` folder: `regression_sales_order_SO-2051.csv`, `regression_draft_manifest_SO-2051.csv`, `regression_inventory_active_packages.csv`.)
