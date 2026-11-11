---
name: trigger--cannabis-harvest-yield-analysis--05-pos
description: "should fire cannabis-harvest-yield-analysis"
tags: ["trigger", "cannabis-harvest-yield-analysis", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

our trim percentage keeps climbing, can you look at the last 10 harvests
