# Flag guide

Each flag puts its line on HOLD. Fixes are operational. Whether a fix also needs a correction in the traceability system, or a regulator notice, is state-specific → NEEDS VERIFICATION unless cited in `state-profiles.md`.

| Flag | What it means | Usual cause | Fix | Owner |
|---|---|---|---|---|
| `NOT_ON_ORDER` | Package is on the manifest but its tag/SKU/item isn't on the order | Wrong package pulled; substitution not entered on the order | Remove it, or amend the order if the buyer agreed to the substitution | Shipping / Sales |
| `ON_ORDER_NOT_ON_MANIFEST` | Ordered but not being shipped | Missed line; out of stock; intentional short-ship | Add it, or confirm the short-ship with the buyer and amend the invoice | Shipping / Sales |
| `ORDER_QTY_MISMATCH` | Manifest total for the line ≠ order quantity | Partial pick, over-pick, typo | Correct the manifest, or amend the order if intentional | Shipping / Sales |
| `ORDER_QTY_ROUNDING` | Difference < 0.5 g, only from unit conversion | Order in lb, manifest in rounded g (or reverse) | State both in the same unit as the package | Sales / Shipping |
| `ORDER_VS_MANIFEST_UOM_MISMATCH` | One side by weight, the other by count | Order written in units, package tracked by weight | Confirm the net weight per unit and restate one side | Sales |
| `NOT_IN_ACTIVE_INVENTORY` | Tag not found in the active package export | Typo; package finished, on hold, or at another location; export is stale | Read the physical tag; re-export inventory; check inactive/on-hold packages | Shipping / Compliance |
| `EXCEEDS_ON_HAND` | Manifest quantity > package quantity | Wrong package; the package was already partially shipped or sampled | Fix the quantity or split across packages. Never ship more than the package holds in the system | Shipping |
| `UNIT_CONVERSION_ROUNDING` | Manifest exceeds the package by < 0.5 g, only because of conversion | 5 lb written as 2268 g (true: 2267.96 g) | Restate the quantity in the package's own unit | Shipping |
| `MANIFEST_VS_INVENTORY_UOM_MISMATCH` | Manifest unit and package unit are different kinds | Count vs. weight | Use the package's unit of measure | Shipping |
| `LAB_NOT_PASSED` | Lab status isn't one of the confirmed passing values | Failed, pending, retest, or not submitted | Pull the package. Don't ship until status is confirmed passed | Compliance / QA |
| `LAB_STATUS_UNCONFIRMED` | Operator didn't confirm which values mean passed | Missing confirmation | Confirm the passing values and rerun | Compliance |
| `NO_LAB_STATUS_COLUMN` | Inventory export has no testing status | Wrong export or columns hidden | Re-export with testing status included | Compliance |
| `DUPLICATE_TAG_ON_MANIFEST` | Same tag appears on more than one line | Copy-paste | Merge into one line | Shipping |
| `BAD_QUANTITY` / `BLANK_TAG` / `INVENTORY_QTY_UNREADABLE` / `ORDER_QTY_UNREADABLE` | Input data problem | Blank or text cell | Fix the file and rerun | Whoever owns the file |

## Grouping tips

- `NOT_ON_ORDER` + `ON_ORDER_NOT_ON_MANIFEST` on similar item names → one wrong package was pulled. Treat it as a single fix.
- Several `LAB_NOT_PASSED` lines from the same batch → a batch-level test issue. Tell QA once, not per line.
- `EXCEEDS_ON_HAND` on a package that also shipped on another open manifest today → over-allocation across orders. Ask for other open manifests.
