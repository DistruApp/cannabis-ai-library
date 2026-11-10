# Inventory outreach workflow

## Data contract

Join by stable product, lot, customer, order, line and contact IDs. Keep source
IDs behind every aggregate. Use names for display and only verified source URLs.

### Inventory and value

- Resolve tracking method. Read packages for package-tracked stock, batches
  for batch-tracked stock and products for units/price/availability. Do not
  count a package and its related batch twice.
- Convert expiry timestamps to company-local calendar dates. The default is
  today through six calendar months ahead inclusive, with month-end clamping;
  it is not a fixed 180-day expiry window. Partial months can create seven
  calendar labels. Show the actual bounds.
- Use positive active quantities of eligible stock states. Package
  `quantityActive` and batch `quantity` are the inspected fields; verify current
  semantics. Do not substitute raw quantity, or subtract assembling twice.
- Sum only lots inside the selected window/month/location. Preserve full
  precision and format quantities for display. Never sum incompatible units.
- Value each included quantity at the current list price (wholesale price,
  or unit price where none is set) only when
  product/lot price units and currency are compatible or verified conversions
  exist. Missing/unverified price stays unvalued; recorded zero stays zero.
  Show coverage. Do not use inventory cost fields for this price-based metric.
- Label price-based value before discounts and tax. It is not margin, cost,
  historical sales value, expected recovery or a guarantee of selling at that
  price. If cost is separately requested, calculate and label it separately.
- Keep full-product active quantity/value distinct from filtered expiring
  quantity/value. Later-expiring lots must not move into an earlier month.
  Across location rows, avoid duplicating a full-product total in aggregates.
- Product `quantityAvailable` reflects product-level reservations; it does not
  allocate available units to expiring lots. Do not deduct reservations again
  from active quantities. Display relevant testing/hold/other eligibility
  status; do not call an active lot ready for sale without supporting evidence.
- Keep expired, held and missing-date stock distinct. Product-tracked stock
  without usable lot expiry remains unclassified, not implicitly safe.
- Page relevant searches completely using the documented stable sort, currently
  `INSERTED_AT ASC`. Preserve filters across cursors and distinguish partial
  scope from a complete result. Do not label a bounded sample all inventory.

### Previous buyers

- Query line history for selected product IDs with fixed date bounds and
  `DELIVERED`/`COMPLETED` statuses. Label the period as order-date based.
  Resolve current argument names from schemas.
- For paid-buyer analysis, exclude samples/trade samples and require positive
  paid line value/net quantity according to verified semantics. If status or
  price is unavailable, keep the limitation explicit rather than inventing it.
- Refilter returned lines by selected product IDs: a product filter may return
  other products on containing orders. Do not include those in buyer totals.
- The inspected LINE_ITEM report quantity is already net of returnedQuantity.
  Verify current semantics and avoid subtracting returns twice. Fully returned
  lines do not establish positive demand. Deduplicate lines across pages.
- Verify quantity units through available order/line detail before charting
  quantities. For multiple incompatible units, use distinct matching order
  count for comparison and show quantities per product/unit.
- Group by customer ID, then matched product. Show quantity/unit, distinct
  orders, most recent matching order, actual line purchase value and order reps.
  Purchase value is net quantity × actual line price, before unallocated
  order-level adjustments/tax. Average is over distinct matching orders, not
  a claim about the customer's entire relationship. Order rep is not necessarily
  the customer's current owner. Preserve multiple reps.
- Product purchase history does not prove the customer bought the lots now
  expiring. Buying one selected product does not imply buying all selections.
  Rank by an explicit observed measure, not an invented probability to buy.
- Keep products with no matching buyers visible and labelled. Do not silently
  broaden the history window or treat unknown history as zero demand.

### Contacts, offer and context

Resolve saved contacts by the selected customer company ID and check ownership
again. Let the user choose among multiple contacts. Missing name/email stays
missing; label any manual recipient input as supplied by the user.

Terms, deadline, optional minimum and sender come from the user. Do not infer
promotion policy, consent, a shipment commitment or sellable quantity.

Carry a compact reviewable context: company, report bounds/read times, selected
product IDs/names, qualifying quantities/units/lots/dates and eligibility,
matching customer/order/line evidence, chosen recipient and literal terms.
A price-based inventory value is optional context, not a revenue claim. Do not
include unrelated customers, internal costs, credentials or entire raw exports.

Revalidate/clear the recipient when the customer changes. Rebuild the handoff
when filters, product, terms or source data change; show the new scope before
submission. Distinguish live rechecks from supplied snapshots. Label truncation;
do not silently omit evidence or assume the conversation can open a private URL.

## Dashboard and interaction

The default screen should answer what needs attention before asking the user
to configure a report. Show active scope, meaningful inventory facts and buyer
coverage. A monthly value chart may help, but key product quantities and dates
must remain directly accessible. Do not let a large sparse chart dominate while
hiding urgent stock. Avoid mixed-unit KPIs and speculative revenue figures.

Use a compact title/company/last-read/Refresh header. Keep filters visible.
Show a readable inventory table with product/SKU, expiry and days remaining,
quantity/unit, location, price-based value/coverage and previous-buyer status.
Allow source-lot expansion separate from selection. Use focused detail areas
as needed; no mandatory three-tab layout or sequential loading wizard.

For a selected product, show a customer comparison with direct values and a
readable purchase table. Horizontal quantity bars work when units are verified;
otherwise show a clear valid metric. Preserve selected product/month and the
independent purchase period. Source drilldown supports the decision without
forcing the user to inspect raw records to discover basic totals.

A selected customer leads to recipient/context review and a clearly named
host-conversation action. The dashboard does not need an embedded email editor
or external model API. The draft is generated and revised in the conversation.
Use platform-supported handoff or an explicitly labelled Copy prompt fallback.

Keep useful last-successful results visible during refresh, with timestamp and
refresh/stale/error state. Preserve filters; reconcile selection against new
results rather than silently using outdated context. Local filters should use
authorized loaded data where possible. Scope caches/saved filters to user and
company and invalidate them appropriately. Honor runtime storage/connection
constraints; never share provider data across visitors to make loading faster.
Do not pass stale or still-partial evidence as current during drafting.

A saved view is optional follow-up customization, not a core build requirement.
If requested, store filter choices rather than inventory snapshots, identify
persistence scope, and explain out-of-window months. Test save/change/reopen.

## Visual review

Use readable labels, aligned numeric columns, useful whitespace and restrained
color. Give actual product/customer names room. Show important values without
hover. Do not use color alone for urgency or status. Keep implementation IDs
and connector diagnostics out of the ordinary workflow, available in evidence.

Inspect the initial dashboard, filtered inventory, expanded source lots, buyer
comparison/purchase detail, context preview and conversation draft at recording
size and a narrower viewport. Check keyboard focus and long names. Measure
first load and refresh honestly; report any loss of useful information while
waiting. Empty scope, failed reads and incomplete data must look different.
