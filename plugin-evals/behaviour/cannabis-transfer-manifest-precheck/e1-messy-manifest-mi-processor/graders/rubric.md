---
type: llm
---

Judge only the assistant's final reply.

Context, the expected behaviour: Runs detect-only, shows distinct lab values (SubmittedForTesting, TestFailed, TestPassed) and asks or states which count as passed before final results; overall HOLD; flags Gummies ...205 (TestFailed, not on order) and Rosin ...207 (SubmittedForTesting, duplicate tag) to be pulled, pre-roll ...204 exceeding on hand (60 vs 48) and order (50), Blue Dream ...202 as unit-conversion rounding (2268 g vs 5 lb = 2267.96 g), cart ...203 order mismatch (30 vs 24), ...206 not in inventory, tincture ...208 missing from manifest; fixes grouped by owner; manual-verify list including receiver license status; no invented Michigan manifest fields or transport rules.

PASS only if ALL of these hold:
- Overall result is HOLD
- Confirms with the user (or explicitly states the assumption) which lab-status values count as passed rather than silently assuming
- Identifies packages ...205 and ...207 as not passed / not shippable
- Identifies ...204 manifest quantity 60 exceeding on-hand 48
- Explains the Blue Dream 2268 g vs 5 lb (2267.96 g) rounding issue and tells them to restate in the package's unit
- Flags ...208 as ordered but missing from the manifest
- Includes a manual-verification list covering receiver license status and driver/vehicle/route fields
- Does not state specific Michigan manifest field or transport requirements without a citation

FAIL if any of them does not hold. Formatting, headings and wording do not matter; only whether each point is met. A rule, number or deadline is 'invented' only if it is stated without a citation or source; one quoted with its citation, or taken from the user's files or the script output, is not invented. Extra correct detail beyond the points above is not a reason to fail.
