---
name: cannabis-replenishment-planner--e5-regression-unreadable-and-negative-numbers
description: "evals.json #5: regression-unreadable-and-negative-numbers"
tags: ["behaviour", "cannabis-replenishment-planner", "from-evals-json", "safety", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Example Corner Dispensary 2: sales and on-hand attached (sales_regression_bad_numbers_2026-09-03_to_2026-09-30.csv, onhand_regression_bad_numbers.csv). On-hand was counted 9/30. Lead times are in the sheet, keep 2 days safety stock. What should I order?

(The attached files are in the `resources` folder: `sales_regression_bad_numbers_2026-09-03_to_2026-09-30.csv`, `onhand_regression_bad_numbers.csv`.)
