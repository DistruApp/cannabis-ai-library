---
name: trigger--cannabis-harvest-yield-analysis--04-pos
description: "should fire cannabis-harvest-yield-analysis"
tags: ["trigger", "cannabis-harvest-yield-analysis", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Build me a harvest report for the owners from this Metrc harvest batch export
