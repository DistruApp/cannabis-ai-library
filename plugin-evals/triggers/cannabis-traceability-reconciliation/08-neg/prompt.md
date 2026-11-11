---
name: trigger--cannabis-traceability-reconciliation--08-neg
description: "must not fire cannabis-traceability-reconciliation"
tags: ["trigger", "cannabis-traceability-reconciliation", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Calculate yield per light for our last three harvests
