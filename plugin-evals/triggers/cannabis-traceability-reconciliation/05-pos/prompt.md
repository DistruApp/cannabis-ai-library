---
name: trigger--cannabis-traceability-reconciliation--05-pos
description: "should fire cannabis-traceability-reconciliation"
tags: ["trigger", "cannabis-traceability-reconciliation", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

we have extra product in the dry room that isn't showing in metrc, what do we do
