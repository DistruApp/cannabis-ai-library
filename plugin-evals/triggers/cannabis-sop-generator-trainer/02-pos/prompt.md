---
name: trigger--cannabis-sop-generator-trainer--02-pos
description: "should fire cannabis-sop-generator-trainer"
tags: ["trigger", "cannabis-sop-generator-trainer", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

turn these notes into a proper SOP for our extraction room cleaning
