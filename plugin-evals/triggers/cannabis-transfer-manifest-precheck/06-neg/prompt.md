---
name: trigger--cannabis-transfer-manifest-precheck--06-neg
description: "must not fire cannabis-transfer-manifest-precheck"
tags: ["trigger", "cannabis-transfer-manifest-precheck", "trigger-neg"]
plugins: ["../../../.."]
runs: 1
max_turns: 5
timeout_seconds: 180
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
---

We just received a transfer from our supplier and the quantities look off, help me decide whether to accept it
