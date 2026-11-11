---
name: trigger--distru-expiring-inventory--05-pos
description: "should fire distru-expiring-inventory"
tags: ["trigger", "distru-expiring-inventory", "trigger-pos"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Draft promo emails to past buyers of the gummies that expire next month, from our Distru data
