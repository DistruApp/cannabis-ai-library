---
name: cannabis-batch-cogs--e2-live-resin-missing-solvent-cost
description: "evals.json #2: live-resin-missing-solvent-cost"
tags: ["behaviour", "cannabis-batch-cogs", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

cost out our papaya live resin run. 1180 jars. biomass was 45.36 kg of fresh frozen we pay $95/lb. 30 hrs labor @ $26. we do overhead as 12% of materials. lab $600. don't have the solvent cost handy, just use whatever.

(The attached files are in the `resources` folder: `bom_live_resin_run.csv`.)
