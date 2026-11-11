---
name: trigger--cannabis-harvest-yield-analysis--07-neg
description: "must not fire cannabis-harvest-yield-analysis"
tags: ["trigger", "cannabis-harvest-yield-analysis", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

What's the extraction yield and cost per gram on our last live resin run?
