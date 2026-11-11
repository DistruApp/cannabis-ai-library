# Gate 3 fact-check: NY, IL, OK (medical), federal

Checked 2026-11-11. Read-only review; no repo file was edited.

**Library files compared:** `skills/cannabiz-skills/compliance/cannabis-state-rules-lookup/references/state-profiles.md` (header, NY, IL, OK sections; NY/IL/OK are not in the "Other states" table) and the "Federal status" bullet in `cannabis-state-rules-lookup/SKILL.md`. The same `state-profiles.md` is copied byte-for-byte into `cannabis-traceability-reconciliation`, `cannabis-transfer-manifest-precheck` and `cannabis-inspection-readiness`, so **every fix below has to land in all four copies**. A grep of `skills/` and `docs/` found no other NY, IL, OK or federal citations: no `NYCRR`, `ILCS`, `Ill. Adm. Code` or `442:10` anywhere.

**Method:** Step 1 answers were built from primary sources before the library was opened. Sources:
- **NY:** OCM's Metrc implementation plan PDF and STS Bulletin 18, both on cannabis.ny.gov, plus 9 NYCRR Part 125 via the Cornell LII copy. That copy is secondary text, and its history note says "eff. 9/27/2023" with no later amendment shown.
- **IL:** 68 Ill. Adm. Code 1291 and 8 Ill. Adm. Code 1300 via Cornell LII, and 410 ILCS 705 via FindLaw. FindLaw is secondary and not on the approved list. ilga.gov refused connections (ECONNREFUSED) and cannabis.illinois.gov did not resolve (ENOTFOUND), so both are **BLOCKED**.
- **OK:** OMMA's own "Emergency Rules Effective August 28, 2026" PDF, the full Title 442 text, which the rules page marks CURRENT RULES. I downloaded it and read it directly.
- **Federal:** the federalregister.gov API for metadata and govinfo.gov PDFs for full text. The federalregister.gov HTML pages are bot-blocked.

## Summary table

Key: MATCH, OMISSION, CONFLICT, PROFILE-UNVERIFIED-OK, COULDN'T-VERIFY. "→V" means an item the profile marks UNVERIFIED can now be verified.

