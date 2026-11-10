---
name: cannabis-state-rules-lookup
description: Answer "what does our state require?" questions for licensed cannabis operators with a cited, dated answer from primary sources (state regulator rules, administrative code, official traceability guidance), and flag what can't be verified. Use when an operator asks about a state cannabis rule, deadline, reporting window, which traceability system their state uses (Metrc, BioTrack, CCRS, NMS2S, etc.), whether something is allowed, or wants a rule checked before acting, even if they don't name the regulation. Not for federal tax planning (280E strategy), legal opinions, or drafting regulatory submissions; route those to a CPA or attorney.
license: MIT
metadata:
  version: "1.0"
  category: compliance-traceability
  risk-level: high
  last-compliance-review: "2026-10-16"
---

# State rules lookup

Gives an operator a **cited** answer they can act on, or tells them plainly that the answer couldn't be verified and where to check. A wrong rule stated confidently is worse than no answer.

## Workflow

```
- [ ] 1. Pin the jurisdiction (references/jurisdiction-gate.md)
- [ ] 2. Check references/state-profiles.md
- [ ] 3. If not covered or stale: research live (references/research-method.md)
- [ ] 4. Answer with the template below
```

### 1. Jurisdiction
State, license type, activity. Adult-use vs. medical matters (OK and FL are medical-only programs; PA's program is medical). In Illinois, the regulating agency depends on license type. Ask once if missing.

### 2. Check the profile
Use `references/state-profiles.md` first. Note each item's verification level: **V\*** and **V** can be cited (with the date), **Vendor-only** has to be described as such, and **UNVERIFIED** can't be stated as fact. If the profile's review date is more than 90 days old, or the item is flagged as pending a change, verify it live before answering.

### 3. Research live (when web access is available)
Follow `references/research-method.md`: start from the regulator's site, then the official administrative code, then official traceability guidance (Metrc bulletins for that state). Record the exact URL, quote the operative sentence word for word, and note the effective date and the date you accessed it. **Without web access**, answer only from the profile and say what needs checking.

### 4. Answer

```
ANSWER: [one or two plain sentences]
JURISDICTION: State · license type · activity
SOURCE: [citation] — [URL] — effective [date] — checked [date] — [V / Vendor-only / UNVERIFIED]
EXACT TEXT: "[operative sentence]"
WHAT THIS MEANS FOR YOU: [operational steps]
OPEN QUESTIONS / AMBIGUITIES: [e.g., the rule doesn't define the base for a % threshold]
VERIFY WITH: [compliance lead / counsel] before [submitting / changing SOP]
```

## Gotchas

- **Traceability systems change.** NY and IL moved from BioTrack to Metrc. NM moved from BioTrack to its own system (NMS2S) in Aug–Sep 2026. WA uses the state-built CCRS. Don't assume "Metrc or BioTrack."
- **Same vendor, different rules.** Two Metrc states can have different reporting windows, adjustment reasons, and item categories. Never carry a rule across states.
- **Unofficial compilations.** California's DCC regulations page is an unofficial compilation; the official text is the CCR. Say which one you cited.
- **Pending rule changes.** If a regulator has a rulemaking open on the topic, say so. The answer might be different soon.
- **Ambiguous rules.** When a rule doesn't define a term (e.g. what a percentage threshold is measured against), list the plausible readings. Don't pick one for the operator.
- **Federal status.** As of 2026-10-16, FR Doc 2026-08176 (effective 2026-04-28) moved FDA-approved marijuana products to Schedule III and created an expedited DEA registration path for state medical licensees. How it affects 280E for a particular operator is a **CPA question**. Never say 280E does or doesn't apply to them.
- **Paraphrase isn't a quote.** Only put text in quotation marks if you saw it on the source page.

## Example

User: "We're a California distributor. How often do we have to reconcile Metrc, and what happens if we're off?"

Answer: "At least every 30 calendar days. If you find a discrepancy you have to audit it, and if it's 'significant' (a 5% difference between physical and track-and-trace inventory) you have to notify DCC in writing." Then SOURCE: 4 CCR §15051 and §15034, from the DCC unofficial compilation in effect as of 2026-10-01 (V\*), with the exact text. Then the open question: the rule doesn't say whether 5% is per package or on total inventory, so confirm with counsel. Then: "Separately, the account manager must correct data-entry errors within 3 calendar days of discovery (§15048.1)."
