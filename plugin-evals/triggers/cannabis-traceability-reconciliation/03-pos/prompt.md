---
name: trigger--cannabis-traceability-reconciliation--03-pos
description: "should fire cannabis-traceability-reconciliation"
tags: ["trigger", "cannabis-traceability-reconciliation", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

our distru on-hand and metrc dont agree on the gelato carts, one says each one says grams
