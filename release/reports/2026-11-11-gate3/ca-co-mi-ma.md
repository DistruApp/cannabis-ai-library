# Gate 3 fact-check: CA, CO, MI, MA vs `state-profiles.md`

Checked 2026-11-11. Read-only: no repo file was edited.

**Profile checked:** `skills/cannabiz-skills/compliance/cannabis-state-rules-lookup/references/state-profiles.md`. The copies in `cannabis-traceability-reconciliation`, `cannabis-inspection-readiness` and `cannabis-transfer-manifest-precheck` are byte-identical, so every fix below has to go into all four copies, or the duplication needs fixing first. Beyond the profile, the only state rules anywhere in `skills/` and `docs/` are the CA §15034/§15036/§15051 discrepancy rules, in `cannabis-state-rules-lookup/SKILL.md`, its `evals.json` and docs page, and `cannabis-traceability-reconciliation/SKILL.md:82`.

**Method:** Step 1 answers came from primary or secondary sources before I opened the library. Step 2 then compared them with the library.

**Sources and access:**

| State | Text used | Official sites |
|---|---|---|
| CA | Cornell LII copy of 4 CCR Div. 19 (secondary; history notes go to 2022). DCC's own site wasn't needed. | — |
| CO | Cornell LII copy of 1 CCR 212-3 (secondary; amendment history ends "47 CR 21 … effective 12/4/2024"). **Not checked against the Jan-2026 or the claimed 2026-11-01 versions.** | **BLOCKED** (403 or Cloudflare): med.colorado.gov/rules, sbg.colorado.gov/med/rules, sos.state.co.us. A person should open https://sbg.colorado.gov/med/rules and https://www.sos.state.co.us/CCR/DisplayRule.do?action=ruleinfo&ruleId=3175 |
| MI | Cornell LII copy of Mich. Admin. Code R 420 (secondary; most rules eff. 3/7/2022, R 420.804 eff. 6/22/2020) | **BLOCKED**: michigan.gov/cra (403), legislature.mi.gov (hung or refused). A person should open https://www.michigan.gov/cra/laws-rules-and-regulations and https://legislature.mi.gov/Laws/MCL?objectName=mcl-333-27903 |
| MA | The CCC's own PDF "935 CMR 500.000 … Effective 09-11-2026" (official regulator site; self-described as an unofficial compilation), https://masscannabiscontrol.com/document/935-cmr-500-000-adult-use-of-marijuana-effective-09-11-26-pdf/. Cornell LII for 935 CMR 501 (medical; history to 11/22/2024). CCC "Massachusetts Seed-to-Sale Guidance", May 2021. | — |

## Summary table

| Q | CA | CO | MI | MA |
|---|---|---|---|---|
| Q1 T&T system + recording speed | MATCH | MATCH (system); no hour deadline found, daily reconcile | PROFILE-UNVERIFIED-OK | MATCH (+P1 omission: guidance end-of-day match) |
| Q2 Reconciliation frequency | MATCH | PROFILE-UNVERIFIED-OK (Cornell text matches verbatim) | COULDN'T-VERIFY (no rule in R 420; statute and bulletins blocked) | MATCH (P2: cites an older PDF) |
| Q3 "Significant" discrepancy | MATCH | OMISSION, P2 (no threshold defined; say so) | COULDN'T-VERIFY (none in R 420) | **OMISSION, P0** (no % threshold: *any* inventory discrepancy is a 24-h reportable incident) |
| Q4 Notification deadlines | MATCH (+P1 omission: loss of T&T access) | **OMISSION, P0** (3-920(B): 14 days) | **OMISSION, P0** (R 420.804: 24 h) | **OMISSION, P0** (500.110(9): 24 h + 10-day report) |
| Q5 Adjustments and corrections | MATCH (P2: §15049(e) should be (d)) | OMISSION, P1 | COULDN'T-VERIFY | OMISSION, P1 (guidance) |
| Q6 Manifest + lab status | OMISSION, P1 | OMISSION, P1 | OMISSION, P1 | OMISSION, P1 |
| Q7 Records retention | OMISSION, P1 (7 yr) | OMISSION, P1 | OMISSION, P1 (4 yr) | OMISSION, P1 |
| Q8 Waste and destruction | Partial MATCH (§17223) + OMISSION, P1 | OMISSION, P1 | **OMISSION, P0** (90-day destroy deadline) + P1 | OMISSION, P1 |
| Q9 Worker credential | OMISSION, P1 | OMISSION, P1 | OMISSION, P1 | OMISSION, P1 |

