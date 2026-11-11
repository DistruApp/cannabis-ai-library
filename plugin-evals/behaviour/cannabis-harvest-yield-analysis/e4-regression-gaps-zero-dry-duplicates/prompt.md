---
name: cannabis-harvest-yield-analysis--e4-regression-gaps-zero-dry-duplicates
description: "evals.json #4: regression-gaps-zero-dry-duplicates"
tags: ["behaviour", "cannabis-harvest-yield-analysis", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Example Gardens harvest log attached (harvests_regression_gaps.csv). Which room does better per sq ft, and what's our dry-down? EX-R1-0829 is still curing. The one row with no unit was weighed in pounds.

(The attached files are in the `resources` folder: `harvests_regression_gaps.csv`.)
