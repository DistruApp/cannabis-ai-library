---
name: cannabis-traceability-reconciliation--e4-regression-duplicates-blank-units-rounding
description: "evals.json #4: regression-duplicates-blank-units-rounding"
tags: ["behaviour", "cannabis-traceability-reconciliation", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Can you reconcile our Metrc export against this count sheet? Both pulled 10/31 at 5pm. We're a Michigan grower. Some people double-entered rows on the count sheet and a couple of unit cells are empty.

(The attached files are in the `resources` folder: `regression_metrc_packages.csv`, `regression_count_sheet.csv`.)
