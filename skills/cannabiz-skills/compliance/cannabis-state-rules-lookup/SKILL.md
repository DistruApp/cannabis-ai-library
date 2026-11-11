---
name: cannabis-state-rules-lookup
description: Answer "what does our state require?" questions for licensed cannabis operators with a cited, dated answer from primary sources (state regulator rules, administrative code, official traceability guidance), and flag what can't be verified. Use when an operator asks about a state cannabis rule, deadline, reporting window, which traceability system their state uses (Metrc, BioTrack, CCRS, NMS2S, etc.), whether something is allowed, or wants a rule checked before acting, even if they don't name the regulation. Also use when they ask what a federal change such as marijuana rescheduling means for them (it gives the cited federal status and sends 280E planning to a CPA), or ask for a state notice (such as a discrepancy or theft notice) to be drafted, filed or sent to a regulator or police (it gives the cited deadline and what the notice must contain; the operator drafts and files it). Not for 280E tax planning itself, legal opinions, or filing or drafting regulatory submissions; route those to a CPA or attorney.
license: MIT
metadata:
  version: "1.0"
  category: compliance-traceability
  risk-level: high
  last-compliance-review: "2026-11-11"
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

**Keep the programs apart.** Where a state has separate adult-use and medical rules (e.g. Massachusetts: 935 CMR 500 adult use, 935 CMR 501 medical), a profile item cited only to one program's chapter doesn't answer a question about the other. If the profile doesn't cite the operator's own program's section for that item, treat it as NEEDS VERIFICATION against that program's rules, name the chapter to check, and don't recommend an SOP change from the other program's text.

### 2. Check the profile
Use `references/state-profiles.md` first. For each item note its label **and the version of the text behind it** (e.g. "Cornell LII copy amended through 2024-12-04"), not just the profile's review date: a recently reviewed copy of an old rule is still an old rule. How each label may be used:

- **V\*** and **V**: cite with the source version and check date.
- **V (LII)**: cite as "the Cornell LII copy of [rule], amended through [date] (a secondary copy), says …", and give the official page to confirm the current text.
- **NEEDS VERIFICATION**: cite as "the [version] text says …; the current text wasn't confirmed".
- **Vendor-only**: say it comes from the vendor.
- **UNVERIFIED**: can't be stated as fact. Say what it rests on and where to confirm it.

This is how the jurisdiction gate's "cited" rule applies here: a deadline or threshold can come only from a profile item (with its label) or from text you read live in this session. A V (LII) or NEEDS VERIFICATION item tells the operator what that version of the rule says, never what their confirmed current obligation is.

If the profile is past its review-by date, the item is flagged pending a change, or it's labelled NEEDS VERIFICATION or UNVERIFIED, check it live before answering. If you can't, the answer is **verification-only**: give the citation, the stored text with its version and label, and the page to check, and in WHAT THIS MEANS FOR YOU tell the operator not to change an SOP, post an adjustment or decide a report isn't needed on the strength of it until the current text is confirmed.

