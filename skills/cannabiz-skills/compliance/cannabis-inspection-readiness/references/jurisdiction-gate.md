# Jurisdiction gate

Run this before stating any requirement that depends on state law. Cannabis rules are state-specific, change often, and differ even between two Metrc states.

## The five facts to pin down

| # | Fact | Why it matters | If unknown |
|---|---|---|---|
| 1 | **State** (and city/county if local rules apply) | Every rule is state law | Ask. Never infer from a phone number, product name, or currency. |
| 2 | **License type(s)** (e.g. cultivation tier, manufacturer type, distributor/transporter, retailer, microbusiness, medical vs. adult-use) | Obligations attach to license type | Ask. A vertically integrated operator may hold several. Treat each separately. |
| 3 | **Activity in question** (harvest, packaging, transfer, waste, sale, adjustment) | Narrows which rules apply | Infer from the request and confirm in one line |
| 4 | **Traceability system** (Metrc, BioTrack, state-built, other) | Field names, reason codes, and workflows differ | Look it up in `state-profiles.md`. If it's marked UNVERIFIED or the state is missing, ask. |
| 5 | **Rule citation and effective/verified date** | Rules change; an outdated rule is a wrong answer | Cite from `state-profiles.md` or the user's documents only. Otherwise mark `NEEDS VERIFICATION`. |

Ask for all missing facts in **one** combined question, not a drip of clarifications. If the user wants to proceed without them, continue the operational analysis (math, discrepancies, checklists). Leave every rule-dependent item as `NEEDS VERIFICATION`, and don't fill one in with a rule from another state.

## Jurisdiction block (print at the top of every state-dependent output)

```
JURISDICTION
State: ___   License type(s): ___   Activity: ___
Traceability system: ___ (source: ___, verified ___)
Rules relied on: [citation + URL + verified date] | none — see NEEDS VERIFICATION items
```

## Hard rules

- Never state a deadline, threshold, reason code, hold period, or reporting obligation unless it's cited from a primary source read in this session, from `state-profiles.md` with its verification label (V (LII) is a secondary source and must be labelled so), or from the operator's own documents.
- Never carry a rule from one state into another, even when both use Metrc.
- A rule summarized from memory is an assumption and gets labeled that way.
- Recommend compliance or legal review for anything that would be submitted to a regulator or the traceability system.
