---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs the script and reports ...601 (NaN), ...602 (inf), ...603 (-10 ea), ...604 ('1,5' lb) and ...605 ('1.234,5' g) as INVALID_NUMBER, each with its row, column and raw value from input_problems. None of them is called a shortage or overage, none is guessed (no 1.5 lb, 15 lb, 1234.5 g or 1.2345 g), and none is in the totals. ...606 ('1,234.5' in Metrc vs 1234.5 g counted) is a MATCH because US thousands separators are read normally. ...607 is SHORT_IN_COUNT by 10 g. Net weight variance -10 g on 2 quantity-compared packages (system_total_compared 1434.5 g, -0.697%), with the five INVALID_NUMBER packages listed next to the total. Asks for those five cells to be corrected or recounted and the script rerun. Draft actions and sign-off are included.

PASS only if ALL of these hold:
- Reports ...601 to ...605 as INVALID_NUMBER, not as SHORT_IN_COUNT or OVER_IN_COUNT
- Does not state a guessed value for '1,5' or '1.234,5' (such as 1.5 lb, 15 lb, 1234.5 g or 1.2345 g)
- Reports ...606 as a match (Metrc '1,234.5' read as 1234.5 g)
- Reports ...607 as SHORT_IN_COUNT by 10 g
- States the net weight variance as -10 g on 2 quantity-compared packages and lists the five INVALID_NUMBER packages as left out of the total
- Includes every input_problems entry with its row, column and raw value
- Asks for the invalid cells to be corrected and the script rerun rather than hand-computing their variance

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
