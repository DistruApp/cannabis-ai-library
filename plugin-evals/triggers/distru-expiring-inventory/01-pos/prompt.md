---
name: trigger--distru-expiring-inventory--01-pos
description: "should fire distru-expiring-inventory"
tags: ["trigger", "distru-expiring-inventory", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Which of our products expire in the next 90 days and which customers usually buy them? We use Distru.
