---
name: trigger--distru-expiring-inventory--04-pos
description: "should fire distru-expiring-inventory"
tags: ["trigger", "distru-expiring-inventory", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Customize our expiring-inventory dashboard to only show the Oakland location
