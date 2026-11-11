---
name: trigger--distru-expiring-inventory--02-pos
description: "should fire distru-expiring-inventory"
tags: ["trigger", "distru-expiring-inventory", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

build me a distru dashboard of expiring stock and past buyers so I can push it before it dates out
