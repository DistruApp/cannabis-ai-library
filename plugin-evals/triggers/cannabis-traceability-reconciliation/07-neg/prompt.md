---
name: trigger--cannabis-traceability-reconciliation--07-neg
description: "must not fire cannabis-traceability-reconciliation"
tags: ["trigger", "cannabis-traceability-reconciliation", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Our cannabis excise tax return doesn't match our sales report, can you reconcile them?
