# Column mappings for common exports

Operators upload exports from traceability systems, ERPs, and POS systems. Column names vary by system, version, state, and the user's column settings, so **always show the detected mapping and get a one-line confirmation before computing anything.**

> **Verification status (2026-10-16):** The aliases below are *matching hints*, not verified schemas. None has been checked against a live export from each system. If a required field isn't found, ask which column holds it. Never guess between two candidate columns.

## Canonical fields and aliases

| Canonical field | Meaning | Common aliases (case/space-insensitive) |
|---|---|---|
| `package_id` | Traceability package tag/label | Tag, Package Tag, Label, Package Label, Package ID, Package #, Metrc Tag, Barcode, Global ID, BioTrack ID, Inventory ID |
| `item` | Product/item name | Item, Item Name, Product, Product Name, SKU Name |
| `sku` | Internal SKU | SKU, Product Code, Item Code |
| `category` | Item category | Category, Item Category, Product Category, Type |
| `quantity` | On-hand quantity | Quantity, Qty, On Hand, Available, Current Quantity, Remaining Quantity |
| `uom` | Unit of measure | UoM, Unit, Unit of Measure, UnitOfMeasureName, Units |
| `batch` | Batch/lot/harvest | Batch, Batch #, Lot, Lot Number, Harvest, Harvest Name, Production Batch |
| `location` | Room/location | Location, Room, Area, Bin |
| `lab_status` | Testing state | Lab Status, Testing Status, LabTestingState, Test Status |
| `packaged_date` | Package date | Packaged Date, Package Date, Created |
| `unit_cost` | Cost per unit | Unit Cost, Cost, Cost per Unit, COGS/unit |

## Known source systems

| System type | Examples | Notes |
|---|---|---|
| State traceability | Metrc, BioTrack, state-built systems | Package tags are the join key. Metrc's API has an endpoint listing **state-specific adjustment reasons** (`GET /packages/v2/adjust/reasons`, seen in the Metrc API index 2026-10-16). Ask the operator to export that list rather than assuming reasons. |
| ERP / inventory | Distru and other cannabis ERPs | Usually carries the package tag plus SKU and cost. Unit naming may differ from traceability. |
| Retail POS | Dutchie, Flowhub, Treez, and others | Sales exports are usually by SKU/product, sometimes by package. Check which before computing sell-through by package. |

## Unit normalization

Before comparing quantities, normalize units: g ↔ kg ↔ lb ↔ oz (1 lb = 453.592 g, 1 oz = 28.3495 g), and keep **each** (count-based) items separate from weight-based ones. A count in "each" can't be compared to a weight without a per-unit net weight from the operator. Flag those rows and don't convert them.
