# Gate 5 fixes: distru-expiring-inventory

Skill: `skills/distru-skills/distru-expiring-inventory/` (no Python script). Review: `pi-distru-expiring-inventory.md`. Built on the files as changed by this morning's triage pass. Most findings are in the bundled reference `assets/expiring-inventory-dashboard.html`. I reproduced them by running the original page's JavaScript in Node 26 with the real inlined d3 and a stub DOM. I did not open it in a browser.

## Reproduction against the original page

`repro-original.mjs` (scratchpad) on the pre-fix file, with today set to 2026-11-05:

```
F1 months: 2026-11..2027-04 | total value: 300   (correct: $500; the Nov 1 lot is expired, the May 5 lot is in the window)
F2 string qty units: "023" | value with no price on record: 0 | unitPrice: 0
F3 duplicate line -> {"orders":1,"units":10,"lastOrderValue":80}
F3 buyers from zero/negative/$0/7-year-old lines: Zero, Neg, Sample, Old
F5 brief: "Sales rep: R. Write it in their voice and sign it from them." + "[X]% off"
F7 renderHeat source uses monthsAhead(6): true
```

The bundled snapshot itself showed the problems. It has 6 already-expired packages (June and August 2026) and 136 order lines at $0 that were counted as purchases. It also has 3 identical order lines that were double-counted.

## Findings

| ID | Reviewer | Verdict | Mine | Fix | Regression check (harness) |
|---|---|---|---|---|---|
| F1 | P0 | CONFIRMED | P0 | New `ExpiryModel.bounds`: today through the same day N months ahead, inclusive, with month-end clamping (`addMonths`). Each lot is filtered by its own date. Every month the window touches gets a label (7 labels for 6 months). Expired lots are held out and counted. The window's dates are shown under the lead figure, in the matrix note, the footer and the brief. | `window is today through six months ahead…`, `reviewer walkthrough…` (50 units, $500), `addMonths clamps month ends`, `snapshot: default window…` |
| F2 | P0 | CONFIRMED | P0 | Only finite numbers count. Strings, `NaN`, `Infinity` and negatives are held out and counted, never coerced. A missing or invalid price is unvalued (`null`), not $0, and a recorded $0 stays $0. Coverage is shown ("N products unvalued"). $0 and unvalued cells stay selectable ("No price" / "+"). Duplicate `packageId`s count once, and missing IDs are disclosed. A package whose unit differs from its product's is held out. | `missing price is unvalued…`, `string, NaN, Infinity and negative quantities…`, `negative or string price…`, `duplicate package IDs…`, `a package in a different unit…`, `missing or impossible expiry dates…` |
| F3 | P0 | CONFIRMED | P0 | New `ExpiryModel.buyers`. A line counts only if it is dated in the 12-month history, has positive finite quantity and price, has `DELIVERED`/`COMPLETED` status when status is present, and is not a sample. Lines are deduped by `lineId`, or as identical lines when there are no IDs. Every order rep is kept. A missing `orderDate` no longer crashes. | `identical duplicate line…`, `duplicate line IDs…`, `zero, negative and $0 lines…`, `lines outside the 12-month history…`, `missing order date…`, `all order reps kept…`, `snapshot: $0 order lines…` (3 duplicates, 136 unpaid) |
| F4 | P1 | CONFIRMED | P1 | History completeness ("4,000 of 8,983 order lines read, so some buyers may be missing") now appears beside the buyers, in the footer and in the brief. "No one has ordered it" became "No paid order lines for it dated … in the history read (…)". | `brief: carries IDs, read time…`, `footer: discloses…` |
| F5 | P0 | CONFIRMED | P0 | The brief drawer now has fields for recipient, offer, order-by date, optional minimum and sender. They go into the brief literally and update the handoff links as the user types. A blank term becomes `[Offer not set: ask the user, do not invent it]` and similar. Order reps are listed as "Context only; they are not the sender"; the brief no longer signs as a rep or "the sales team" and no longer says `[X]% off`. An order-by date on or after the first lot's expiry is flagged in the drawer and in a note outside the email. `references/reference-dashboard.md`, the SKILL.md handoff rule and the docs page now match. | `brief: user terms go in literally…`, `brief: an order-by date on or after…` |
| F6 | P1 | CONFIRMED | P1 | The brief now carries the read time and a "snapshot, not live" label, customer and product IDs, and every selected lot's date and units. It also carries the window bounds, the history bounds and completeness, the chosen recipient and the literal terms. It says "not cost, margin or revenue", that history ≠ these lots, "do not send, schedule or queue", and that bracketed facts must stay unresolved. | `brief: carries IDs, read time, every lot date…` |
| F7 | P1 | CONFIRMED | P1 | The matrix uses the same window model as the chart and figures. Changing the window drops a selection, and any open brief drawers, that no longer exist in the new window. | `window change: matrix and chart share months; stale selection is cleared` |
| F8 | P1 | CONFIRMED (partly fixed) | P2 | The assertions are tighter. Case 1 now requires explaining how to connect. Case 2 now prohibits send, schedule, draft-creation or Distru-write tool calls, not just claims. Case 3 now prohibits signing as a rep or the sales team. Connected-tool fixtures with numeric answers need a Distru mock in `plugin-evals/`, which I may not edit; see open items. | `evals/evals.json` |

