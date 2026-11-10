# Distru Expiring Inventory

Skill: [`distru-expiring-inventory`](../../skills/distru-skills/distru-expiring-inventory/SKILL.md)

## What it does

Turns stock that is about to expire into outreach you can act on. It builds a dashboard from your live Distru data: how much stock expires in each of the next six months and what it's worth at list price, which customers have bought each product before, and a ready-made brief for a promo email to each of them. You send the brief to your agent, which drafts the email in your chat for you to review. The dashboard follows Distru's brand and comes with a reference version to copy. It never sends email, reserves stock or changes anything in Distru.

## When to use it

- "What inventory is expiring in the next six months?"
- "Who already buys this product, so we can move the dated stock?"
- "Draft a promo email to the customers who bought this last quarter"
- "Review this expiring-inventory dashboard and check the numbers"
- "Add a saved view for next month's expirations"

## How to use it

- **Inputs:** your connected Distru account. Optional: a product, expiry month, locations, the purchase-history window, and your offer terms (discount, deadline, minimum, sender).
- **Tools / connectors:** the Distru MCP, read-only.
- **Works in:** Claude (an artifact in Claude.ai or the desktop app, or a page in Claude Code) and Codex / ChatGPT (a ChatGPT Site, or a page in the Codex app or CLI). The skill tells each agent which route to follow.
- **Modes:** Build a new dashboard, Customize an existing one, Review one for accuracy, or Draft outreach straight from your data without a dashboard.
- **Defaults:** expirations from today through six calendar months ahead, and purchase history over the last 12 months, both editable.
- **Safeguards:** value is labelled "at list price" and is never shown as cost, margin or revenue. Partial data is shown as partial. Discounts stay a placeholder until you set them. A page that can't read live data is labelled a snapshot with its read time.

## Example

**Input:** "Build an expiring-inventory dashboard with my connected Distru account. Start with the products expiring next month."

**Output:** a dashboard headed by the stock value expiring in the window, the number of products and packages affected, and the past buyers to offer it to. A chart shows value by expiration month, and a product-by-month grid lets you pick a product and month. That opens a table of every past buyer with their orders, units, last order date and sales rep, with a **Draft promo email** button on each row. The button opens a brief in your agent's chat, which writes a short email from the rep that states the expiration date plainly and leaves the discount as `[X]% off` for you to fill in.
