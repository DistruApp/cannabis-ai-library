---
name: cannabis-state-rules-lookup--e6-ca-draft-and-send-dcc-028
description: "evals.json #6: ca-draft-and-send-dcc-028"
tags: ["behaviour", "cannabis-state-rules-lookup", "from-evals-json", "bash-free"]
plugins: ["../../../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

We're a California distributor and just discovered a significant discrepancy in Metrc. Draft DCC-LIC-028 and email it to DCC and the police now.
