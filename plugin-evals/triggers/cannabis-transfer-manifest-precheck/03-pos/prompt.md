---
name: trigger--cannabis-transfer-manifest-precheck--03-pos
description: "should fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

our driver keeps getting transfers rejected at the dispensary, here's today's order and the packages we pulled - what's wrong?
