---
name: trigger--cannabis-harvest-yield-analysis--07-pos
description: "should fire cannabis-harvest-yield-analysis"
tags: ["trigger", "cannabis-harvest-yield-analysis", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Which strain is doing better for us, Blue Dream or GMO Cookies? Our harvest log is in this folder.
