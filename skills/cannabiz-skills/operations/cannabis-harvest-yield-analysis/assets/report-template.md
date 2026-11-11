# Harvest Yield Report — [Facility] — [period]

## Bottom line
[2–4 sentences: total dry output, best/worst room or strain per sq ft (vs. operator target if given), largest unaccounted weight, cost per gram if available.]

## Sources and assumptions
| File | Rows | Mapping confirmed | Units |
|---|---|---|---|
- Period: [period the user named]; harvest dates in the file: [first]–[last]; batches outside the named period: [list, and whether the operator said to include them | none]
- Dry weight definition: [bucked/trimmed dry | total dry plant material] [DATA or ASSUMPTION]
- Cost basis: [operator-provided cycle cost | cost/sq ft × canopy | none]
- Targets used: [operator's own targets | none, compared against this file's batches only]

## Results by batch
| Batch | Strain | Room | Date | Dry (g) | Dry-down % | g/plant | g/sq ft | g/light | A % | B % | Trim % | Unaccounted (g) | $/dry g | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Rankings (dry g per sq ft, or the script's `ranking_metric` if canopy is missing)
| Room / Strain | Batches | Dry (g) | g/sq ft | g/plant | Dry-down % | Coverage |
|---|---|---|---|---|---|---|
Note: [strain/room confound, small-sample caveats. Quote the script's coverage line whenever a figure covers fewer than all batches, e.g. "3 of 4 batches; 1 excluded: no dry weight". Say "still curing" only if the operator or their records say so.]

## Flags worth a look
Rule used: outside 1.5 × IQR of this file's own batches (n = __).
| Batch | Flag | Possible explanations to check |
|---|---|---|

## Unaccounted weight (records to find before closing harvests)
| Batch | Unaccounted (g) | Check |
|---|---|---|

## Actions
| Action | Owner | Due | Priority |
|---|---|---|---|

## Data gaps
- [Every `input_problems` line: batches excluded from a metric and why, blank unit cells filled from --weight-unit, duplicate harvest IDs, strain or room names written more than one way, blank breakdown parts, zero weights or counts]
- ...

---
Prepared by AI-assisted analysis on [date] from files: [list]. Harvest weights should also tie to traceability harvest records (state requirements: NEEDS VERIFICATION).
