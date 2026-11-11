---
name: trigger--cannabis-batch-cogs--04-pos
description: "should fire cannabis-batch-cogs"
tags: ["trigger", "cannabis-batch-cogs", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

I need cost per unit for our pre-roll 5-packs so sales can build the wholesale price sheet