**How I graded severity.** P0 means a missing notification or destruction deadline that a library skill's own workflow runs into: reconciliation, discrepancy, theft, or expired or destroyed product. Other legal deadlines and requirements are P1. Citation, wording and freshness problems are P2.

---

## Step 1: primary-source answers

### California, 4 CCR Div. 19 (DCC; adult-use and medicinal share these rules)
Every source below is a Cornell LII copy, accessed 2026-11-11, at https://www.law.cornell.edu/regulations/california/4-CCR-<section>.

| Q | Citation | Operative text (≤40 words) | Conf. |
|---|---|---|---|
| Q1 | §15049(b); §15049.1(a); §15048(b)(2) | "Each of the following activities shall be recorded in the track and trace system within 24 hours of occurrence". For cultivation activities, "within three (3) calendar days of occurrence". Access is requested from Metrc support. | High |
| Q2 | §15051(a)(1); §15048.1(a)(8) | "at least once every 30 calendar days … Reconciling on-hand inventory of cannabis and cannabis product with the records in the track and trace system" | High |
| Q3 | §15034 | "a five percent difference between the licensee's physical inventory and the inventory recorded in the track and trace system." No base is defined. | High |
| Q4 | §15036(a),(b); §15051(b); §15048.1(a)(7); §15050(c)(1) | "notify the Department and local law enforcement within 24 hours of discovery" of a significant discrepancy, diversion, theft, loss, criminal activity, loss or alteration of records, or a security breach. The notice goes on "DCC-LIC-028". §15051(b): audit, and written notice if significant. §15048.1(a)(7): "Notify the Department of any loss of access to the track and trace system that exceeds 72 hours". §15050(c)(1): back-enter within three calendar days once access is restored. | High |
| Q5 | §15049(d); §15048.1(a)(4) | "If a package adjustment is used … the licensee shall include a description explaining the reason for adjustment." "Correct any data entry errors within three (3) calendar days of discovery of the error" | High |
| Q6 | §15049.2(a),(c),(d); §15314(a),(b),(d); §15307(a)-(g); §15309(b) | The manifest must be prepared in T&T before transfer and must show the origin, distributor and receiver (name, license number, address), UIDs, item name, category, weight or count, estimated departure and arrival, driver's license number, and vehicle make, model and plate. "If there are any discrepancies … the licensee shall reject the shipment." Before transport to a retailer, the distributor must confirm the COA matches the batch, the COA is "less than 12 months old", and labels match. | High |
| Q7 | §15037(a) | "Records must be kept for at least seven years from the date of creation, unless a shorter time is specified." | High |
| Q8 | §15049(b)(5),(c)(6); §17223(b),(c) | Destruction must be recorded within 24 h, and the notes must give "(A) The name of the employee performing the destruction or disposal; (B) The reason …; and (C) The method of disposal." §17223 (cultivation chapter) requires a written waste plan and a secured receptacle. I found no holding period, witness or video rule. | High |
| Q9 | §15043 | Retail and temporary-event staff "shall display a laminated or plastic-coated identification badge issued by the licensee". There's no state-issued worker credential. | High |

### Colorado, 1 CCR 212-3 (MED; medical and adult-use)
Every source below is a Cornell LII copy, accessed 2026-11-11, at https://www.law.cornell.edu/regulations/colorado/1-CCR-212-3-<rule>. The amendment history ends 12/4/2024, so it **predates the Jan-5-2026 and claimed Nov-1-2026 versions**. The official site is BLOCKED.

