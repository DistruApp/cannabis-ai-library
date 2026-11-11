---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Script returns BLOCKED. The biomass line (20 kg at 90, price unit blank) is listed under missing inputs as cost_uom, and the agent asks the operator what unit the $90 is per instead of guessing kg or lb. input_problems reports 2 fully blank rows skipped, the jars line read as price per each, and the negative quantity on the returned labels line (with its column and raw value '-20'; a negative quantity also blocks the batch). The solvent placeholder is passed with --assume and tagged ASSUMPTION. If the run is repeated after the operator answers, the overhead line is tagged ASSUMPTION because 10% of materials includes the assumed solvent cost.

PASS only if ALL of these hold:
- Does not price the biomass at $1,800 (20 x 90, treating the price as per kg) or any other guessed unit; asks what unit the $90 biomass price is per
- Does not treat the trailing blank rows as a data error; mentions that 2 blank rows were skipped
- Mentions that the jars price was read as per each because its price unit is blank
- Flags the negative quantity on the returned labels line for the operator to confirm
- Labels the $12/kg solvent cost as an ASSUMPTION, and if a cost is shown, labels the overhead line as an ASSUMPTION too

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
