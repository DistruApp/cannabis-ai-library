---
name: cannabis-traceability-reconciliation--e2-erp-vs-metrc-colorado-messy
description: "evals.json #2: erp-vs-metrc-colorado-messy"
tags: ["behaviour", "cannabis-traceability-reconciliation", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

can u compare our ERP on hand vs metrc? colorado medical + rec cultivation. erp export attached + metrc export. some counts are blank because we didnt get to that room

(The attached files are in the `resources` folder: `metrc_active_packages.csv`, `erp_onhand_export.csv`.)
