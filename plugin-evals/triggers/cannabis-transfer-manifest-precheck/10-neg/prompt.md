---
name: trigger--cannabis-transfer-manifest-precheck--10-neg
description: "must not fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Review this COA and tell me if the potency matches our label claim