### 3. Research live (when web access is available)
Follow `references/research-method.md`: find the operative text of the current rule (the regulator's rules page, then the official administrative code to confirm the version), and use guidance, FAQs and Metrc bulletins to explain how to comply, not to settle what's required. Record the exact URL, quote the operative sentence word for word, and note the effective date and the date you accessed it. **Without web access**, answer only from the profile, say you couldn't re-check it in this session, and say what needs checking.

### 4. Answer

```
ANSWER: [one or two plain sentences]
JURISDICTION: State · license type · activity
SOURCE: [citation] — [URL, or "no URL in profile"] — [effective date or source version] — checked [date, and "not re-checked this session" if so] — [V / V (LII) / Vendor-only / NEEDS VERIFICATION / UNVERIFIED]
EXACT TEXT: "[operative sentence]", or "No quote on file; profile summary only"
WHAT THIS MEANS FOR YOU: [operational steps]
OPEN QUESTIONS / AMBIGUITIES: [e.g., the rule doesn't define the base for a % threshold]
VERIFY WITH: [compliance lead / counsel] before [submitting / changing SOP]
```

## Before you reply

- **SOURCE has the URL on file.** Copy the citation and URL from `references/state-profiles.md` even when you can't open the page in this session, and say you didn't re-check it. If the profile item has no URL (some rows in the other-states table don't), write "no URL in profile" and name the regulator to check. Never build or guess a URL, and never put words in quotation marks that aren't quoted in the profile or on a page you read.
- **No numbers from memory.** If the state or topic isn't in the profile and you can't research it live, don't give a period, count, deadline or threshold at all, not even labelled UNVERIFIED or "as I recall". Say it's NEEDS VERIFICATION and name the regulator and rule set to check. Don't quote other states' rules for comparison.
- **"None found" isn't "none exists".** When the profile says no threshold, deadline or rule was found, say none was found in the sections and version the profile names, keep its label, and don't tell the operator they have no obligation. Still don't borrow another state's number.
- **You never file, send or notify** anyone (a regulator, the police, an inspector), not now and not "if you give me access", and you don't draft the submission (the form, letter or email) for them. Say the operator does it, list what the cited rule says the notice must contain, send drafting to their compliance lead or counsel, and still give the cited rule they're acting on (e.g. California's 24-hour notice to DCC and local law enforcement under 4 CCR §15036(a)(1); the notice to DCC goes on form DCC-LIC-028).
- **Federal questions** (rescheduling, "is 280E over?"): give the federal status from the Gotchas with its FR document number, effective date, link and as-of date, ask the state and whether the business is medical, adult-use or both (that decides whether the Schedule III placement covers it), and send the tax conclusion to a CPA. If you can't re-check it in this session, say federal status may have changed since that date.

## Gotchas

- **Traceability systems change.** NY and IL moved from BioTrack to Metrc. NM moved from BioTrack to its own system (NMS2S) in Aug–Sep 2026. WA uses the state-built CCRS. Don't assume "Metrc or BioTrack."
- **Same vendor, different rules.** Two Metrc states can have different reporting windows, adjustment reasons, and item categories. Never carry a rule across states.
- **Unofficial compilations.** California's DCC regulations page is an unofficial compilation; the official text is the CCR. Say which one you cited.
- **Pending rule changes.** If a regulator has a rulemaking open on the topic, say so. The answer might be different soon.
- **Ambiguous rules.** When a rule doesn't define a term (e.g. what a percentage threshold is measured against), list the plausible readings. Don't pick one for the operator.
- **Federal status.** As of 2026-11-11, FR Doc 2026-08176 (91 FR 22714, effective 2026-04-28) placed in Schedule III marijuana "in a U.S. Food and Drug Administration approved product **or subject to a state medical marijuana license**" (21 CFR 1308.13(g)(2)). It also created an expedited DEA registration path for state medical licensees under 21 CFR part 1301. Adult-use and other unlicensed marijuana stays in Schedule I: "any form of marijuana other than in an FDA-approved drug product or marijuana subject to a state medical marijuana license remains a schedule I controlled substance". General rescheduling is still pending. FR Doc 2026-08177 (Docket DEA-1362) noticed a DEA hearing starting 2026-06-29, and no final rule had appeared in the Federal Register as of 2026-11-10. (V. FR Doc 2026-08176: https://www.govinfo.gov/content/pkg/FR-2026-04-28/html/2026-08176.htm; FR Doc 2026-08177: https://www.govinfo.gov/content/pkg/FR-2026-04-28/html/2026-08177.htm. Both re-checked on govinfo 2026-11-11; federalregister.gov blocks automated access.) Whether DEA registration applies to an operator, and how any of this affects 280E, are **counsel and CPA questions**. The rule itself says "Nothing in this rule constitutes a determination regarding federal tax liability". Never say 280E does or doesn't apply to them.
- **Paraphrase isn't a quote.** Only put text in quotation marks if the profile quotes it or you saw it on the source page.

## Example

User: "We're a California distributor. How often do we have to reconcile Metrc, and what happens if we're off?"

Answer: "At least every 30 calendar days. If you find a discrepancy you have to audit it, and if it's 'significant' (a 5% difference between physical and track-and-trace inventory) you have to notify DCC in writing. Separately, a significant discrepancy must be reported to DCC and local law enforcement within 24 hours of discovering it; the notice to DCC goes on form DCC-LIC-028. You file both notices; I can't send them for you." Then SOURCE: 4 CCR §15051 and §15034 from the DCC unofficial compilation in effect as of 2026-10-01 (V\*), and §15036(a)(1) from the Cornell LII copy amended 2022-11-07 (V (LII)), each with its URL, check date and exact text, and a note that it wasn't re-checked this session if it wasn't. Then the open question: the rule doesn't say whether 5% is per package or on total inventory, so confirm with counsel. Then: "Separately, the account manager must correct data-entry errors within 3 calendar days of discovery (§15048.1)."
