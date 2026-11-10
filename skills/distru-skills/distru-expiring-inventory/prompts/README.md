# Prompts

Ready-made requests for this skill. Paste one as your message and replace the
bracketed parts ([your company], [product], [expiry month]) with your own. A
cloud chat cannot read a local path, so install the skill or attach its files first.

| Prompt | Mode | Claude | Codex |
| --- | --- | --- | --- |
| [create-claude-artifact.txt](create-claude-artifact.txt) | Build | ✓ (artifact; in Claude Code, a page) | |
| [create-chatgpt-site.txt](create-chatgpt-site.txt) | Build | | ✓ (Site; in the Codex app or CLI, a page) |
| [customize-saved-view.txt](customize-saved-view.txt) | Customize | ✓ | ✓ |
| [review-dashboard.txt](review-dashboard.txt) | Review | ✓ | ✓ |
| [draft-targeted-emails.txt](draft-targeted-emails.txt) | Draft outreach | ✓ | ✓ |

The two build prompts ask for the same dashboard; they differ only in where it
lives and how the brief reaches the chat. Each agent uses its own.

## Short versions (brackets are parameters)

**Build.** Use Distru Expiring Inventory to create a new private [Claude artifact /
ChatGPT Site / local page] with my connected Distru account. Verify [company].
Show stock expiring in the next six calendar months, its value at list price and
the source lots. Let me pick a product and month, compare the customers who bought
it in an editable 12-month window, and open a brief for one of them in [Claude /
ChatGPT] to draft the email. Keep results visible during Refresh and show read
times. Do not send anything or change Distru. Report what passed and what is untested.

**Review.** Use Distru Expiring Inventory in Review mode on [dashboard]. Check live
reads and Refresh, the expiring quantity and value against the lots, past buyers,
contacts, the handoff, the generated email and the opening screen. Show evidence
and corrections. Do not change Distru.

**Draft.** Use Distru Expiring Inventory in Draft outreach mode for [product and
expiry month]. If no targets are picked, show the matching buyers and contacts.
For [customer/contact], draft here using [discount, deadline, optional minimum,
sender]. Check the purchase and expiry facts; keep unknowns explicit. Do not send.

**Customize.** Use Distru Expiring Inventory to update [dashboard] with [change].
Keep its identity, connection, audience and data rules, and recheck what changed.
