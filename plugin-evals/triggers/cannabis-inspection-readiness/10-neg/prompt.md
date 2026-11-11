---
name: trigger--cannabis-inspection-readiness--10-neg
description: "must not fire cannabis-inspection-readiness"
tags: ["trigger", "cannabis-inspection-readiness", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Check this label against Michigan packaging rules
