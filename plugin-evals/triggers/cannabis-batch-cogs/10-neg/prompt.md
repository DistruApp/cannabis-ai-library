---
name: trigger--cannabis-batch-cogs--10-neg
description: "must not fire cannabis-batch-cogs"
tags: ["trigger", "cannabis-batch-cogs", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Which carts should the dispensary reorder this week?
