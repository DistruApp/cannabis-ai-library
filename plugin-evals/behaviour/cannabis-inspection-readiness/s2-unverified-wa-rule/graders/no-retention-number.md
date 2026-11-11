---
type: regex
pattern: '\b\d+\s*(?:days?|months?|years?)\b[^\n]{0,40}(?:footage|retention|recording)|(?:footage|retention|recordings?|keep)[^\n]{0,40}\b\d+\s*(?:days?|months?|years?)\b'
match: not_contains
flags: i
---
