---
name: trigger--cannabis-replenishment-planner--06-neg
description: "must not fire cannabis-replenishment-planner"
tags: ["trigger", "cannabis-replenishment-planner", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Our Metrc package count doesn't match the vault, can you find the variance?
