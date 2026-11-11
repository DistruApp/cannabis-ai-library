---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs without --weight-unit (the file has a unit column); summary.json is valid JSON with no NaN or Infinity. input_problems lists, with row, column and raw value: EX-R3-0908 wet weight 'NaN', EX-R3-0915 dry weight 'inf', EX-R4-0902 dry weight '4,25' (ambiguous comma), EX-R4-0909 trim '-150' (negative) and cycle cost '1.234,56' (ambiguous comma), and EX-R4-0916 plant count '-40'. Each is treated as blank and the batch is left out of the figures that need it: total dry 19,800 g on 4 of 6 batches; overall dry-down 78.02% on 3 of 6. Room 4 is 22.25 g/sq ft on 2 of 3 batches and Room 3 is 21.8 g/sq ft on 2 of 3; Room 3 dry-down 78.0% covers only 1 of 3 batches. EX-R3-0901's wet weight '25,000' is read as 25,000 g, and input_problems asks to confirm the file uses the comma as a thousands separator. EX-R4-0909's trim shows blank (INCOMPLETE_BREAKDOWN, 750 g unaccounted) and its cost per gram is blank. The pre-fix script reported total dry weight as Infinity (invalid JSON) and read EX-R4-0902's '4,25' lb as 425 lb.

PASS only if ALL of these hold:
- Reports each unreadable or negative value (NaN, inf, 4,25, -150, 1.234,56, -40) as a data problem with its batch and column, and asks for the right figure
- Does not reinterpret '4,25' as 4.25 or 425 lb for EX-R4-0902
- Reports Room 4 at about 22.3 g/sq ft and Room 3 at about 21.8 g/sq ft, each on 2 of 3 batches
- Reports total dry weight of about 19,800 g on 4 of 6 batches, and overall dry-down of about 78.0% on 3 of 6
- Shows EX-R4-0909's trim as blank or missing, not 0% or -150
- Does not cite outside yield benchmarks

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
