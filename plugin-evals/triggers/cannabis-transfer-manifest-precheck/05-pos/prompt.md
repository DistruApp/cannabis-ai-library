---
name: trigger--cannabis-transfer-manifest-precheck--05-pos
description: "should fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

we're shipping 5 lb of bulk flower to a processor, is the quantity on this transfer right? file attached
