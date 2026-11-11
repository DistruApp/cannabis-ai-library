---
name: trigger--distru-expiring-inventory--06-neg
description: "must not fire distru-expiring-inventory"
tags: ["trigger", "distru-expiring-inventory", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Reconcile our Metrc packages against the physical count
