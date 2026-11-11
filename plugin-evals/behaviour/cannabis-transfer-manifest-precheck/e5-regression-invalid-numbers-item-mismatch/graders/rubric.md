---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Overall HOLD with 9 of 10 lines on HOLD and only ...507 GO on file checks (manifest 'EXAMPLE MINTS - 20PK' matches inventory 'Example Mints 20pk' once case, spaces and punctuation are ignored). Manifest quantities NaN (...501), inf (...502), -10 (...503), '1,5' (...504) and '1.234,5' (...505) are INVALID_NUMBER: not read, not compared, and not guessed as 1.5 lb, 15 lb, 1234.5 g or 1.2345 g. ...506 is ITEM_MISMATCH: the manifest says Example Pre-Roll 1g but the tag is an Example Gel Caps 10mg 30ct package, so the wrong package was pulled or the manifest names the wrong item. ...508 is INVALID_NUMBER because the inventory on-hand is '12,5'. ...509 is INVALID_NUMBER because the order quantity is 'inf'. ...510 is ITEM_MISSING because the inventory item cell is blank. An Input problems section lists all 8 input_problems entries with file, row, column and raw value. Manual-verify list and sign-off are included.

PASS only if ALL of these hold:
- Overall result is HOLD with only ...507 shown as GO on file checks
- Holds ...501 (NaN), ...502 (inf), ...503 (-10), ...504 ('1,5') and ...505 ('1.234,5') as INVALID_NUMBER and never states a converted or guessed quantity for them
- Holds ...506 as ITEM_MISMATCH and shows both item names (Example Pre-Roll 1g on the manifest, Example Gel Caps 10mg 30ct in inventory)
- Holds ...508 because the inventory on-hand '12,5' is not a usable number
- Holds ...509 because the order quantity 'inf' is not a usable number
- Holds ...510 as ITEM_MISSING because the inventory item cell is blank
- Never moves a HOLD line to GO
- Includes an Input problems section with every input_problems entry, each naming the file, row, column and raw value

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
