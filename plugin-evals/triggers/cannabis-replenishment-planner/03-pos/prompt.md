---
name: trigger--cannabis-replenishment-planner--03-pos
description: "should fire cannabis-replenishment-planner"
tags: ["trigger", "cannabis-replenishment-planner", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Build me a PO for Friday's vendor orders, budget is $8k, here's sell-through by SKU
