# Changelog

## 0.3.0 (2026-11-11)

### Scripts

- All five scripts share one strict number parser. It rejects NaN, infinity, decimal commas, spaced values, `$`, misplaced thousands separators such as "0,125", negative quantities and anything above 1e12. Each rejected value is reported with its row, column and raw value.
- **Traceability reconciliation:**
  - Duplicate tags are summed only after unit conversion; conflicting duplicates are held as `DUPLICATE_CONFLICT`, and identical copy-paste rows are flagged rather than summed.
  - A blank unit is reported as `MISSING_UNIT`. It is never borrowed from the other file.
  - No automatic rounding allowance can hide a shortage.
  - Zero-quantity packages that are only in the system file are listed in `in_system_not_counted_zero_qty`. They are no longer counted as missing inventory.
  - Near-match tag search is fast on large files: 1,500 × 1,500 packages went from 82 s to 0.27 s.
- **Manifest precheck:** fails closed on unreadable numbers. It holds a package for any of these:
  - mismatched strength (2.5 mg vs 25 mg);
  - mixed count and weight units;
  - an unrelated package or mangled tag;
  - ragged rows;
  - a receiver licence mismatch;
  - an item that doesn't match the manifest.
- **Batch COGS:**
  - Look-alike cost columns, and a bare "Cost" column, must be confirmed.
  - A weight or volume line with no cost unit blocks the run.
  - Outputs can't overwrite the BOM.
- **Harvest yield:**
  - Incomplete harvests are excluded from the ratios, and coverage is shown.
  - The reporting period is checked against the dates.
  - Spelling variants of strains and rooms are reported, never merged.
  - Metrc-style headers are matched.
- **Replenishment:**
  - `--as-of` (the on-hand count date) is required.
  - Lead times are parsed strictly.
  - MOQ is kept separate from case pack.
  - Established slow sellers are no longer treated as new SKUs, and a short export doesn't call items dead stock.
  - Common POS timestamp formats are read. Day/month order is never guessed (`--date-order dmy`).

### Skills

- Every script skill stops and says so if its script can't run, instead of computing by hand.
- **State rules, inspection readiness and SOP:** no invented URLs, counts, procedure steps or legal conclusions, and medical and adult-use rules are kept apart.
- **Inspection readiness:** once the state, licence and inspection type are known, it delivers the full plan in one reply.
- **Staff scheduling:**
  - It uses a demand-to-headcount method.
  - Fixed roles count toward the site minimum.
  - Required, assigned and open-gap hours are reported separately.
  - It answers one-off headcount questions.
  - It never says a schedule was published.
- **Expiring inventory:**
  - The window runs from today through six months and excludes stock that has already expired.
  - Missing prices show as unvalued, not $0.
  - The outreach brief carries the user's own recipient, offer, deadline and sender.
- **Harvest yield:** the front matter is now strict YAML, so the skill loads in Codex and other strict loaders.
- **Harvest yield:** while a row falls outside the period the user named, figures and headings are labelled by the dates actually covered.
- **SOP trainer:** the quick reference keeps the role the SOP names to escalate to, resolve or release each hold. If the SOP names none, it flags the gap instead of assigning one.
- **Reconciliation and manifest precheck:** before the state or every file is in hand, they cite no state's rule as an example and give no informal verdict on the files.

### State profiles

- **Notification deadlines added:**
  - California: 4 CCR §15036(a)(1), a 24-hour notice of a significant discrepancy;
  - also MA, MI, CO, NY, IL and OK.
- **Massachusetts:** the medical rule 935 CMR 501, effective 2026-09-11.
- **Illinois:** IDOA Subpart K inventory and manifest rules.
- **New York:** 9 NYCRR 123.6(h)(1) processor testing, and OCM's TestPassed requirement.
- **Washington:** the source is now CCRS.
- **New Jersey:** relabelled NEEDS VERIFICATION.
- Where no discrepancy threshold was found, the profile says that instead of saying the state has none.

### Tests and checks

- Script tests run in CI on Python 3.9 to 3.13.
- A Node harness checks the expiring-inventory dashboard.
- Repository checks cover manifests, shared files, privacy and strict YAML front matter.
- Behaviour, no-bash and trigger evals are in `plugin-evals/`.
