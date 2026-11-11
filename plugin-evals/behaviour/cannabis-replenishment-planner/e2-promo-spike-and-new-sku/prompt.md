---
name: cannabis-replenishment-planner--e2-promo-spike-and-new-sku
description: "evals.json #2: promo-spike-and-new-sku"
tags: ["behaviour", "cannabis-replenishment-planner", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

we ran a labor day sale 9/1 on GMO Cookies, pull 35 days of sales so that's included. also the Runtz smalls just launched. same files, on-hand counted 9/30. 7 day lead time if missing, no safety stock.

(The attached files are in the `resources` folder: `pos_sales_2026-08-02_to_2026-09-30.csv`, `onhand_2026-09-30.csv`.)
