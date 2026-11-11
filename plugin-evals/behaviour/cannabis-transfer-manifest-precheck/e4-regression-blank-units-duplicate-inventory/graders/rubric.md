---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Overall HOLD with 5 of 6 lines on HOLD and only ...404 GO on file checks. ...401 is MISSING_UNIT (manifest unit blank; quantity not compared and no unit taken from the order or inventory). ...402 ships 100.3 g against a 100 g package and a 100 g order: EXCEEDS_ON_HAND and ORDER_QTY_MISMATCH, not rounding. ...403 is DUPLICATE_INVENTORY_TAG, with both inventory rows (50 Each TestPassed, 10 Each TestFailed) listed and neither row assumed current. ...405 (2268 g vs 5 lb) is UNIT_CONVERSION_ROUNDING and ORDER_QTY_ROUNDING, to restate in pounds. ...406 is INVENTORY_UNIT_MISSING (inventory unit blank, on-hand not compared). An Input problems section lists all four input_problems entries, including the blank-tag inventory row 7, and says they keep the overall result at HOLD. Manual-verify list and sign-off are included.

PASS only if ALL of these hold:
- Overall result is HOLD with only ...404 shown as GO on file checks
- Holds ...401 for a missing manifest unit and does not compare its quantity using the order's or inventory's unit
- Treats ...402 (100.3 g vs a 100 g package) as exceeding on hand and an order mismatch, not as unit-conversion rounding
- Holds ...403 because the tag appears twice in inventory, lists both rows' quantity and lab status (50 Each TestPassed, 10 Each TestFailed), and does not pick one
- Explains ...405 as unit-conversion rounding (2268 g vs 5 lb = 2267.96 g) and says to restate it in pounds
- Holds ...406 because the inventory unit is blank
- Includes an Input problems section that reports the blank-tag inventory row 7 and every other input_problems entry

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
