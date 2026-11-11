---
name: trigger--cannabis-replenishment-planner--09-neg
description: "must not fire cannabis-replenishment-planner"
tags: ["trigger", "cannabis-replenishment-planner", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Email our vendors the purchase orders we approved yesterday
