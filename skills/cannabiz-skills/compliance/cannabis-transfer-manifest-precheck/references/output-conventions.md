# Output conventions

Shared by every skill in the library. Outputs are written for people running a cannabis business: plain language, no AI jargon, numbers before narrative.

## Label every claim by source

| Label | Meaning | Example |
|---|---|---|
| **[DATA]** | Computed from or read in the operator's files | "Package 1A40…0042 is 3.5 g short in Metrc vs. the count sheet [DATA]" |
| **[RULE]** | From a cited primary source (citation + verified date) | "[RULE: 4 CCR §15xxx, verified 2026-10-16]" |
| **[ASSUMPTION]** | A value the skill had to assume. The operator must confirm it. | "Labor rate $22/hr [ASSUMPTION — confirm]" |
| **NEEDS VERIFICATION** | Rule-dependent item with no verified source | "Waste hold period — NEEDS VERIFICATION with your state's rules" |

Only use the labels where the source isn't obvious; don't clutter every line. Put assumptions in **one list** near the top so they can be corrected in a single pass.

## Standard report shape

1. **Bottom line**: 2–4 sentences on what's wrong or what to do, with the dollar or unit size.
2. **Jurisdiction block** (state-dependent outputs only)
3. **Assumptions to confirm**
4. **Main table(s)**
5. **Actions**: owner · due · priority. Draft adjustments are marked *DRAFT, not submitted*.
6. **Data gaps**: what couldn't be checked and why
7. **Sign-off** (High-risk skills):

```
Prepared by AI-assisted analysis on [date] from files: [list].
Reviewed by: ____________  Role: ____________  Date: ________
Nothing in this report has been submitted to [traceability system] or any regulator.
```

## Never

- Invent a number, rule, test result, license status, or package tag.
- Round a discrepancy away. Report it at the precision of the source data.
- Say "compliant" or "approved". Say "no issues found in the checks performed" and list the checks.
- Present output as legal, tax, or accounting advice.
