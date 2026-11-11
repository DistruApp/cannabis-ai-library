---
name: cannabis-batch-cogs--e4-regression-blank-cost-unit-and-blank-rows
description: "evals.json #4: regression-blank-cost-unit-and-blank-rows"
tags: ["behaviour", "cannabis-batch-cogs", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Cost out Example Extracts batch EX-LR-01 from the attached BOM. 800 jars. 20 labor hours at $25. Overhead is 10% of materials. Lab was $400. We don't have the solvent price yet, use $12/kg as a placeholder.

(The attached files are in the `resources` folder: `bom_regression_cost_units.csv`.)
