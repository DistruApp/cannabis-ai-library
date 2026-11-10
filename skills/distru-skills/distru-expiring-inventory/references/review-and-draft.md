# Review and targeted drafting

## Review mode

Identify the actual app/revision, company, platform, bounds, product selection
and completeness. Use Check | Pass/Fail/Not tested | Evidence | Correction.
A successful build or ZIP validation is not a live capability check.

1. **Connection:** app identity/read and subsequent Refresh. Distinguish native
   chat, local preview and hosted app; test each claimed runtime separately.
2. **Stock/value:** sum selected qualifying lots; verify boundaries, units,
   locations and active quantity. Reconcile price-based value separately from
   full-product value, actual cost and availability. Check missing prices and
   date/eligibility states. No double reservations/assembling subtraction.
3. **Buyers:** trace a customer comparison to selected-product sales lines.
   Verify statuses, samples, net returns, units, dates, actual prices and paging.
4. **Recipient/context:** confirm contact ownership, matching product purchase
   claims, qualifying lots, source times and literal user-entered terms. Change
   customer/product and ensure stale recipient/context is not reused.
5. **Handoff:** inspect the prepared payload, then verify the intended host
   conversation actually receives it. A link opening or prefilled composer is
   one checkpoint, not proof of connector selection or email generation.
6. **Generated email:** after submission, check subject/body against source
   facts, recipient and terms; request a wording change and check them again.
   Do not confuse an earlier deterministic app template with host AI generation.
7. **Interaction:** dates/locations/product changes, no-buyers/no-contact states,
   partial reads and refresh failure. Time loading, observe stale results and
   selection behavior. Verify optional saved-view persistence if implemented.
8. **Visual quality:** inspect the opening screen, filtered stock, buyer chart,
   source detail, context review and draft. Can the user quickly identify stock,
   quantity, expiry, a previous buyer and a next action? Check recording-size
   text, long names, direct chart values, keyboard focus and narrow layout.

Use clearly labelled isolated synthetic boundary tests where useful. Do not
change ERP data to make a review pass. If only reviewing, report findings; if
fixes were requested, change only the authorized app and rerun affected checks.

## Draft outreach mode

Use selected products/customers from the dashboard or user request. Resolve
ambiguous names to IDs. If selecting targets, show matching products, quantity
and unit/order count, last purchase, candidate contacts and inclusion evidence.
Rank on a stated observed metric. Do not claim a probability of buying again.

If recipients are already selected, preserve that scope. Recheck contacts belong
to the customer. If context arrives as copied text, distinguish supplied facts
from live connector verification. Re-read when freshness matters and access
permits; never claim a live read that did not occur. A private URL alone is not
verified input. Missing required facts remain unresolved.

Use user-provided offer terms, deadline, optional minimum and sender. Ask for
missing required terms before presenting a recipient-ready offer. Do not invent
a discount or contact. Flag a deadline inconsistent with expiry and any stock
eligibility/availability limitation outside the customer-facing message.

Draft an editable subject/body in the host conversation. Mention verified prior
buying only for the products actually bought. Describe the selected lots' date
or range; do not assign one expiry to the entire product. Do not promise stock,
shipment, release status or revenue. Use the user's tone and requested length.

Example structure (brackets are user inputs, never fabricated facts):

> Subject: [Product] — [entered offer]
>
> Hi [chosen contact],
>
> You previously ordered [verified product]. We have selected inventory with
> an expiration date of [verified date/range]. [Entered offer and deadline.]
>
> Would you like us to confirm availability for your next order?
>
> [User-provided sender]

Keep the evidence/check summary outside the email: recipient source, selected
product/lot scope, terms, source read time and unresolved facts. Let the user
request wording edits and preserve all factual constraints while rewriting.
Sending, scheduling, campaigns, stock reservations and ERP writes are outside
this workflow. A draft does not establish consent, a sent email or a sale.