## How the page is structured now

The data rules moved into their own `<script>` block (`ExpiryModel`: `parseDay`, `addMonths`, `monthKeys`, `bounds`, `priceMap`, `expiring`, `buyers`). It has no DOM access, so it can be tested in Node, and a builder can copy the rules separately from the screens. The UI script keeps the original design, brand, chart and handoff routes. The rules "no Distru connection, no numbers" and "draft only, never send" are unchanged. The page still reads nothing live and still labels itself a snapshot.

The demo numbers change. The default window is now Nov 5, 2026 – May 5, 2027 (7 months shown). Buyers no longer include $0 lines or duplicates. The demo video therefore no longer matches the page exactly.

## Checks run

- `node check-dashboard.mjs assets/expiring-inventory-dashboard.html`: **24 checks passed**. It covers the model rules, plus the real app script run with the inlined d3, the snapshot, the window change, the brief text and the footer.
- Every script block parses, and the longest brief on the snapshot is 2,487 URL-encoded characters (18-month window).
- `python3 scripts/check_repo.py --no-cli`: 7,324 passed, 0 failed.

## Files changed

`assets/expiring-inventory-dashboard.html`, `references/reference-dashboard.md`, `SKILL.md` (the handoff rule only), `evals/evals.json`, `docs/distru-skills/distru-expiring-inventory.md`.

## Shared-file changes needed

None.

## Open items

1. **Regression test has no home in the repo.** Resolved: the Node harness is now `tests/js/check_expiring_dashboard.mjs`, and CI runs it with Node 22.
2. **Not browser-tested.** Resolved for 0.3.0: a Claude session checked it in a browser on 9f3e1d7 (see the release report). Still to check by eye: the new terms fields (layout, focus, narrow screens), the handoff links updating as the user types, the "No price" / "+" matrix cells, multi-rep cells, and the 19-column matrix at 18 months.
3. **Upstream template.** The HTML says "Built by scripts/build_dashboard.py … edit this template, then rebuild". That script is not in this repo. A rebuild from an older upstream template would undo these fixes, so port them there.
4. **Without line IDs**, identical order lines are counted once. That can undercount if Distru has two identical lines on one order. The footer discloses it, and a live build should read line IDs.
5. **Connected numeric evals (F8).** These need a Distru tool mock and fixtures in `plugin-evals/`. The cases: date boundaries, duplicate pages, price coverage, returns, units, partial reads, and literal terms in the handoff.
6. **Suite rebuild** is needed for the `evals/evals.json` assertion changes.
7. **Demo video** now differs from the reference (window, buyer counts, brief). Re-record it, or note the difference where the video is shown.
