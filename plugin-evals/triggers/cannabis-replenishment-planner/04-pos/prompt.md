---
name: trigger--cannabis-replenishment-planner--04-pos
description: "should fire cannabis-replenishment-planner"
tags: ["trigger", "cannabis-replenishment-planner", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

We're a brand. Here's sell-through from our 12 dispensary accounts. Can you suggest reorder quantities for each account?
