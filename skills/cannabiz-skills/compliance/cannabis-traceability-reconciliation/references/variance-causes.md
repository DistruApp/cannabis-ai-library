# Variance causes: what to check for each status

Use this to assign a **likely cause** and the **one check that would confirm it**. These are operational patterns, not legal rules. Whether and how to correct something in the traceability system is state-specific (see the jurisdiction gate).

| Status | Likely causes (most → least common) | Confirming check | Typical next step |
|---|---|---|---|
| `SHORT_IN_COUNT` (weight) | Moisture loss on stored bulk flower; scale not tared or calibrated; sales/samples not yet reported to traceability; product sampled for QA/lab not recorded; partial repackaging into new tags; theft or diversion | Re-weigh on a calibrated scale; check the POS → traceability sales sync for the period; check lab sample and QA records; look for new packages of the same item | Re-weigh. If the loss is confirmed and explained, draft an adjustment with documentation. If unexplained, escalate to the compliance lead. |
| `SHORT_IN_COUNT` (each) | Unreported sales or samples; damaged units pulled and not recorded as waste; miscount | Recount; check the POS for the period; check the waste log | Recount before anything else |
| `OVER_IN_COUNT` | Prior adjustment overshot; product from another package mixed in; units returned from a retailer not received in the system; miscount | Check adjustment history for this tag; check returns/rejected transfers | **High priority.** Possible untracked product. Don't sell or move it until it's resolved. |
| `IN_SYSTEM_NOT_COUNTED` | Not counted (wrong room/missed shelf); in transit on a transfer; sold or destroyed but not recorded; package depleted but not finished in the system | Physical search by tag; check outgoing transfers and the waste log; check whether quantity should be 0 | Search, then reconcile records. Don't adjust until the physical search is done. |
| `COUNTED_NOT_IN_SYSTEM` | New package created physically but not in the system; incoming transfer not yet received; package was finished/closed in error; tag from another license location | Check pending incoming transfers; check inactive/finished packages for this tag; check repackaging records | **High priority.** Possible untracked product. Place it on hold until resolved. |
| Near-match note on a not-counted / not-in-system pair | Count sheet mistyped (transposed or dropped digits), or two real packages with sequential tags | Read the physical tag | If it's a typo, fix the count sheet and rerun. Until confirmed, both rows stay open with their own status. |
| `UOM_MISMATCH` | Item tracked by count in one system and by weight in the other | Get net weight per unit from the item master or label | Recount in the system's unit, or convert with the operator's confirmed net weight. |
| `UNKNOWN_UOM` | Unusual unit label in the export | Ask the operator what the unit means | Map it and rerun. |
| `MISSING_UNIT` | Unit cell left blank, or the file has no unit column | Look at the source row; ask the operator what unit that file uses | Fill in the unit and rerun, or rerun with `--default-count-unit` / `--default-system-unit` if the operator states it. |
| `DUPLICATE_CONFLICT` | The same tag on two or more rows with a blank quantity or units that can't be converted | Look at each listed row; check whether the tag was entered twice or two packages share a mistyped tag | Fix the file so each tag appears once with one quantity and unit, then rerun. |
| `BAD_QUANTITY` | Blank quantity cell | Look at the source row | Fix the input, rerun. |
| `INVALID_NUMBER` | Quantity cell holds text, NaN or inf, a negative number, or a decimal comma ("1,5", "1.234,5"), often from a spreadsheet set to a European number format | Look at the raw value in `input_problems` and ask what was meant | Correct the cell and rerun. Never guess the value. |

## Pattern checks (run before row-by-row)

- **Same counter / same room / same shift** behind most variances → count-process problem, not inventory loss.
- **All shortfalls on bulk flower, proportional to package weight** → moisture-loss pattern. Ask for weigh history.
- **All shortfalls on finished goods at a retail or distribution location** → sales or transfer reporting lag. Compare as-of times.
- **Over and short rows on the same item with offsetting quantities** → product placed in the wrong package or bin.
- **Variance concentrated on one date's packages** → a repackaging or production event that wasn't fully recorded.

## Escalate immediately (tell the user plainly)

- Any unexplained shortfall that's large relative to the package, or any recurring unexplained shortfall
- Any product on site that isn't in the system (`OVER_IN_COUNT` / `COUNTED_NOT_IN_SYSTEM`) that stays unexplained after the checks above
- Any sign of altered records

Whether and when a state requires notifying the regulator about loss or theft is state-specific → **NEEDS VERIFICATION** unless cited in `state-profiles.md`.
