# The reference dashboard

[assets/expiring-inventory-dashboard.html](../assets/expiring-inventory-dashboard.html)
is what a finished build should look and feel like. It is one offline file
(fonts and d3 inlined) built on Distru's 2026 brand, and it is the dashboard
shown in Distru's expiring-inventory demo video.

Open it in a browser. Add `?agent=claude` to see the Claude handoff; without it
you get the ChatGPT / Codex handoff.

## What it is, and is not

- **Data:** a frozen snapshot of Distru's staging demo account (read November 5,
  2026), with every name replaced by an invented one: the seller is "Evergreen
  Valley Wholesale", the reps are "Glen Gary" and "Glen Ross", and products and
  buyers are made up. Numbers, dates and IDs are unchanged.
- **Not live:** it reads nothing. Copy its design and interactions, then wire them
  to real reads as your route describes. Never ship its snapshot as anyone's data.
- **Partial on purpose:** its order history is the first 4,000 of 8,983 lines, and
  says so beside the buyers, in the footer and in every brief. Keep that kind of
  honesty: with a partial read, "no buyers" means "no matching lines in what was
  read", not "no demand".
- **Snapshot gaps:** its records carry no package IDs, line IDs, order statuses
  or units. The page says what it could not check. A live build reads those
  fields and applies the rules below to them.

## Data rules the reference implements

The `ExpiryModel` script block holds the date, valuation and buyer rules as
plain functions, separate from the screens. Keep them when you copy the page,
and feed them company-local dates.

- **Window:** today through the same day N calendar months ahead, inclusive,
  with month-end clamping (Aug 31 + 6 months is Feb 28 or 29). Filter each lot
  by its own expiry date, then label every month the window touches: six months
  from November 5 runs to May 5 and shows seven month labels. Already-expired
  lots stay out of the window and are counted separately. The chart, the four
  figures and the matrix all use the same window.
- **Quantities:** only finite numbers count. A string such as `"2"` or `"1,5"`,
  `NaN`, `Infinity` or a negative quantity is held out and counted, never
  coerced. Duplicate package IDs count once. A package whose unit differs from
  its product's is held out rather than added.
- **Value:** wholesale price, or unit price where no wholesale price is set. No
  price on record means unvalued, not $0; a recorded $0 stays $0. Unvalued and $0
  stock stays selectable in the matrix ("No price", or a "+" when only part of
  a cell is unvalued), and the lead figure says how many products are unvalued.
- **Buyers:** a line counts only when it is dated inside the history period
  (12 months to today by order date), has a positive quantity and a positive
  price (net of returns; $0 lines such as samples are not purchases), has a
  `DELIVERED` or `COMPLETED` status when status is present, and is not a sample.
  Duplicate line IDs count once; without line IDs, identical lines count once.
  Every order rep is kept. Each excluded group is counted in the footer.

## Copy these

1. **Hero (dark):** eyebrow "Inventory · <company>", the title "Expiring
   *inventory*" with one accent word, a one-line explanation, and a window toggle
   (6 / 12 / 18 months; 6 by default).
2. **Four figures:** expiring value at list price (the lead figure, with the
   window's actual dates and any unvalued products under it), products with
   stock expiring, packages, and past buyers to offer it to. They count up once.
3. **Value by expiration month:** stacked bars by product, a pill on the peak
   month, and a tooltip with the month's products and values. Click a bar to pick
   that month.
4. **Product × month matrix:** one row per product, one cell per month in the
   same window as the chart, shaded by value. Click a cell to pick that product
   and month. Changing the window drops a pick that is no longer in it.
5. **Offer table** for the pick: the selected lots with each expiry date, then
   each past buyer with initials, orders, units, last order date, last order
   value and every order rep, most recent first, and a **Draft promo email**
   button per buyer.
6. **Brief drawer** under the row: "To <buyer>", fields for the user's own
   recipient, offer, order-by date, optional minimum and sender, the brief in a
   read-only box that updates as they type, then the handoff buttons for your
   route and **Copy brief**. An order-by date on or after the first lot's expiry
   is flagged in the drawer and in a note outside the email.
7. **Footer:** the read time and whether it is live or a snapshot, the window's
   dates, how value is calculated, the history period and how much of it was
   read, and every group of records held out.

The brief it writes (angle brackets come from the data; the terms come only
from what the user typed):

```
Draft a short promotional email from <company>, a cannabis wholesaler, to one of its retail customers. This is a draft for me to review and send myself; do not send, schedule or queue anything.

Source: Distru snapshot read <read time>. This is not a live read; re-check the facts in Distru if freshness matters.
Customer: <buyer> (customer ID <id>)
Recipient: <what the user entered, or "[Recipient not set: ask the user, do not invent it]">
Product: <product> (product ID <id>)
Selected lots (<month>, inside the expiry window <start> to <end>): <n> packages, <units> units in total: <units> expiring <date>; <units> expiring <date>.
Value: about <value> at list price (<price> per unit), before discounts and tax. This is not cost, margin or revenue; do not put it in the email.
Their paid history with this product, orders dated <start> to <end> (<4,000 of 8,983 order lines read, so some buyers may be missing>): <orders> orders, <units> units; last ordered <date>, <value> of it on that order. This does not show they bought these particular lots.
Order reps on those orders: <reps>. Context only; they are not the sender.

Offer: <user's offer, or "[Offer not set: ask the user, do not invent it]">
Order by: <user's date, or "[Deadline not set: …]">
Minimum order: <user's minimum, or "none given">
Sender: <user's sender, or "[Sender not set: …]">

Put the subject line first as "Subject: …", then a blank line, then a warm, specific body under 150 words that references their past orders of this product. Be upfront that this is dated stock and state the selected lots' expiration dates plainly; do not apply them to all of this product. Use only the facts above. Do not promise availability, shipment or release status. Keep anything still in [brackets] as a bracketed placeholder and list what I still need to fill in. Plain text, no markdown.
```

The user sets the offer, deadline, recipient and sender. A blank term stays a
bracketed placeholder; the brief never picks a discount, and never signs as an
order rep or "the sales team". A live build says "live read <time>" instead of
"snapshot".

## Brand (Distru 2026)

- **Type:** Open Sauce Sans 800 for headlines (letter-spacing -0.04em), Open Sauce
  One for body text.
- **Colour:** dark top in Night `#030805` / Forest 800 `#313F2F`; light body in
  White and Sand `#F5F5EC`; Mint `#36E8AA` only on dark, for one accent word or the
  lead figure. Chart series in order: Forest `#313F2F`, Mint `#36E8AA`, Slate 600,
  Slate 300, Leaf `#12A150`, Other `#E4E4D8`. Matrix ramp Lime `#FBFFE5` → Mint
  Hover `#8CF6C8` → Bean `#4D8062` → Forest `#313F2F`.
- **Motion:** bars grow, figures count up; no gradients, spinning or bouncing.
  Honour `prefers-reduced-motion`.

If the user's own company is not Distru-branded, keep the layout and swap the
colours, but keep the contrast and the single accent.
