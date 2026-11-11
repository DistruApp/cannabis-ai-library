---
name: trigger--cannabis-inspection-readiness--08-neg
description: "must not fire cannabis-inspection-readiness"
tags: ["trigger", "cannabis-inspection-readiness", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

We received a notice of violation for camera downtime, draft our response to the regulator
