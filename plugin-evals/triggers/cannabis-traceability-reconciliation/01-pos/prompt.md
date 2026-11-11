---
name: trigger--cannabis-traceability-reconciliation--01-pos
description: "should fire cannabis-traceability-reconciliation"
tags: ["trigger", "cannabis-traceability-reconciliation", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

metrc says 14 packages but we only found 12 in the vault, help me figure out whats missing
