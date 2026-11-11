---
name: cannabis-replenishment-planner--e1-dispensary-weekly-reorder
description: "evals.json #1: dispensary-weekly-reorder"
tags: ["behaviour", "cannabis-replenishment-planner", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Here's our POS sales for Aug-Sep and today's on-hand (9/30). Lead times and case packs are in the on-hand sheet. Keep 3 days of safety stock. What should I order this week and how much cash do I need?

(The attached files are in the `resources` folder: `pos_sales_2026-08-02_to_2026-09-30.csv`, `onhand_2026-09-30.csv`.)
