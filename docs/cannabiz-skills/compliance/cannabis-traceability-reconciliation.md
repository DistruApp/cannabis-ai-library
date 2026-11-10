# Cannabis Traceability Reconciliation

Skill: [`cannabis-traceability-reconciliation`](../../../skills/cannabiz-skills/compliance/cannabis-traceability-reconciliation/SKILL.md)

## What it does

Turns two inventory lists that don't agree into a report an inventory or compliance manager can act on. A bundled script does the math: it matches packages by tag, converts units (pounds, grams, each), and sorts every package into a clear status such as short, over, not counted, counted but not in the system, missing unit, or duplicate rows it can't combine. Possible tag typos are noted next to both packages without hiding either one. The skill then explains the likely cause of each variance, ranks what to fix first, and drafts corrective actions for human sign-off. Proposed adjustments are drafts only and are never submitted to the state system.

## When to use it

- "Our count doesn't match Metrc"
- "Metrc says 14 packages but we only found 12 in the vault"
- Month-end or pre-audit inventory reconciliation
- "We have product in the dry room that isn't showing in Metrc"
- Uploading a traceability export next to a count sheet or ERP on-hand report

## How to use it

- **Inputs:** the traceability package export and the count or ERP export, both as CSV, with the time each one was pulled. Also the state and license type.
- **Tools / connectors:** none. Works from uploaded files and needs an assistant that can run Python for the bundled calculator.
- **Works in:** Claude or any LLM with code execution.
- **Safeguards:** shows the column mapping for confirmation before calculating, never fills a blank unit or drops a duplicate row without saying so, never invents state adjustment reasons or deadlines, and never suggests adjusting just to make the numbers match.

## Example

**Input:** a Metrc export of 10 packages and a September 30 count sheet from a Michigan grower and processor.

**Output:** 12 packages compared, 3 matching. Net weight variance of minus 23.8 g, both short packages bulk flower in storage, so moisture loss is the probable cause and they should be re-weighed. Gummies counted 12 units over the system, flagged high priority. One rosin package noted as a likely typo on the count sheet, kept open until someone reads the physical label. The report includes a jurisdiction block, a variance table, draft actions and a sign-off line.
