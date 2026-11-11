---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs with --as-of 2026-09-30 --safety-days 2; summary.json is valid JSON and warnings is empty. input_problems lists, with row, column and raw value: sales units 'NaN' (EX-J), 'inf' (EX-K) and '4,25' (EX-L), each row left out; sales revenue '1.234,56' (EX-M) left out of revenue; on-hand 'inf' (EX-J, so EX-J shows NO_ONHAND_RECORD); unit cost '4,25' (EX-K, BAD_UNIT_COST, order cost blank); case pack 'NaN' (EX-L, BAD_CASE_PACK, quantity not rounded); open PO '1.234,56' (EX-M, BAD_OPEN_PO, held); on-hand '-3' (EX-P, NEGATIVE_ONHAND, held, no order). EX-N's returns (-8) exceed its sales (3), so it is flagged NEGATIVE_NET_SALES(-5) with velocity 0, not negative. EX-Q's on-hand '1,200' is read as 1,200 (SLOW). Vendor PO draft for Example Distro: EX-K 40 units (cost blank) and EX-L 40 units $240; PO total $240 with 1 line missing cost. skus_held_for_review is EX-M and EX-P. The pre-fix script crashed with OverflowError on the inf sales row.

PASS only if ALL of these hold:
- Reports each unreadable value (NaN, inf, 4,25, 1.234,56) with its SKU and column and asks for the right figure, without reinterpreting any of them
- Does not suggest an order for EX-P and says its on-hand of -3 must be corrected first
- Does not give EX-N a negative velocity; notes its returns exceed its sales in the window
- Does not order EX-M until the '1.234,56' open PO is confirmed
- States the Example Distro PO draft as $240 plus EX-K's 40 units with no cost (unit cost unreadable), not as a complete total
- Marks the PO as a draft not sent to any vendor

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
