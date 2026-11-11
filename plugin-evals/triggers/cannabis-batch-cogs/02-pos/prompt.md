---
name: trigger--cannabis-batch-cogs--02-pos
description: "should fire cannabis-batch-cogs"
tags: ["trigger", "cannabis-batch-cogs", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Our gummy batch unit cost jumped from $2.10 to $2.65, can you figure out why? Both BOMs attached
