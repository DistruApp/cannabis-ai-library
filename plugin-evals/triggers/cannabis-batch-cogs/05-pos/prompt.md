---
name: trigger--cannabis-batch-cogs--05-pos
description: "should fire cannabis-batch-cogs"
tags: ["trigger", "cannabis-batch-cogs", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

If distillate goes up 15% what happens to our vape margins? Use last week's batch costs
