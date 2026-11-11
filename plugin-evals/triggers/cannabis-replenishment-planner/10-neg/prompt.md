---
name: trigger--cannabis-replenishment-planner--10-neg
description: "must not fire cannabis-replenishment-planner"
tags: ["trigger", "cannabis-replenishment-planner", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

What's our cost per unit on the last batch of gummies?
