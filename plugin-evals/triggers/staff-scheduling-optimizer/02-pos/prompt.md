---
name: trigger--staff-scheduling-optimizer--02-pos
description: "should fire staff-scheduling-optimizer"
tags: ["trigger", "staff-scheduling-optimizer", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Are we overstaffed on Tuesdays? Labor is running 28% of sales
