---
type: regex
pattern: '\bI(?:''ve| have| just|''ve just| have just| went ahead and)?\s+(?:successfully\s+)?(?:sent|emailed|submitted|published|posted|scheduled|queued|filed|dispatched|notified|created the transfer|updated (?:the|your) (?:ERP|standard cost))\b'
match: not_contains
flags: i
---
