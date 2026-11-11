---
name: trigger--cannabis-transfer-manifest-precheck--04-pos
description: "should fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

double check the packages on this outgoing delivery match what the store ordered
