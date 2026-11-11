---
name: cannabis-traceability-reconciliation--e1-clean-mi-month-end
description: "evals.json #1: clean-mi-month-end"
tags: ["behaviour", "cannabis-traceability-reconciliation", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Month-end. Attached is our Metrc active packages export (pulled 9/30 6pm) and the physical count our team did 9/30 after close. We're a Michigan grower + processor. Why don't these match and what do we need to do?

(The attached files are in the `resources` folder: `metrc_active_packages.csv`, `physical_count_2026-09-30.csv`.)
