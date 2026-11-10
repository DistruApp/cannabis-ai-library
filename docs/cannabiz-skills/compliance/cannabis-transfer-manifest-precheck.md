# Cannabis Transfer Manifest Precheck

Skill: [`cannabis-transfer-manifest-precheck`](../../../skills/cannabiz-skills/compliance/cannabis-transfer-manifest-precheck/SKILL.md)

## What it does

Catches shipping mistakes before they leave the building. A bundled script joins the sales order, the draft manifest and the package inventory, then flags packages not on the order, order lines missing from the manifest, quantity or unit mismatches, quantities above what the package holds, packages not in active inventory, duplicate tags and product without a passing lab status. It returns GO or HOLD for each line with the fix needed. Anything it can't check from files, such as whether the receiving license is active or driver and vehicle details, goes on a manual checklist with where to verify it.

## When to use it

- "Check this manifest before the driver leaves"
- "Does this transfer match the order?"
- Catching wrong packages, wrong quantities or untested product before shipping
- Uploading a Metrc or BioTrack transfer draft next to an invoice or sales order

## How to use it

- **Inputs:** the sales order, the draft manifest, and an active package export with lab status, all as CSV. Also the state and license type.
- **Tools / connectors:** none. Works from uploaded files and needs an assistant that can run Python for the bundled checker.
- **Works in:** Claude or any LLM with code execution.
- **Safeguards:** lab status only counts as passed for values the user confirms. GO means the file checks passed, not that the shipment is compliant. It never creates or submits the transfer.

## Example

**Input:** a 9-line sales order, its draft manifest and the morning package export for a Michigan processor shipping to a retailer.

**Output:** HOLD, with 8 of 9 lines needing action. Two packages are not lab passed and must be pulled, one line ships more than the package holds, one order line is missing from the manifest, and one package is not in active inventory. Fixes are grouped by owner, followed by the manual verification list and a sign-off line.
