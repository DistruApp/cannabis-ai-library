---
name: trigger--distru-expiring-inventory--03-pos
description: "should fire distru-expiring-inventory"
tags: ["trigger", "distru-expiring-inventory", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

I need to move dated inventory fast. Pull the lots expiring by March from Distru and show who ordered them last year.
