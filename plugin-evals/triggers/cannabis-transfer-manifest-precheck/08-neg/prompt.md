---
name: trigger--cannabis-transfer-manifest-precheck--08-neg
description: "must not fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

Our physical count doesn't match Metrc for the vault, find the variances
