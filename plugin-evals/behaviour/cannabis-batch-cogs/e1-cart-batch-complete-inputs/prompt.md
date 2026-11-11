---
name: cannabis-batch-cogs--e1-cart-batch-complete-inputs
description: "evals.json #1: cart-batch-complete-inputs"
tags: ["behaviour", "cannabis-batch-cogs", "from-evals-json", "needs-bash"]
plugins: ["../../../.."]
runs: 3
max_turns: 40
timeout_seconds: 600
allowed_tools: ["Read", "Glob", "Grep", "Skill", "TodoWrite", "Bash"]
append_system_prompt: "Put your complete reply in your final message: the full report, plan or draft, and any questions you need answered. Do not only write it to a file."
---

What did our Gelato cart batch GEL-CART-1003 really cost per unit? BOM attached. 14 labor hours at $24 loaded, overhead is $35 per labor hour, lab was $425. We expected 500 carts and got 492.

(The attached files are in the `resources` folder: `bom_distillate_cart_batch.csv`.)