| Q | Citation | Operative text | Conf. |
|---|---|---|---|
| Q1 | 3-805(A),(E)(1) | "Licensees are required to use the Inventory Tracking System as the primary inventory tracking system of record." I found no hour-based entry deadline. Entries are governed by daily reconciliation. | Med |
| Q2 | 3-805(E)(1) | "A Licensee must reconcile all on-premises and in-transit Regulated Marijuana inventories each day in the Inventory Tracking System at the close of business." | Med |
| Q3 | (none) | I found no numeric "significant discrepancy" threshold in 3-805, 3-905 or 3-920. | Med |
| Q4 | 3-920(B),(C),(D); 3-905(B)(24)(b),(c) | Report to the Division any discovered plan or action to commit "theft, burglary, underage sales, diversion … or … compromise the integrity of the Inventory Tracking System … as soon as possible after the discovery … but not later than 14 days." Local law-enforcement obligations are unchanged. Adverse health events: 48 h. Fire: 48 h to the Division. The security plan must include theft-reporting and post-theft reconciliation protocols. I found no named form. | Med |
| Q5 | 3-805(I)(6); 3-805(F)(1),(3); 3-605(I)(3)(a) | ITS entries must include "a note explaining the reason for any destruction … and reason for any adjustment of weights to Inventory Tracking System packages." Receipt discrepancies must be documented in the ITS. During loss of access, no transfers until access is restored and back-entered. I found no correction-deadline rule. | Med |
| Q6 | 3-605(C),(E),(H)(2)-(3),(I); 4-215(A)(1); 4-210; 4-205(G)(2) | The ITS manifest must show departure date and time, origin and destination (name, address, license), transporter, product name and quantity (weight and unit), arrival date and ETA, vehicle make, model and plate, and the escorting licensee's name and license number. A copy goes to the recipient. "shall not Transfer or process … unless Test Batches … has been tested … and passed all contaminant tests required by this Rule" (exceptions: 5-205(C), 6-205(C), Reduced Testing Allowance). Potency testing is required before transfer (4-210). | Med |
| Q7 | 3-905(A)(2)(a), (B), (B.5) | Six months of records on premises. The listed records are kept for the "current calendar year and the preceding calendar year". Books and records "necessary to fully account for the business transactions" are kept for the "current year and three immediate prior tax years". | Med |
| Q8 | 3-230(D),(E),(F)(4),(I) | Waste must be made "unusable and Unrecognizable prior to leaving the Licensed Premises" (≥50% non-marijuana mix, or compost, digestion, biochar or gasification). It must be weighed and tracked in the ITS, and a waste log kept. Third-party mobile rendering must be recorded on video. I found no advance-notice or holding period in this version. | Med |
| Q9 | 3-205(A) | "All Persons in a Limited Access Area … shall be required to hold and properly display a current Identification Badge issued by the Division at all times." (Owner or Employee License.) | Med |

### Michigan, Mich. Admin. Code R 420 (CRA; MRTMA adult-use and MMFLA medical)
Every source below is a Cornell LII copy, accessed 2026-11-11, at https://www.law.cornell.edu/regulations/michigan/Mich-Admin-Code-R-420-<n>. The official sites and the statute (Marihuana Tracking Act, MCL 333.27903) are BLOCKED.

