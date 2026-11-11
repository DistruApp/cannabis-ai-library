---
name: trigger--cannabis-transfer-manifest-precheck--02-pos
description: "should fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Attached is the Metrc transfer draft and the invoice for Example Harbor Wellness. Make sure we're not shipping anything untested.
