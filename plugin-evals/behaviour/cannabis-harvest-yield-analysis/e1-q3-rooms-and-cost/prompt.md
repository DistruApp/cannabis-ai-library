---
name: cannabis-harvest-yield-analysis--e1-q3-rooms-and-cost
description: "evals.json #1: q3-rooms-and-cost"
tags: ["behaviour", "cannabis-harvest-yield-analysis", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

Q3 harvests attached (harvests_2026_q3.csv). Which rooms are pulling their weight and what's our cost per gram? Our internal goal is 25 g/sq ft dry. Note one batch was logged in pounds.

(The attached files are in the `resources` folder: `harvests_2026_q3.csv`.)
