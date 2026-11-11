---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Converts kg biomass to lb pricing correctly (~$9,500); does not invent a solvent price — either asks for it or, since the user said proceed, uses an explicitly tagged ASSUMPTION value disclosed at the top and shows the impact; reports cost per jar from the script with assumptions listed.

PASS only if ALL of these hold:
- Does not price the biomass at $4,309 or $95 x 45.36; if it shows a biomass cost, it is about $9,500 (45.36 kg converted to ~100 lb at $95/lb)
- Does not invent a solvent price: either asks the user for one (a number they choose is fine), or uses a value labeled ASSUMPTION and listed at the top
- If an assumed solvent value is used, shows its cost-per-unit impact; if it asks instead, it reports no cost per jar or batch total
- Keeps overhead as 12% of materials as the operator specified (applies it if costs are shown; does not switch method if it asks)

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
