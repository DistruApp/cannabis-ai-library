---
name: trigger--cannabis-harvest-yield-analysis--06-pos
description: "should fire cannabis-harvest-yield-analysis"
tags: ["trigger", "cannabis-harvest-yield-analysis", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Before we close out these harvests, check the weights in this log for anything that doesn't add up