| Q | Citation | Operative text | Conf. |
|---|---|---|---|
| Q1 | R 420.210(1)-(2); R 420.505(2); R 420.304(1)(j) | "A licensee shall immediately tag, identify, or record as part of a batch in the statewide monitoring system any marihuana product". Sales locations "shall enter all transactions, current inventory" in the SMS. Labs enter results "within 3 business days of test completion". The SMS is Metrc (vendor and CRA FAQ; not fetched). | Med |
| Q2 | (none found) | I found no reconciliation frequency in R 420. | — |
| Q3 | (none found) | I found no threshold in R 420. | — |
| Q4 | R 420.804(1) (licensees); R 420.15 (applicants); R 420.802(4),(9),(10); R 420.602(2)(a) | "Licensees shall notify the agency and local law enforcement authorities within 24 hours of becoming aware of, or within 24 hours of when the licensee should have been aware of, the theft or loss of any marihuana product or criminal activity". Employee or third-party violations: 3 business days. Fire: 1 business day (agency and BFS). An employee's felony charge or conviction: "immediately". | Med-High |
| Q5 | (none found) | I found no adjustment-reason or correction-deadline rule in R 420. CRA and Metrc bulletins are blocked. | — |
| Q6 | R 420.303(5)-(6); R 420.304(1)(k); R 420.502(5); R 420.214a(7); R 420.206(7)(e)-(j); R 420.304(1)(i)(ii) | "Before the cultivator transfers or sells … to a marihuana sales location, a sample … must be tested … All test results must indicate passed". Exception: untested product may go to a producer for processing. Quarantined product "may not be packaged, transferred, or sold until passing test results are entered". Before a sale or transfer, verify in the SMS that the product isn't on hold, recalled, or ordered destroyed. Transporters carry a route plan and manifest, must not hold product that isn't on the manifest, wait until the product is weighed and accepted, and hold custody ≤96 h. | Med-High |
| Q7 | R 420.203(2)(f)(iii) | "Licensee records must be maintained for at least 4 years" (longer during an investigation). | Med-High |
| Q8 | R 420.211(1),(4),(6),(8); R 420.502(4),(6) | Waste must be made unusable and unrecognizable (≥50% mix), "recorded in the statewide monitoring system", and disposed of by an approved method, with comprehensive waste records. "A marihuana business shall destroy all product required to be destroyed for any reason within 90 calendar days of when the marihuana business became aware". Expired product must be destroyed. | Med-High |
| Q9 | R 420.602(2)(b)-(c) | There's no state badge or employee license. Employees are entered in the SMS "within 7 business days of hiring" to get an employee ID, and removed within 7 business days of termination. | Med-High |

### Massachusetts, 935 CMR 500 (adult use, eff. 09-11-2026) and 501 (medical)
The main source is the CCC PDF (eff. 09-11-2026), accessed 2026-11-11. For 501 I used the Cornell LII copy. The guidance is the CCC Seed-to-Sale Guidance (May 2021), https://masscannabiscontrol.com/wp-content/uploads/2021/05/20210517_Guidance_Seed-to-Sale.pdf.

| Q | Citation | Operative text | Conf. |
|---|---|---|---|
| Q1 | 500.105(8)(b),(e),(g); 500.002 (Seed-to-sale SOR); Guidance Q12, Q13 | "Real-time inventory shall be maintained". The SOR is the system designated by the Commission (Metrc). Guidance Q13: "at the end of day physical inventory must match Metrc"; Q12: waste "accounted for by the end of the business day". | High (rule), Med (guidance) |
| Q2 | 500.105(8)(c)2-3, (d) | "Conduct a monthly inventory … Conduct a comprehensive annual inventory". Each inventory record has the date, a summary, and the names, signatures and titles of the people who took it. | High |
| Q3 | 500.110(9)(a)1 | There's no numeric threshold. "Discovery of inventory discrepancies" is itself a reportable incident. | High |
| Q4 | 500.110(9)(a)-(c); 500.105(13)(b)1 (transport); 501.110(9) (medical) | Notify "Law Enforcement Authorities and the Commission … immediately and, in no instance, more than 24 hours following discovery". Triggers include discrepancies, diversion or theft or loss, unauthorized destruction, and loss or alteration of records. Then "within ten calendar days" file the incident report with the Commission. Keep the documentation ≥1 yr. Transport: report "any unusual discrepancy in weight, count, or inventory" within 24 h. | High |
| Q5 | Guidance Q9, Q36, Q37 (not regulation) | A wrong wet weight can be corrected through Metrc Support within 48 h; after that, file an incident report and a plan of correction. QC-sample adjustments need a comment. Retail voids must be reconciled in Metrc and POS within 24 h. | Med |
| Q6 | 500.105(13)(f); 500.105(8)(h); 500.160; Guidance Q39-40 | The manifest is completed before transport and sent to the destination beforehand. It lists origin and destination (name, address, registration number), agent names and registration numbers, the product description with weight and form, mileage, departure and arrival times, before and after weight or count, a reweigh time, and a receiver signature. "No Marijuana Product … may be sold or otherwise marketed for adult use that has not first been tested". Guidance: "a Licensee may only transfer cannabis product that has test results. This requirement includes transfers between licenses". Failed product may move only cultivator to manufacturer, for remediation. Notify the CCC within 72 h of a non-remediable failure. | High |
| Q7 | 500.105(12)(d); 500.105(13)(f)5; 500.110(9)(c); 500.105(9)(g) | Waste records: 3 yrs. Manifests: ≥1 yr. Incident documents: ≥1 yr. After closure: 2 yrs. | High |
| Q8 | 500.105(12)(c)-(d) | Grind and mix until unusable. "A Marijuana Establishment Agent shall witness and document". Keep an electronic record of date, type, quantity, manner, location, and the agent's name and signature, for 3 years. **The 2026 text says one agent. The 2024 Cornell copy said "No fewer than two".** | High |
| Q9 | 500.030(5)-(7) | "A Marijuana Establishment Agent shall always carry a Registration Card". Tell the CCC within 5 business days of changes or a lost or stolen card. | High |