| Q | New York | Illinois | Oklahoma (medical) |
|---|---|---|---|
| Q1 system / recording speed | System MATCH. Go-live date CONFLICT (P2): retail was 2026-01-12, not 2025-12-17. Recording speed OMISSION (P1): real-time; nursery/cultivation activities within 3 calendar days. | System MATCH (the IB-2025-03 quote couldn't be checked: BLOCKED). Recording speed OMISSION (P1): dispensary sales "at the time of sale"; IDOA Subpart K (eff. 2026-05-01) is COULDN'T-VERIFY. | System MATCH. Recording speed OMISSION (P1): "real time or after each individual sale". |
| Q2 reconciliation frequency | OMISSION (P1): monthly audit plus annual audit | OMISSION (P1): dispensary daily reconciliation and daily count (bulk monthly); cultivation center weekly physical inventory | OMISSION (P1): daily, at close of business |
| Q3 "significant" threshold | **OMISSION (P0):** 2% or 5% of *anticipated inventory*, tiered by license type | OMISSION (P2): no % threshold; rules use "imbalance" | OMISSION (P2): no threshold defined |
| Q4 notifications | **OMISSION (P0):** OCM within 24 h for a significant discrepancy; OCM within 24 h for theft, loss or diversion; incident report within 10 calendar days confirming law enforcement was notified | **OMISSION (P0):** dispensary theft: IDFPR and ISP in writing within 24 h. Dispensary error: tell IDFPR immediately if the cause isn't found in 2 calendar days; finish the investigation in 10 business days. Cultivation center: local police, ISP and IDOA within 24 h, by phone or in person. | **OMISSION (P0):** OMMA and law enforcement immediately, no later than 24 h, with a signed statement. Unaccounted Metrc tags: 48 h. |
| Q5 adjustments / corrections | OMISSION (P1): adjustments recorded in real time; outage backlog entered within 3 calendar days; OCM transfer-variance procedure. Data-entry correction deadline: COULDN'T-VERIFY (none found). | **OMISSION (P0):** dispensaries need IDFPR approval *before* any inventory adjustment, plus a detailed reason; keep the documents 2 years | OMISSION (P1): no adjustment-reason rule found; outage backlog "immediately"; out-of-control outage halts business |
| Q6 manifest / testing | OMISSION (P1): manifest contents, and a COA must accompany product to retail. →V: Retail Item ID (2026-02-28) and TestPassed/RetestPassed before distributor→dispensary transfer (2026-03-31) | OMISSION (P1): manifest built in Metrc before transfer, copy in the vehicle; dispensary checks manifest on receipt; product must pass testing before sale. Subpart K text COULDN'T-VERIFY. | OMISSION (P1): manifest contents, copies, no alteration after departure, receiver must refuse product without a manifest; no transfer to a dispensary until final-product testing |
| Q7 retention | OMISSION (P1): 5 years | OMISSION (P1): dispensary 5 years (adjustment documents 2 years); cultivation 5 years | OMISSION (P1): 7 years |
| Q8 waste / destruction | OMISSION (P1): weigh and enter in Metrc before mixing; 50% non-cannabis mix; 2 witnesses; 5 years | **OMISSION (P0):** cultivation, craft grow and infuser: 7 days' notice to IDOA and ISP. Dispensary: entered in the State Verification System first, on video, schedule changes 3 business days ahead, 5 years. | **OMISSION (P0):** waste to a licensed waste facility within 90 days; waste packages tagged and reported; plant-part disposal log kept 7 years |
| Q9 worker credential | OMISSION (P1): licensee-issued ID badge displayed at all times | OMISSION (P1): state agent ID card visible at all times | OMISSION (P1): state employee credential before employment, worn or displayed; transporter agent license carried |
| Other | Profile marks the Feb–Mar 2026 milestones UNVERIFIED → now V | Missing pointer (P1): IDOA rule update effective 2026-05-01 (new Subpart K). Cornell copies of Part 1300 predate it. | Pending change OMISSION (P2): proposed permanent rules, comments 2026-11-02 to 2026-12-08. "HB3143" attribution COULDN'T-VERIFY. |

**Federal, in SKILL.md:** CONFLICT/understatement (P1). FR 2026-08176 puts in Schedule III not only FDA-approved products but also marijuana "subject to a state medical marijuana license" (new 21 CFR 1308.13(g)(2)–(5)). OMISSION (P1): FR 2026-08177, a DEA hearing on general rescheduling that began 2026-06-29, and FR 2026-08178, which withdrew the 2024 hearing. Through 2026-11-10 the Federal Register has no final rule on general rescheduling.

**Freshness:** The profile header says "Last reviewed 2026-10-16", 26 days before 2026-11-11, so it is within 90 days. Dates older than 90 days in the sections reviewed:
- NY's "2025-12-17" is historical and is also wrong for retail.
- IL's IB-2025-03 "July 1" refers to 2025 and is historical.

**Quotes not found verbatim:**
- IL: "July 1: Metrc becomes the official cannabis inventory tracking system for Illinois." (IB-2025-03). Couldn't check: cannabis.illinois.gov is BLOCKED. A human should open https://cannabis.illinois.gov/research-and-data/seed-to-sale-tracking.html.
- The NY and OK sections and the federal bullet contain no quotes.

---

## Step 1 answers (primary sources)

### New York (adult use)
- **Q1, system:** OCM's Metrc implementation plan ("Welcome to Metrc" packet at https://cannabis.ny.gov/metrc-nys-implementation-plan, served as a PDF) gives these dates:
  - Non-retail: "December 17 … All existing inventory must be in the Metrc system."
  - Dispensary: "January 12, 2026 (new date) • All existing inventory must be in the Metrc system. … • Must start reporting sales to Metrc."
  - Also "Metrc closes external transfer process for all license types" at 12/17.
  - Confidence: high.
- **Q1, speed:** 9 NYCRR 125.8(a): "Licensees shall track all physical inventory of cannabis in an electronic real-time inventory tracking system". 125.8(a)(8)(i), nursery and cultivation: "record the following activities in the inventory tracking system within three (3) calendar days of occurrence". Source: Cornell LII, https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.8, eff. 2023-09-27. Confidence: high.
- **Q2:** 125.8(d)(2): "conducting a monthly inventory audit of all cannabis and cannabis products", plus an annual audit. Confidence: high.
- **Q3:** 125.8(e) thresholds, all measured against *anticipated inventory*:
  - 2% for cooperatives, Tier 3–5 cultivators, ROD and ROND.
  - Retail dispensary, delivery and on-site consumption: "five (5) percent of the anticipated inventory or greater" where the system anticipated 1,000 products or fewer, and 2% "if the inventory tracking system anticipated an inventory of more than 1,000 cannabis products".
  - Nursery, Tier 1–2 cultivators, distributors, processors and microbusinesses: 5%, or 2% if the licensee also holds a 2%-tier license.
  - Confidence: high on structure. The tier list is paraphrased.
- **Q4:**
  - 125.8(e): "shall notify the Office no later than twenty-four (24) hours after discovery of the event", in a manner the Office prescribes.
  - 125.3(e): the Office must be notified "immediately and, in no instance, more than twenty-four (24) hours following discovery" of incidents that include "diversion, theft, or loss of any cannabis or cannabis product". The licensee must then file an incident report "within ten (10) calendar days of any incident", which must include "confirmation that the appropriate law enforcement authorities were notified". Incident records are kept "not less than five (5) years or the duration of an open investigation, whichever is longer."
  - Source: https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.3, eff. 2023-09-27. Confidence: high.
- **Q5:**
  - 125.8(a)(2)(ii) requires real-time records of "a complete cannabis and cannabis product inventory, as well as inventory adjustments".
  - 125.8(b)(4) covers loss of system access: "Within three (3) calendar days of restored access, enter all licensed cannabis activity that occurred during the loss of access". Under 125.8(b)(3), no transport, receipt, transfer or delivery is allowed until access is restored.
  - OCM STS Bulletin 18 (2026-04-27, https://cannabis.ny.gov/system/files/documents/2026/04/sts-bulletin-18.pdf): when a package is short, a licensee "may accept the full package and adjust the quantity in Metrc using the entry error action reason". Also: "If the variance between the shipped and received quantity exceeds 5%, it will be flagged in Metrc."
  - No regulatory deadline for correcting data-entry errors was found: COULDN'T-VERIFY.
  - Confidence: high for what was found.
- **Q6:**
  - 125.10(g)(1)–(2): the manifest is generated "Prior to transporting any cannabis or cannabis products". At minimum it lists the originator, lot, recipient, unique IDs, product name, type and quantity, departure and arrival times, and driver and vehicle details.
  - 125.10(g)(3): for products going to retail licensees, "a certificate of analysis shall accompany cannabis products".
  - OCM Metrc plan: by 2026-02-28, "Any finished good products leaving a distribution facility to transfer to a dispensary MUST have Retail Item ID QR code on each unit". By 2026-03-31 they must also have "A 'TestPassed' or 'RetestPassed' testing status associated to each package prior to transfer."
  - Source: https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.10. Confidence: high.
- **Q7:**
  - 125.13(a): keep records "for at least five (5) years from the date of creation".
  - 125.10(g)(11): manifests and invoices are kept "for a period of five (5) years".
  - Source: https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.13. Confidence: high.
- **Q8:** 125.11(j): "All cannabis waste disposed of shall be weighed, recorded, and entered into the inventory tracking system prior to mixing and disposal." Also from 125.11:
  - (c): waste is ground and mixed so it is "at least 50% non-cannabis waste by weight".
  - (j)(4): two employee witnesses.
  - Disposal records are kept 5 years.
  - No advance notice to OCM was found.
  - Source: https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.11. Confidence: high.
- **Q9:** 125.3(d)(1): licensees and employees must "hold and properly display an identification badge, issued by the licensee, at all times" on the premises. 125.4 has no state-issued worker permit. Confidence: high.

### Illinois (adult use; agency depends on license type)
- **Q1:** Metrc. I couldn't open state pages: cannabis.illinois.gov is BLOCKED (ENOTFOUND) and ilga.gov is BLOCKED (ECONNREFUSED).
  - Dispensary: 68 IAC 1291.310(b)(1): "Each sales transaction at the time of sale". Source: https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-68-SS-1291.310, added 48 Ill. Reg. 13377, eff. 2024-08-20.
  - IDOA: new Subpart K, "Cannabis Plant Monitoring System" (8 IAC 1300.1000–1300.1050), adopted at 50 Ill. Reg. 7050, eff. 2026-05-01, per JCAR's Flinn Report as seen in search results. Search snippets of 1300.1030 and 1300.1000 say activities are recorded "upon completion of the activity" and tags are recorded "within three calendar days of receipt". I couldn't read the text verbatim: COULDN'T-VERIFY. A human should open https://www.ilga.gov/agencies/JCAR/EntirePart?titlepart=00801300.
- **Q2:**
  - Dispensary: 1291.310(e): "An AIC shall conduct a daily physical count of all inventory". Bulk "must be counted monthly". Statute 410 ILCS 705/15-75(d), via FindLaw: "The agent-in-charge shall conduct daily inventory reconciliation."
  - Cultivation center: 8 IAC 1300.180(b): "Upon commencing business, each cultivation center shall conduct a physical weekly inventory of cannabis stock." That text is from the pre-2026-05-01 Cornell version. 410 ILCS 705/20-30(a), via FindLaw, says "physical inventory recorded weekly".
  - Confidence: high for the dispensary rules; medium for cultivation, since the text may have changed on 2026-05-01.
- **Q3:** no percentage threshold. The rules use "imbalance". Confidence: high.
- **Q4:**
  - Dispensary theft: 1291.310(e)(3): "Within 24 hours after the first discovery of the reduction due to theft, criminal activity or suspected criminal activity … the dispensing organization shall inform the Department and ISP in writing."
  - Dispensary error, 1291.310(e)(2): if the dispensary "cannot identify the reason for the mistake within two calendar days", it "shall inform the Department immediately in writing of the imbalance and the corrective action taken to date". "The dispensing organization shall complete its investigation within 10 business days."
  - Cultivation center: 410 ILCS 705/20-30(h), via FindLaw: "within 24 hours of the discovery of any loss or theft", notify "local law enforcement, the Illinois State Police, and the Department of Agriculture". "Notification shall be made by phone or in person". Craft grower and infuser equivalents were not checked.
  - Confidence: high (dispensary, Cornell); medium (cultivation, FindLaw only).
- **Q5:** 1291.310(e)(1): "A dispensing organization must receive Department approval prior to completing an inventory adjustment." It "shall provide a detailed reason for the adjustment". "Inventory adjustment documentation must be kept at the dispensary for two years from the date performed." No IDOA adjustment rule was verified. Confidence: high (dispensary).
- **Q6:**
  - 1291.310(d): "Upon cannabis delivery, a dispensing organization shall confirm the product's name" and other manifest details against the label and package.
  - 8 IAC 1300.1040 (eff. 2026-05-01; search-snippet text only, UNVERIFIED): the manifest is prepared "through the cannabis plant monitoring system, prior to transferring".
  - 410 ILCS 705/40-25(k): a manifest "shall be present in any vehicle transporting cannabis". This was quoted inside a search result, so it is UNVERIFIED.
  - Testing: 8 IAC 1300.700(e): "must pass all testing requirements before offered for sale to the public". Source: https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-8-SS-1300.700, eff. 2020-06-03.
  - Confidence: medium.
- **Q7:** dispensary records: 410 ILCS 705/15-75(e)(1), FindLaw, "5 years from the date on the document". Adjustment documentation: 2 years under 1291.310(e)(1). Cultivation: 8 IAC 1300.155(a) "for a 5-year period". Confidence: medium-high.
- **Q8:**
  - Cultivation center, craft grower and infuser, 8 IAC 1300.810(b): "shall provide the Department and ISP a minimum of 7 days' notice prior to rendering the product unusable". IDOA may hold product up to 7 days or send a witness. Source: https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-8-SS-1300.810, eff. 2020-06-03; it may have been amended on 2026-05-01.
  - Dispensary, 68 IAC 1291.325:
    - (b) "shall notify the Department and ISP of this day and time at the initial registration inspection", and changes need notice "at least three business days before the implementation".
    - (e) flower is "entered into the State Verification System prior to rendering it unusable", "conducted under video surveillance".
    - (f) "Electronic documentation of destruction and disposal shall be maintained for a period of at least five years."
  - Confidence: high.
- **Q9:** 410 ILCS 705/15-40(b), via FindLaw: "A dispensing organization agent must keep his or her identification card visible at all times when in the dispensary." 8 IAC 1300.165(g): "A cultivation center agent must keep his or her ID card visible at all times when on the property of a cultivation center." Confidence: high.

### Oklahoma (medical only)
Source for this section: the OMMA "EMERGENCY RULES EFFECTIVE AUGUST 28, 2026" PDF, https://oklahoma.gov/content/dam/ok/en/omma/content/rulemaking-process/rules/2026-8-28/August%2028%202026%20Emergency%20Rules.pdf. The rules page marks it "CURRENT RULES". Confidence for all answers: high.
- **Q1:** "OMMA uses Metrc for the statewide seed-to-sale inventory tracking system" (https://oklahoma.gov/omma/businesses/seed-to-sale.html). OAC 442:10-5-6(d): licensees "must ensure all information is reported to the Authority accurately and in real time or after each individual sale". 442:10-5-6(f)(1): "track, update, and report inventory after each individual transaction, transfer, or sale".
- **Q2:** 442:10-5-6(f)(2): "All commercial licensees must ensure all on-premises and in-transit medical marijuana and medical marijuana product inventories are reconciled each day in the State inventory tracking system at the close of business, if not already done."
- **Q3:** none defined.
- **Q4:**
  - 442:10-5-13: "the commercial licensee shall notify immediately the Authority and law enforcement." The notice is a signed statement "attaching and submitting electronically", and "The notice shall be provided no later than twenty-four hours after discovery of the event."
  - Tags, 442:10-5-6(f)(3)(B): "If a commercial licensee is unable to account for unused inventory tracking system tags, the commercial licensee must report to the Authority and the State inventory tracking system vendor within forty-eight (48) hours."
  - Monthly report due by the 15th (5-6(a)). Submitting through Metrc satisfies it (5-6(a)(4)).
- **Q5:** no adjustment-reason or correction-deadline rule was found in Chapter 10. Rules that do apply:
  - Replacement tags must be "properly reflected in the State inventory tracking system" (5-6(f)(3)(G)).
  - Outage, 5-6(h): activity during the outage "must be immediately entered". If the outage is within the licensee's control, it "may not perform any business activities" until reporting resumes.
- **Q6:**
  - 442:10-3-6(b)(1)–(8) sets manifest contents.
  - (c) "A separate inventory manifest shall be prepared for each licensee receiving".
  - (g) the manifest may not be altered after departure, except for receiver signatures and rejections.
  - (h) "A receiving licensee shall refuse to accept any medical marijuana or medical marijuana products that are not accompanied by an inventory manifest."
  - Testing, 442:10-8-1(d): "Growers, processors, and dispensaries shall not sell or otherwise transfer any final harvest batch or final product to a dispensary until the product has undergone final product testing."
- **Q7:** 442:10-5-6(b): "all records shall be maintained for at least seven (7) years from the date of creation". Manifests: 3-6(f), 7 years.
- **Q8:**
  - 442:10-5-6(f)(8): "All packages of medical marijuana waste shall have an inventory tracking system tag affixed and the contents of the waste package shall be reported in the State inventory tracking system."
  - 442:10-9-9(a): "Commercial licensees shall transfer medical marijuana waste to a medical marijuana waste facility for disposal within ninety (90) days."
  - 442:10-5-10(b): on-site disposal of root balls, stems and similar plant parts requires a signed disposal log, kept 7 years.
- **Q9:**
  - Employee credential, 442:10-5-1.1: "A medical marijuana business license holder shall require all individuals employed under their license to have an active, unexpired credential prior to employment". The credential is "to be worn or displayed on their person during the employee's hours of work."
  - Transporters, 442:10-3-5(b): the agent "shall carry the transporter agent license … at all times during transportation".
- **Pending change:** proposed permanent rules (Chapters 1 and 10), "begins Monday, Nov. 2, and closes at 5 p.m. on Tuesday, Dec. 8, 2026". Hearing: Dec. 8, 9 a.m., State Capitol Room 535. Source: https://oklahoma.gov/omma/rules-and-legislation/public-comment.html.

### Federal
- **FR 2026-08176** (91 FR 22714), published 2026-04-28. Final rule; final order of the Acting Attorney General (AG Order No. 6754-2026). "Effective April 28, 2026."
  - It amends 21 CFR 1308.13(g) to add "(2) Marijuana, as defined in 21 U.S.C. 802(16), in a U.S. Food and Drug Administration approved product or subject to a state medical marijuana license", and parallel entries for extract and THC.
  - Preamble: "I am hereby ordering that FDA-approved drug products containing marijuana, as well marijuana in any form covered by a state medical marijuana license, be placed in schedule III of the CSA."
  - Everything else stays in Schedule I: "any form of marijuana other than in an FDA-approved drug product or marijuana subject to a state medical marijuana license remains a schedule I controlled substance".
  - It adds an expedited registration under 21 CFR part 1301. "any applicant that submits an application within 60 days of the publication of this rule … may engage in the manufacture, distribution, and/or dispensing … in conformity with a state-issued license during the pendency of the application."
  - On tax: "Nothing in this rule constitutes a determination regarding federal tax liability".
  - Sources: https://www.federalregister.gov/documents/2026/04/28/2026-08176/ and https://www.govinfo.gov/content/pkg/FR-2026-04-28/pdf/2026-08176.pdf. Confidence: high.
- **FR 2026-08177** (Docket DEA-1362), published 2026-04-28. Notice of hearing on the May 2024 proposed rule to reschedule marijuana generally.
  - "The hearing will commence on June 29, 2026, at 9 a.m." Notices of participation were due "on or before May 28, 2026".
  - A companion notice, FR 2026-08178, withdrew the 2024 hearing notice (89 FR 70148) and terminated those proceedings.
  - A Federal Register API search on 2026-11-11 (DEA, "marijuana", published since 2026-04-01) found no final rule on general rescheduling through 2026-11-10.
  - Sources: https://www.federalregister.gov/documents/2026/04/28/2026-08177/ and https://www.govinfo.gov/content/pkg/FR-2026-04-28/pdf/2026-08177.pdf. Confidence: high.

---

## Findings and proposed profile text

Proposed text follows the profile's own style and labels. **V** means confirmed on the regulator's own page or document. **V (Cornell LII copy)** marks the secondary text the brief allows. **UNVERIFIED** marks text seen only through FindLaw or a search snippet.

### P0

**P0-1 · NY Q3/Q4: significant-discrepancy threshold and both 24-hour notices are missing.**
Proposed addition under `### New York (NY)`:
> - **Rules relevant to Wave 1 skills** (V, Cornell LII copy of 9 NYCRR Part 125, eff. 2023-09-27; checked 2026-11-11. Confirm there are no later amendments on the official NYCRR):
>   - **§125.8(d), Audits:** "conducting a monthly inventory audit of all cannabis and cannabis products", plus an annual audit.
>   - **§125.8(e), Significant discrepancy, 24-hour notice:** "shall notify the Office no later than twenty-four (24) hours after discovery of the event". The threshold is measured against *anticipated inventory* and depends on license type. It is 2% for cooperatives, Tier 3–5 cultivators, ROD and ROND. Retail dispensaries, delivery and on-site consumption use "five (5) percent of the anticipated inventory or greater" when the system anticipated 1,000 products or fewer, and 2% above 1,000. Nurseries, Tier 1–2 cultivators, distributors, processors and microbusinesses use 5% (2% if the licensee also holds a 2%-tier license). *The rule doesn't say whether this is measured by weight, count or package. Present the readings; don't pick one.*
>   - **§125.3(e), Theft, loss or diversion:** notify OCM "immediately and, in no instance, more than twenty-four (24) hours following discovery" of incidents that include "diversion, theft, or loss of any cannabis or cannabis product". **Separately**, file an incident report "within ten (10) calendar days of any incident" that includes "confirmation that the appropriate law enforcement authorities were notified." Always state both deadlines.

Sources: https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.8 and https://www.law.cornell.edu/regulations/new-york/9-NYCRR-125.3

**P0-2 · IL Q4: 24-hour theft notice, 2-day and 10-day error deadlines, and cultivation-center notice are missing.**
Proposed addition under `### Illinois (IL)`:
> - **Dispensaries (IDFPR), 68 Ill. Adm. Code 1291.310** (V, Cornell LII copy, eff. 2024-08-20; checked 2026-11-11):
>   - **(e), daily count:** "An AIC shall conduct a daily physical count of all inventory". Bulk "must be counted monthly".
>   - **(e)(3), theft or criminal activity:** "Within 24 hours after the first discovery of the reduction due to theft, criminal activity or suspected criminal activity … the dispensing organization shall inform the Department and ISP in writing."
>   - **(e)(2), imbalance from a mistake:** if it "cannot identify the reason for the mistake within two calendar days", it "shall inform the Department immediately in writing". "The dispensing organization shall complete its investigation within 10 business days."
> - **Cultivation centers (IDOA), 410 ILCS 705/20-30(h)** (UNVERIFIED: seen on FindLaw; ilga.gov was unreachable on 2026-11-11): "within 24 hours of the discovery of any loss or theft", notify "local law enforcement, the Illinois State Police, and the Department of Agriculture". "Notification shall be made by phone or in person". Craft-grower and infuser equivalents are UNVERIFIED.

**P0-3 · IL Q5: dispensary adjustments need IDFPR approval first.**
> - **1291.310(e)(1), adjustments:** "A dispensing organization must receive Department approval prior to completing an inventory adjustment." It must give "a detailed reason for the adjustment". "Inventory adjustment documentation must be kept at the dispensary for two years from the date performed." (V, Cornell LII copy.) **Don't tell an IL dispensary to post a Metrc adjustment before it has approval.**

**P0-4 · IL Q8: 7-day destruction notice (IDOA licensees) and dispensary destruction rules.**
> - **Destruction, IDOA licensees, 8 Ill. Adm. Code 1300.810(b):** "shall provide the Department and ISP a minimum of 7 days' notice prior to rendering the product unusable". (V, Cornell LII copy, eff. 2020-06-03. Part 1300 was amended effective 2026-05-01, so NEEDS VERIFICATION against the current text.)
> - **Destruction, dispensaries, 68 Ill. Adm. Code 1291.325:** the destruction day and time are given to the Department and ISP at the initial inspection, and changes need notice "at least three business days before the implementation". Flower must be "entered into the State Verification System prior to rendering it unusable", "conducted under video surveillance". Records: "at least five years." (V, Cornell LII copy, eff. 2024-08-20.)

**P0-5 · OK Q4: 24-hour loss/theft notice and 48-hour tag notice.**
Proposed addition under `### Oklahoma (OK), medical only`:
> - **Rules relevant to Wave 1 skills** (V, OMMA "Emergency Rules Effective August 28, 2026" PDF, marked CURRENT RULES; checked 2026-11-11):
>   - **OAC 442:10-5-13, Loss and theft:** "the commercial licensee shall notify immediately the Authority and law enforcement", by an electronically submitted signed statement. "The notice shall be provided no later than twenty-four hours after discovery of the event."
>   - **OAC 442:10-5-6(f)(3)(B), tags:** "If a commercial licensee is unable to account for unused inventory tracking system tags, the commercial licensee must report to the Authority and the State inventory tracking system vendor within forty-eight (48) hours."

**P0-6 · OK Q8: 90-day waste transfer deadline.**
> - **OAC 442:10-9-9(a):** "Commercial licensees shall transfer medical marijuana waste to a medical marijuana waste facility for disposal within ninety (90) days."
> - **OAC 442:10-5-6(f)(8):** "All packages of medical marijuana waste shall have an inventory tracking system tag affixed and the contents of the waste package shall be reported in the State inventory tracking system."

Source: https://oklahoma.gov/content/dam/ok/en/omma/content/rulemaking-process/rules/2026-8-28/August%2028%202026%20Emergency%20Rules.pdf

### P1

**P1-1 · Federal bullet in SKILL.md understates FR 2026-08176 and omits the pending hearing.** Proposed replacement:
> - **Federal status.** As of 2026-11-11, FR Doc 2026-08176 (91 FR 22714, effective 2026-04-28) placed in Schedule III marijuana "in a U.S. Food and Drug Administration approved product **or subject to a state medical marijuana license**" (21 CFR 1308.13(g)(2)). It also created an expedited DEA registration path for state medical licensees under 21 CFR part 1301. Adult-use and other unlicensed marijuana stays in Schedule I: "any form of marijuana other than in an FDA-approved drug product or marijuana subject to a state medical marijuana license remains a schedule I controlled substance". General rescheduling is still pending. FR Doc 2026-08177 (Docket DEA-1362) noticed a DEA hearing starting 2026-06-29, and no final rule had appeared in the Federal Register as of 2026-11-10. (V, federalregister.gov / govinfo.) Whether DEA registration applies to an operator, and how any of this affects 280E, are **counsel and CPA questions**. The rule itself says "Nothing in this rule constitutes a determination regarding federal tax liability". Never say 280E does or doesn't apply to them.

This matters most for OK, which is medical-only and squarely within "state medical marijuana license". NY and IL adult-use activity is not covered.

**P1-2 · NY Q1/Q5/Q6/Q7/Q8/Q9: recording speed, adjustments, outage, manifest/COA, retention, waste, badge.**
> - **§125.8(a):** "electronic real-time inventory tracking system"; inventory "as well as inventory adjustments" recorded in real time. **§125.8(a)(8):** nursery and cultivation activities "within three (3) calendar days of occurrence". **§125.8(b)(4):** after an outage, "Within three (3) calendar days of restored access, enter all licensed cannabis activity". No transfers until access is restored.
> - **§125.10(g):** the manifest is generated "Prior to transporting". For product going to retail licensees, "a certificate of analysis shall accompany cannabis products". Manifests are kept "for a period of five (5) years".
> - **§125.13(a):** records are kept "for at least five (5) years from the date of creation".
> - **§125.11(j):** "All cannabis waste disposed of shall be weighed, recorded, and entered into the inventory tracking system prior to mixing and disposal." Waste is mixed so it is at least 50% non-cannabis, two employees witness, and records are kept 5 years.
> - **§125.3(d)(1):** each employee must "hold and properly display an identification badge, issued by the licensee, at all times".
> - **Transfer variances (OCM STS Bulletin 18, 2026-04-27, V):** if a package is short, the receiver "may accept the full package and adjust the quantity in Metrc using the entry error action reason". "If the variance between the shipped and received quantity exceeds 5%, it will be flagged in Metrc." https://cannabis.ny.gov/system/files/documents/2026/04/sts-bulletin-18.pdf

**P1-3 · NY Q6: the UNVERIFIED Metrc milestones can now be verified.** Replace the "Later dates … UNVERIFIED" sentence with:
> OCM's Metrc implementation plan (V, https://cannabis.ny.gov/metrc-nys-implementation-plan, checked 2026-11-11): non-retail licensees had to have "All existing inventory … in the Metrc system" by 2025-12-17; dispensaries by "January 12, 2026 (new date)", when they also had to "start reporting sales to Metrc". From 2026-02-28, finished goods sent from a distributor to a dispensary "MUST have Retail Item ID QR code on each unit". From 2026-03-31 they must also carry "A 'TestPassed' or 'RetestPassed' testing status associated to each package prior to transfer." C.O.D. reporting is not covered by this document and stays UNVERIFIED.

This also fixes the P2 conflict "integration deadline for all licensees was 2025-12-17".

**P1-4 · IL Q1/Q2/Q6/Q7/Q9 and the 2026-05-01 IDOA rule change.**
> - **IDOA rule update:** Part 1300 was amended effective 2026-05-01 (50 Ill. Reg. 7050), adding Subpart K, "Cannabis Plant Monitoring System" (§§1300.1000–1300.1050: tagging, reporting, transfer/manifest, loss of access and reconciliation). The section text is UNVERIFIED: ilga.gov could not be reached on 2026-11-11. Treat every IDOA timing requirement as NEEDS VERIFICATION, and don't rely on Cornell copies of Part 1300 dated before 2026-05-01.
> - **Dispensary recording:** 1291.310(b)(1): "Each sales transaction at the time of sale" (V, Cornell LII copy). Daily reconciliation, 410 ILCS 705/15-75(d): "The agent-in-charge shall conduct daily inventory reconciliation." (UNVERIFIED, FindLaw.)
> - **Cultivation inventory:** 8 IAC 1300.180(b), "a physical weekly inventory of cannabis stock" (V, Cornell LII copy, pre-2026-05-01 text; NEEDS VERIFICATION).
> - **Receiving:** 1291.310(d): "Upon cannabis delivery, a dispensing organization shall confirm the product's name" and the other manifest details against the package (V, Cornell LII copy).
> - **Testing:** 8 IAC 1300.700(e): "must pass all testing requirements before offered for sale to the public" (V, Cornell LII copy, eff. 2020-06-03).
> - **Retention:** dispensary records 5 years (410 ILCS 705/15-75(e)(1), UNVERIFIED, FindLaw); adjustment documents 2 years (1291.310(e)(1), V); cultivation 5 years (8 IAC 1300.155(a), V, Cornell LII copy).
> - **Agent ID:** "A dispensing organization agent must keep his or her identification card visible at all times when in the dispensary." (410 ILCS 705/15-40(b), UNVERIFIED, FindLaw.) "A cultivation center agent must keep his or her ID card visible at all times when on the property of a cultivation center." (8 IAC 1300.165(g), V, Cornell LII copy.)

**P1-5 · OK Q1/Q2/Q5/Q6/Q7/Q9.**
> - **OAC 442:10-5-6(d), (f)(1):** report "accurately and in real time or after each individual sale". Track, update and report "after each individual transaction, transfer, or sale".
> - **OAC 442:10-5-6(f)(2), daily reconciliation:** "All commercial licensees must ensure all on-premises and in-transit medical marijuana and medical marijuana product inventories are reconciled each day in the State inventory tracking system at the close of business, if not already done."
> - **OAC 442:10-5-6(h), outage:** activity during the outage "must be immediately entered". If the outage is within the licensee's control, it "may not perform any business activities" that must be reported until access is restored.
> - **Adjustments:** Chapter 10 sets no adjustment-reason list or correction deadline. Get reasons from the operator's Metrc account.
> - **OAC 442:10-3-6, manifests:** contents are listed in (b)(1)–(8). "A separate inventory manifest shall be prepared for each licensee receiving". The manifest may not be altered after departure except as listed in (g). "A receiving licensee shall refuse to accept any medical marijuana or medical marijuana products that are not accompanied by an inventory manifest."
> - **OAC 442:10-8-1(d), testing:** "Growers, processors, and dispensaries shall not sell or otherwise transfer any final harvest batch or final product to a dispensary until the product has undergone final product testing."
> - **Retention:** "all records shall be maintained for at least seven (7) years from the date of creation" (5-6(b)); manifests also 7 years (3-6(f)).
> - **Workers, OAC 442:10-5-1.1:** "A medical marijuana business license holder shall require all individuals employed under their license to have an active, unexpired credential prior to employment". The credential is "to be worn or displayed on their person during the employee's hours of work." Transporter agents "shall carry the transporter agent license" (3-5(b)).

### P2
- **P2-1, NY:** "integration deadline for all licensees was 2025-12-17" is wrong for dispensaries (2026-01-12). P1-3 fixes it.
- **P2-2, IL/OK Q3:** add one line to each: "No percentage 'significant discrepancy' threshold is defined. Don't import another state's 2% or 5%."
- **P2-3, OK pending change:** add "**Pending change:** proposed permanent rules (Chapters 1 and 10) are open for comment from 2026-11-02 to 2026-12-08, with a hearing on 2026-12-08 (V, https://oklahoma.gov/omma/rules-and-legislation/public-comment.html). Re-check the cited sections after adoption."
- **P2-4, OK:** "Emergency rules took effect 2026-08-28" is V. The "(HB3143)" attribution is COULDN'T-VERIFY: the rules PDF didn't name it and I didn't check the legislature. Mark it UNVERIFIED or drop it.
- **P2-5, IL:** the IB-2025-03 quote was not found verbatim because cannabis.illinois.gov is BLOCKED (DNS failure from this environment). A human should open https://cannabis.illinois.gov/research-and-data/seed-to-sale-tracking.html. The fact itself (Metrc replaced BioTrack, mid-2025) is corroborated by Metrc and secondary sources.
- **P2-6, all four copies:** apply every change to all four identical `references/state-profiles.md` files.

## Couldn't verify, and URLs for a human
- ilga.gov (ECONNREFUSED):
  - 8 IAC 1300 Subpart K: https://www.ilga.gov/agencies/JCAR/EntirePart?titlepart=00801300
  - 410 ILCS 705/15-75: https://www.ilga.gov/legislation/ilcs/documents/041007050K15-75.htm
  - 20-30: https://www.ilga.gov/legislation/ilcs/documents/041007050K20-30.htm
- cannabis.illinois.gov (ENOTFOUND): the IB-2025-03 bulletin and the IDOA Spring 2026 rule-update bulletin, https://cannabis.illinois.gov/content/dam/soi/en/web/cannabis/documents/idoa/informational-bulletin-crta-rule-update-summary.pdf
- Illinois Register, 50 Ill. Reg. 7050 (ilsos.gov returned 403).
- NY: no data-entry correction deadline was found in Part 125. The current official NYCRR text (Westlaw/DOS) should confirm there have been no post-2023 amendments to 125.3, 125.8, 125.10, 125.11 and 125.13.
- OK: the credential statute, 63 O.S. §427.14b (Justia returned 403). The OMMA rule text above was verified directly.
