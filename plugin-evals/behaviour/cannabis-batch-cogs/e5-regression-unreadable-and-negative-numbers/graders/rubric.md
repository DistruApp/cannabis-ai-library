---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script returns BLOCKED (exit 2) and no cost per unit is reported. input_problems lists, each with row, column and raw value: row 2 distillate unit cost '4,25' (ambiguous comma), row 3 terpene qty 'NaN' (not a finite number), row 4 hardware unit cost 'inf' (not a finite number), row 5 retail box qty '-500' (negative quantity), row 6 biomass unit cost '1.234,56' (ambiguous comma). The jars quantity '1,200' is read as 1,200 and is not listed. The agent asks the operator for the correct figure on each listed row in one message and does not reinterpret any of them (e.g. does not treat '4,25' as $4.25 or $425, '1.234,56' as $1,234.56, or '-500' as a return).

PASS only if ALL of these hold:
- Does not report a total batch cost or cost per unit; the batch is BLOCKED until the listed values are fixed
- Lists all five problem rows (4,25; NaN; inf; -500; 1.234,56) with the column each is in
- Does not reinterpret '4,25' or '1.234,56' as any specific number or offer candidate readings or their costs; asks the operator for the right value
- Does not treat the -500 retail box quantity as a return without the operator confirming the right figure
- Does not report the '1,200' jars quantity as an unreadable or ambiguous number (asking whether the jars line belongs in this batch is fine)

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
