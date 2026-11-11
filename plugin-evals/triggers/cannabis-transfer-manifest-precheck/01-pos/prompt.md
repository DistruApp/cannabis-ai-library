---
name: trigger--cannabis-transfer-manifest-precheck--01-pos
description: "should fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

can you check this manifest against SO-1042 before the van leaves