---

## Step 2: findings and proposed profile text

The proposed text follows the profile's style. Labels: **V (Cornell LII secondary copy)** means checked on 2026-11-11 against the Cornell copy. **V** alone means checked on the regulator's own site.

### P0

**P0-1, MA Q3/Q4: any inventory discrepancy triggers 24-h notice plus a 10-day report.** This is an OMISSION. The profile has nothing on MA notification. The reconciliation skill says "For any other state, use only a threshold cited in state-profiles.md". So for MA it would apply no threshold and no notice, when in fact every discrepancy is reportable.
Add under MA:
> - **935 CMR 500.110(9), incident reporting:** notify "appropriate Law Enforcement Authorities and the Commission … immediately and, in no instance, more than 24 hours following discovery". Triggers include "Discovery of inventory discrepancies", diversion, theft or loss, unauthorized destruction, and loss or alteration of records. **There is no % threshold: any discrepancy counts.** Then, "within ten calendar days", submit an incident report to the Commission. Keep the documentation for at least 1 year. Transport (500.105(13)): report "any unusual discrepancy in weight, count, or inventory" within 24 hours. Medical MTCs: 501.110(9) has the same deadlines (Cornell copy). (V, CCC PDF effective 09-11-2026, checked 2026-11-11.) **Always state both deadlines.**

Source: https://masscannabiscontrol.com/document/935-cmr-500-000-adult-use-of-marijuana-effective-09-11-26-pdf/ and https://www.law.cornell.edu/regulations/massachusetts/935-CMR-501-110

