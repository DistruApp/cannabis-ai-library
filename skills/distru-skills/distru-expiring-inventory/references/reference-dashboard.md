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
  says so. Keep that kind of honesty.

## Copy these

1. **Hero (dark):** eyebrow "Inventory · <company>", the title "Expiring
   *inventory*" with one accent word, a one-line explanation, and a window toggle
   (6 / 12 / 18 months; 6 by default).
2. **Four figures:** expiring value at list price (the lead figure), products with
   stock expiring, packages, and past buyers to offer it to. They count up once.
3. **Value by expiration month:** stacked bars by product, a pill on the peak
   month, and a tooltip with the month's products and values. Click a bar to pick
   that month.
4. **Product × month matrix:** one row per product, one cell per month, shaded by
   value. Click a cell to pick that product and month.
5. **Offer table** for the pick: each past buyer with initials, orders, units,
   last order date, last order value and the sales rep, most recent first, and a
   **Draft promo email** button per buyer.
6. **Brief drawer** under the row: "To <buyer>, from <rep>", the brief in a
   read-only box, then the handoff buttons for your route and **Copy brief**.

The brief it writes:

```
Write a short promotional email from <company>, a cannabis wholesaler, to one of its retail customers.

Customer: <buyer>
Product: <product>
Stock to move: <units> units, about <value> at list price (<price> per unit), expiring in <month>; the first package expires <date>.
Their history with this product in the last <history window, 12 months by default>: <orders> order(s), <units> units; last ordered <date>, <value> of it on that order.
Sales rep: <rep>. Write it in their voice and sign it from them.

Put the subject line first as "Subject: …", then a blank line, then a warm, specific body under 150 words that references their past orders and offers a time-limited deal to stock up now. Be upfront that this is dated stock and state the expiration date plainly. Use "[X]% off" as a placeholder for the discount. Plain text, no markdown.
```

Leave the discount as a placeholder unless the user gives one: the user sets it.

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
