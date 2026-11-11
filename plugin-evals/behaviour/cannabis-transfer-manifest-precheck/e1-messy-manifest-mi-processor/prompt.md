---
name: cannabis-transfer-manifest-precheck--e1-messy-manifest-mi-processor
description: "evals.json #1: messy-manifest-mi-processor"
tags: ["behaviour", "cannabis-transfer-manifest-precheck", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Driver leaves at 2pm. Attached: sales order SO-1042, our draft manifest, and this morning's Metrc active packages. We're a Michigan processor shipping to a provisioning center. Anything we need to fix?

(The attached files are in the `resources` folder: `sales_order_SO-1042.csv`, `draft_manifest_SO-1042.csv`, `inventory_active_packages.csv`.)