**P0-2, MI Q4: 24-hour theft or loss notice.** This is an OMISSION.
Add under MI:
> - **R 420.804(1):** "Licensees shall notify the agency and local law enforcement authorities within 24 hours of becoming aware of, or within 24 hours of when the licensee should have been aware of, the theft or loss of any marihuana product or criminal activity at the marihuana business." (V, Cornell LII secondary copy, eff. 2020-06-22. NEEDS VERIFICATION against CRA's current rules, since michigan.gov is blocked.) Related deadlines in R 420.802: employee or third-party violations, 3 business days; fire, 1 business day (agency and BFS). R 420.602(2)(a): an employee's felony charge or conviction must be reported "immediately". MI rules set no numeric "significant discrepancy" threshold (none found in R 420). Treat an unexplained shortage as possible "loss" and escalate to compliance the same day.

Source: https://www.law.cornell.edu/regulations/michigan/Mich-Admin-Code-R-420-804 and https://www.law.cornell.edu/regulations/michigan/Mich-Admin-Code-R-420-802

**P0-3, CO Q4: crime and diversion reporting within 14 days.** This is an OMISSION.
Add under CO:
> - **Rule 3-920(B):** report to the Division any discovered plan or action to commit "theft, burglary, underage sales, diversion of marijuana or marijuana product, or other crime", or to "compromise the integrity of the Inventory Tracking System", "as soon as possible after the discovery of the action, but not later than 14 days". This "does not alter or eliminate" any duty to report to local law enforcement. Also: adverse health events to the Division within 48 h (3-920(C)); fire to the Division within 48 h (3-920(D)). There is no numeric "significant discrepancy" threshold (none found in 3-805, 3-905 or 3-920). **NEEDS VERIFICATION** against the rules effective 2026-11-01. (Quoted from the Cornell LII copy, amended through 2024-12-04.)

Source: https://www.law.cornell.edu/regulations/colorado/1-CCR-212-3-3-920

**P0-4, MI Q8: destroy within 90 days.** This is an OMISSION. It matters for the expiring-inventory workflow.
Add under MI:
> - **R 420.502(4),(6):** expired product can't be sold or transferred and "must be destroyed". "A marihuana business shall destroy all product required to be destroyed for any reason within 90 calendar days of when the marihuana business became aware". Before any sale or transfer, verify in Metrc that the product isn't on administrative hold, recalled, or ordered destroyed (R 420.502(5)). Waste must be made unusable and unrecognizable (≥50% non-marihuana mix), "recorded in the statewide monitoring system", and logged (R 420.211(1),(4),(8)). (V, Cornell LII secondary copy, eff. 2022-03-07. NEEDS VERIFICATION against CRA's current rules.)

Source: https://www.law.cornell.edu/regulations/michigan/Mich-Admin-Code-R-420-502 and https://www.law.cornell.edu/regulations/michigan/Mich-Admin-Code-R-420-211

### P1

**P1-1, CA Q6: manifest contents and testing status.** This is an OMISSION. The transfer-manifest-precheck skill reads this profile.
> - **§15049.2(a), shipping manifest (in T&T, before transfer):** must include the origin, distributor and receiver (name, license number, premises address), "The UID numbers for all items", item name, category and weight or count per tag, estimated departure and arrival, driver's license number, and vehicle make, model and plate. §15049.2(d): "If there are any discrepancies … the licensee shall reject the shipment." §15314(b): the manifest goes to DCC and the receiver before transport. (V, Cornell LII secondary copy.)
> - **Testing:** in CA, regulatory testing happens at the distributor (§15304), so **cultivator→distributor transfers of untested product are normal and shouldn't be held.** Before transporting to a retailer, the distributor must confirm (§15307) that the COA matches the batch and is "less than 12 months old", that labels match the COA, and that the T&T weight or count matches. (V, Cornell LII secondary copy.)

**P1-2, CA Q7:**
> - **§15037(a), retention:** "Records must be kept for at least seven years from the date of creation, unless a shorter time is specified." (V, Cornell LII secondary copy.)

**P1-3, CA Q8 (adds to the existing §17223 line):**
> - **§15049(c)(6):** when recording destruction (within 24 h, §15049(b)(5)), the notes must give "(A) The name of the employee performing the destruction or disposal; (B) The reason for destruction or disposal; and (C) The method of disposal." Note that §17223 sits in the cultivation chapter (Ch. 4), and requires waste to be kept in a secured receptacle or area until disposal (§17223(c)). (V, Cornell LII secondary copy.)

**P1-4, CA Q4 (loss of access):**
> - **§15048.1(a)(7) / §15050:** "Notify the Department of any loss of access to the track and trace system that exceeds 72 hours". While access is down, don't transport, receive or deliver, and keep paper records. Once restored, enter the activity "Within three calendar days". (V, Cornell LII secondary copy.)

**P1-5, CA Q9:**
> - **§15043, badges:** staff of retailers and temporary events must display a licensee-issued "laminated or plastic-coated identification badge" (DBA, license number, first name, employee number, color photo). There's no state-issued worker credential. (V, Cornell LII secondary copy.)

**P1-6, CO Q5:**
> - **Rule 3-805(I)(6):** ITS entries must include "a note explaining the reason for any destruction of Regulated Marijuana, and reason for any adjustment of weights to Inventory Tracking System packages." 3-605(I)(3): receipt discrepancies "shall be made in the Inventory Tracking System". 3-805(F)(3): after a loss of ITS access, no transfers until access is restored and back-entered. No correction-deadline rule was found. **NEEDS VERIFICATION** (Cornell LII, through 2024-12-04).

**P1-7, CO Q6:**
> - **Rule 3-605(H)(3), manifest:** departure date and time; origin and destination name, address and license; transporter (if any); product name and quantity (by weight and unit) per destination; arrival date and ETA; vehicle make, model and plate; and the name and license number of the escorting licensee. A copy goes to each recipient (3-605(H)(2)). During transport, carry the business license, the driver's Owner or Employee License, a driver's license, and registration and insurance (3-605(E)).
> - **Testing:** "shall not Transfer or process … unless Test Batches … has been tested … and passed all contaminant tests" (4-215(A)(1); exceptions are 5-205(C), 6-205(C) and Reduced Testing Allowance). Potency testing is required before transfer (4-210). **NEEDS VERIFICATION** (Cornell LII, through 2024-12-04).

**P1-8, CO Q7:**
> - **Rule 3-905:** keep six months of records on premises. The listed records are kept for the current and preceding calendar year. Books and records "necessary to fully account for the business transactions" are kept for the "current year and three immediate prior tax years". Off-premises records must be produced within 3 business days of a request. **NEEDS VERIFICATION.**

**P1-9, CO Q8:**
> - **Rule 3-230:** waste must be made "unusable and Unrecognizable prior to leaving the Licensed Premises" (≥50% non-marijuana mix, or compost, digestion, biochar or gasification). It must be weighed and tracked in the ITS, and a waste log kept. Third-party mobile rendering must be recorded on video (3-230(F)(4)). No advance-notice or holding period was found in this version. **NEEDS VERIFICATION.**

**P1-10, CO Q9:**
> - **Rule 3-205(A):** everyone in a Limited Access Area must "hold and properly display a current Identification Badge issued by the Division" (Owner or Employee License), worn visibly at or above the waist. **NEEDS VERIFICATION.**

**P1-11, MI Q6.** This is an OMISSION, and the precheck skill's worked example is a Michigan processor.
> - **Testing before transfer:** a cultivator can't transfer or sell to a sales location until "All test results must indicate passed in the statewide monitoring system" (R 420.303(5)). **Exception:** untested product may go to a producer for processing (R 420.303(6)). Quarantined product "may not be packaged, transferred, or sold until passing test results are entered" (R 420.304(1)(k)). Check for an administrative hold or recall first (R 420.502(5)).
> - **Manifest:** transporters must carry a route plan and manifest, must not possess product that isn't on the manifest, must wait on site until the product is weighed and accepted or rejected, and may hold custody for no more than 96 h (R 420.206(7)(e)-(j)). (V, Cornell LII secondary copy. NEEDS VERIFICATION against current CRA rules.)

**P1-12, MI Q7:**
> - **R 420.203(2)(f)(iii):** "Licensee records must be maintained for at least 4 years", or longer if an investigation is open. (V, Cornell LII secondary copy.)

**P1-13, MI Q9:**
> - There's no state worker badge or employee license. Employees must be entered in Metrc "within 7 business days of hiring", and removed within 7 business days of termination (R 420.602(2)(b)-(c)). (V, Cornell LII secondary copy.)

**P1-14, MA Q6:**
> - **500.105(13)(f), manifest:** completed before transport and sent to the destination beforehand. It includes origin and destination (name, address, registration number), the names and registration numbers of the transporting agents and the preparer, the product description with weight and form, mileage, departure and arrival times, before and after weight or count, the reweigh time, and the receiver's signature. Retain for at least 1 year.
> - **Testing:** "No Marijuana Product … may be sold or otherwise marketed for adult use that has not first been tested" (500.105(8)(h)). CCC guidance (May 2021, Q39): "a Licensee may only transfer cannabis product that has test results. This requirement includes transfers between licenses". Failed product may move only cultivator to manufacturer, for remediation. Notify the CCC within 72 h of a non-remediable failed result (500.160). (V, CCC PDF effective 09-11-2026; guidance V but dated 2021.)

**P1-15, MA Q7/Q8:**
> - **500.105(12)(d), waste:** "A Marijuana Establishment Agent shall witness and document" rendering. Keep an electronic record of date, type, quantity, manner, location, and the agent's name and signature, for at least 3 years. **The 2026-09-11 text requires one agent. Earlier versions required "No fewer than two".** Don't use old SOPs. Other retention periods: manifests ≥1 yr; incident documents ≥1 yr or the length of an investigation; all records 2 yrs after closure. (V, CCC PDF effective 09-11-2026.)

**P1-16, MA Q9:**
> - **500.030(7):** "A Marijuana Establishment Agent shall always carry a Registration Card" while handling or transporting product. Report changes or a lost or stolen card within 5 business days (500.030(6)). (V, CCC PDF effective 09-11-2026.)

**P1-17, MA Q1/Q5 (guidance, not regulation):**
> - CCC Seed-to-Sale Guidance (May 2021, so check it's still current): "at the end of day physical inventory must match Metrc". Waste must be "accounted for by the end of the business day". A wrong wet weight can be corrected through Metrc Support within 48 h; after that, file an incident report. Retail voids must be reconciled in Metrc and POS within 24 h. QC-sample adjustments need a comment. (Guidance V, 2021.)

### P2

- **P2-1, CA §15049 citation letter.** The profile says "§15049(e): for package adjustments…". In the Cornell LII copy the adjustment text is **§15049(d)**, and (e) is partial-shipment rejection. If the DCC Oct-2026 compilation has renumbered, keep (e). Otherwise change it to (d).
- **P2-2, CO 3-805(E)(4) quote not found verbatim.** The profile quotes "Secondary software applications must use the Inventory Tracking System data as the primary source of data." The Cornell copy reads "Secondary systems must use the Inventory Tracking System data as the primary source of data and must be compatible with updating to the Inventory Tracking System." Fix the quote or confirm it against the 2026-11-01 text.
- **P2-3, CO effective date unverified.** I couldn't confirm the "effective 2026-11-01" date (the official sites are blocked). Web search only found a 2026-01-05 rulemaking (Vicente LLP alert). The profile's MED URLs (med.colorado.gov) return 403. MED material now appears under sbg.colorado.gov/med, so check that the links still work.
- **P2-4, CO Q3.** Add: "CO rules define no numeric significant-discrepancy threshold. Don't apply CA's 5%." The same applies to MI.
- **P2-5, profile Metrc quote for CO** ("required to use METRC as the primary inventory tracking system of record", from med.colorado.gov/metrc). I couldn't fetch it. The rule text (3-805(A)) says "required to use the Inventory Tracking System as the primary inventory tracking system of record".
- **P2-6, MI rules-rewrite claim.** The profile's "CRA rules rewrite is pending" is unverifiable from here. Cornell's newest MI rule dates are 2022-03-07 and 2020-06-22.

**Dates older than 90 days before 2026-11-11 (cutoff 2026-08-13):**
- MA: "from the CCC PDF dated 2026-04-24". That PDF is superseded by the 09-11-2026 version, which I checked, and the 500.105(8) quotes still appear verbatim. Re-cite the 09-11-2026 PDF.
- CO: "Quoted from the version effective 2026-01-05". The profile already flags this as superseded.
- CA: "DCC-LIC-028 form PDF dated January 2026". This is a form revision date and is probably fine, but re-check it.
- MI: "Cornell LII, eff. 2022-03-07". This is a rule effective date, not a review date, but no newer rule was verified.
- If the MA 2021 Seed-to-Sale Guidance is added, label it with its 2021 date.

**Quotes checked verbatim and found:** CA §15049(b), §15049.1, §15051, §15034, §15036(a), §15048.1(a)(4),(8); CO 3-805(E)(1) (Cornell); MI R 420.210; MA 500.105(8) (2026 PDF). **Not found verbatim:** CO 3-805(E)(4) (P2-2). The CA §15049(e) text exists but is at (d) (P2-1).

**Downstream text to update when the profile changes:** the reconciliation skill's line "For any other state, use only a threshold cited in `references/state-profiles.md`" (`cannabis-traceability-reconciliation/SKILL.md:82`) should also tell the agent to surface the state's discrepancy *notification* rule (MA: any discrepancy within 24 h; MI and CO: theft or loss). Otherwise a MA or MI operator gets no deadline at all.
