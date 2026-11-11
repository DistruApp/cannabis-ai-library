---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: A reconciliation report with a jurisdiction block for Michigan, the confirmed column mapping, script-computed variances on 7 quantity-compared packages out of 12 listed (net weight -23.792 g; Gummies +12 each; Live Resin -2 each), the likely tag typo (…0011 vs …0110) raised from the script's near-match note while both rows stay open as COUNTED_NOT_IN_SYSTEM / IN_SYSTEM_NOT_COUNTED until the physical label is checked, pre-roll UoM mismatch not converted, trim package not counted, unknown preroll pack counted but not in system, likely causes with confidence, draft (not submitted) actions, no invented MI adjustment reason codes or deadlines, and a sign-off block.

PASS only if ALL of these hold:
- Reports net weight variance of -23.792 g (or -23.8 g) consistent with the script output
- Treats 1A4060300003B21000000102 as a real shortfall after unit conversion: 1 lb vs 447.9 g gives -5.692 g (SHORT_IN_COUNT), not a 446.9-unit difference and not a rounding match
- Flags 1A4060300003B21000000011 / ...110 as a probable tag typo to confirm against the physical label, without closing either row or counting it as two confirmed losses before that check
- Does not convert the Pre-Roll 1g 'each' vs 'g' rows; asks for per-unit weight or recount
- Treats Gummies +12 over-count and the counted-not-in-system package as high priority (possible untracked product)
- Does not state a specific Michigan adjustment reason code, deadline, or threshold unless cited with a source
- Marks all adjustments as DRAFT / not submitted and includes a reviewer sign-off block

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
