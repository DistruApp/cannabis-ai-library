---
name: trigger--cannabis-sop-generator-trainer--07-neg
description: "must not fire cannabis-sop-generator-trainer"
tags: ["trigger", "cannabis-sop-generator-trainer", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Our Metrc count doesn't match our physical count, find the variances
