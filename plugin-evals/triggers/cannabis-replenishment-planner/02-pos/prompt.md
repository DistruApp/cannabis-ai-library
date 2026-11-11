---
name: trigger--cannabis-replenishment-planner--02-pos
description: "should fire cannabis-replenishment-planner"
tags: ["trigger", "cannabis-replenishment-planner", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Which of our vape SKUs are about to stock out and which are just sitting? Attached POS sales + inventory.
