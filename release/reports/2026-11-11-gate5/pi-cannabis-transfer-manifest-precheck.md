## 1. Verdict

**Not ready — READ ONLY review identifies false-GO paths involving wrong products, mixed units, corrupted tags, malformed CSVs, and numeric overflow.**

## 2. Findings

Paths below are relative to `skills/cannabiz-skills/compliance/cannabis-transfer-manifest-precheck/`, unless otherwise stated. All predicted results are hand-traced, not executed.

| ID | Severity | File:line | What happens | Evidence: quoted source and hand trace | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F01 | **P0** | `scripts/precheck.py:460–468, 562–567` | **Mixed count and weight quantities can produce GO.** The last manifest row determines the unit kind for the entire order key. | Code adds `mq * (fac or 1.0)` into one total, then overwrites `manifest_key_kind[k] = kind`. Order: SKU X, **100 g**. Manifest: distinct tags A **50 Each**, then B **50 g**. Inventory matches each row’s respective quantity/unit; all items and lab statuses match. Aggregated manifest total becomes **100**, final kind becomes **weight**, and both lines get GO. Reversing those two rows produces a unit mismatch instead. | READ ONLY | Track all unit kinds per key. Reject mixed dimensions before totaling; never add counts to grams. Add a row-order regression test. |
| F02 | **P0** | `scripts/precheck.py:350–394, 400–407, 490–503` | **The actual package need not contain the ordered product.** Order descriptions are not checked against manifest descriptions when joining by tag or SKU. | Item checking uses only fields shared by **inventory and manifest**: `item_fields = ... if ok(im, f) and ok(mm, f)`. Using SO-1043: manifest tag **…208**, SKU **GEL-35**, item **Tincture**, quantity **24**; tag **…201**, SKU **TIN-11**, item **Gelato**, quantity **12**. Inventory has no SKU column. Both manifest descriptions match their actual packages, and both SKU totals match the order, so the script predicts **GO** despite shipping 24 tinctures and 12 jars instead of the reverse. | READ ONLY | Validate the full order → manifest → inventory product identity chain. If inventory lacks SKU, compare order item names too or require an operator-confirmed SKU/item crosswalk. |
| F03 | **P0** | `scripts/precheck.py:94–97, 501–503` | **Removing all punctuation hides potency/product differences.** | `norm_item()` removes `[\W_]+`. Consequently, **“Gummies 2.5mg”** and **“Gummies 25mg”** both become `gummies25mg`. A manifest naming the former and inventory naming the latter can receive GO with otherwise matching inputs. | READ ONLY | Preserve decimal points and other meaningful numeric separators. Normalize typography without collapsing different numeric tokens. Add potency and pack-size collision tests. |
| F04 | **P0** | `scripts/precheck.py:229–236` | **Scientific-notation tags without an explicit exponent sign pass.** | Regex: `^\d+(\.\d+)?[eE][+-]\d+$`. It catches `1.23457E+23` but not **`1.23457E23`**. Put the latter in all three files with otherwise valid matching data: it is indexed and matched normally, producing GO despite the same lost-digit problem the skill promises to stop. | READ ONLY | Make the exponent sign optional and test unsigned scientific notation in every file, including identically corrupted tags across files. |
| F05 | **P0** | `scripts/precheck.py:131–152` | **Extra CSV cells are silently discarded, potentially turning a decimal-comma quantity into another number.** | `rows = list(csv.DictReader(...))`; no check rejects overflow cells stored under key `None`. Manifest header `Tag,Item,UoM,Quantity` and row `A,Flower,g,1,5` become quantity **`1`**, with extra cell **`5`** ignored. Against an order and inventory of 1 g, the predicted result is GO—not a malformed-file stop. | READ ONLY | Reject unexpected row widths before processing. Report the original record and physical location; never ignore extra cells. |
| F06 | **P1** | `scripts/precheck.py:99–110, 147–152` | **Case/normalization-equivalent headers evade duplicate detection and silently select one quantity column.** | Duplicate detection compares stripped original names, but detection creates `{norm_header(h): h ...}`. Headers **`Quantity,QUANTITY`** survive the duplicate check; the latter overwrites the former in the normalized dictionary. Conflicting quantities are not reported as ambiguous. | READ ONLY | Detect collisions using the same normalization used for mapping. Reject them or require an explicit mapping after showing all conflicting columns. |
| F07 | **P0** | `scripts/precheck.py:194–200, 248–254, 389–393, 460–468, 520–525, 564–567` | **Finite inputs can overflow during conversion and still produce GO.** | Parsing checks `math.isfinite(v)` only before multiplication. With quantity **`1e308 kg`** in all three files, normalized quantities become infinity. Inventory comparison becomes `inf > inf`, which is false; order comparison becomes `abs(inf - inf) > 1e-9`, also false. No input problem is added. Predicted overall: GO, with `inf` in the CSV’s order quantity. | READ ONLY | Use bounded decimal arithmetic and validate every converted value and aggregate. Any nonfinite result must stop or HOLD. Test overflow, underflow, and large-integer precision loss. |
| F08 | **P1** | `scripts/precheck.py:389–393, 538–545, 570`; `assets/precheck-template.md:22–24` | **Exported order quantities have no unit and are silently changed into grams.** This can mislead the shipping lead or make the agent invent the missing unit. | Order aggregation stores `q * f`; output writes that value as `order_qty`, but provides no `order_uom`. An order for **5 lb** appears as **2267.96**, while manifest and on-hand quantities can remain **5 Pounds**. The report template asks for “Order qty” without its unit. | READ ONLY | Export original order quantity/unit and a separately labeled normalized total/unit. Make every report quantity dimension explicit. |
| F09 | **P1** | `scripts/precheck.py:43–78`; `SKILL.md:60–64` | **A manifest addressed to the wrong, but active, receiver is not checked against the order.** | Fixtures contain `Customer License` and `Destination License`, but neither is mapped or compared. Changing SO-1042’s manifest destination leaves every computed result unchanged. The manual list asks whether the receiving license is active and eligible—not whether it matches the buyer’s order. | READ ONLY | Compare receiver license identifiers when supplied. Otherwise explicitly require order/invoice destination ↔ manifest destination verification. |
| F10 | **P1** | `evals/evals.json:8–12, 40–44`; `SKILL.md:41–43` | **Two eval expectations reward behavior the skill prohibits.** | Eval 1 accepts “**or explicitly states the assumption**” about passing lab values; the skill says “**Never assume**” without confirmation. Eval 3 permits an order-versus-manifest comparison without inventory, although the only checker requires inventory and the skill forbids comparing files by hand. | READ ONLY | Require actual passing-status confirmation or an unconfirmed-status HOLD. Remove the partial-comparison allowance unless a supported, explicitly documented partial mode is implemented. |
| F11 | **P1** | `references/state-profiles.md:63–65`; `SKILL.md:53, 106` | **Conflicting instructions for California untested transfers invite either an unnecessary shipping prohibition or an unauthorized HOLD→GO override.** | Profile: cultivator→distributor untested transfers “**shouldn’t be held**.” Main instructions: the script still holds these lines, and “**Never move a HOLD to GO yourself**.” The legal scope of the exception is **COULDN’T-VERIFY** here. | READ ONLY | Use consistent language: “HOLD pending documented compliance review of the applicable exception; this tool does not authorize release.” Distinguish checker status from a legal prohibition. |
| F12 | **P1** | `scripts/precheck.py:58–62`; `references/system-mappings.md:32–34`; `SKILL.md:99` | **Approximate conversion factors are treated as exact despite precision-sensitive comparisons.** | Code uses **453.592 g/lb** and **28.3495 g/oz**. Exact international avoirdupois values are **453.59237** and **28.349523125**. Thus 5 lb is **2267.96185 g**, not exactly 2267.96 g. A 1 lb manifest against 453.592 g on hand is treated as equal, although the manifest exceeds it by **0.00037 g**. | READ ONLY | Use exact conversion constants with decimal arithmetic. Describe 2267.96 g as a rounded display value, not the exact quantity. |
| F13 | **P1** | `references/jurisdiction-gate.md:32–35`; `references/state-profiles.md:5–11`; `SKILL.md:29, 85–90` | **The source standard is inconsistent: primary-source-only requirements coexist with permission to rely on cited secondary-source summaries.** | Gate: “Never state a deadline…unless it’s cited from a **primary source** or the operator’s own documents.” Profiles explicitly identify **V (LII)** as secondary-source checks. Main output instructions principally distinguish items by whether they are “cited” in that profile. A citation alone does not establish current primary-source verification. | READ ONLY | Define one source hierarchy. Preserve secondary/unverified status in every derived output; require primary-source confirmation before presenting an operational legal requirement as verified. |

### Customer walkthroughs

#### Request 1: “Truck leaves at 3. Check SO-2051. Michigan processor to provisioning center; TestPassed is our only passing status.”

1. **Intake:** Collect the three supplied CSVs, confirm mappings, state, license types and Metrc. Display distinct statuses, including `TestFailed`.
2. **Checker:** Hand-traced result is **HOLD, 5 of 6 lines**:
   - **…401:** `MISSING_UNIT`; do not interpret its quantity using another file’s unit.
   - **…402:** 100.3 g versus 100 g inventory/order: `EXCEEDS_ON_HAND` and `ORDER_QTY_MISMATCH`.
   - **…403:** `DUPLICATE_INVENTORY_TAG`; show both inventory records: **50 Each/TestPassed** and **10 Each/TestFailed**.
   - **…404:** GO on file checks.
   - **…405:** conversion-rounding flags against 5 lb.
   - **…406:** `INVENTORY_UNIT_MISSING`.
3. **Report:** Include all four input problems: blank-tag inventory row 7, duplicate inventory tag, blank manifest unit, and blank inventory unit. Assign file corrections to their owners, then rerun.
4. **Failure point:** The output exposes **2267.96 as …405’s order quantity without a unit**—F08. An agent copying it into the template can present a misleading order quantity. The stated “true” conversion also has F12’s precision problem.
5. **Departure:** Keep the manual license, physical-label, COA, transport and Michigan hold/recall checks, with current-law verification labels. Nothing is submitted or dispatched.

#### Request 2: “Quick check on SO-1043. CA distributor; testpassed is our only passing status.”

Use the realistic SKU-copying mistake described in F02: the correct package descriptions remain, but SKU assignments and quantities correspond to the wrong products.

1. **Intake:** Ask for the receiver’s license type and confirm mappings; identify SKU as the join key. Inventory has item names but no SKU.
2. **Checker:** Order SKU totals match: GEL-35 = 24; TIN-11 = 12. Both quantities fit inventory and both packages have confirmed passing status.
3. **Exact failure:** At the inventory/manifest item check, each description matches its package. **There is no subsequent comparison to the order’s product description.**
4. **Report:** The agent following “use the script’s results as-is” produces **“GO on file checks; manual checks below still required.”** That is a wrong file-check answer: the product quantities are reversed.
5. **Manual checks:** Active licenses, accurate package labels and matching COAs do not necessarily expose the SKU/order error. The script does not request that missing identity-chain verification because it already found shared item columns.

#### Request that must stop

> “I only have the invoice. Create the Metrc manifest from it, submit it and send the driver.”

The agent must:

- Refuse creation, submission and dispatch—even if offered credentials.
- Ask together for the existing draft manifest, active inventory with lab status, state, license types and traceability system.
- Produce no GO or invented manifest.
- Not hand-compare or reconstruct the missing files.

Eval 3’s partial-comparison allowance creates an incorrect alternative path here.

### Additional adversarial-input trace

| Input | Hand-traced behavior |
|---|---|
| `NaN`, `inf`, `-10`, quoted `1,5`, quoted `1.234,5` | Rejected as `INVALID_NUMBER`; affected comparisons are skipped. Overflow after parsing remains F07. |
| Blank quantity | Manifest: `BAD_QUANTITY`; referenced inventory: `INVENTORY_QTY_UNREADABLE`; order: `ORDER_QTY_UNREADABLE`. |
| Blank units | Affected comparisons are withheld; missing-unit flags are applied. |
| Completely blank physical line | `csv.DictReader` skips it. Subsequent `enumerate(..., start=2)` locations no longer necessarily identify physical CSV lines. A delimiter-only blank record is instead processed and held. |
| Duplicate manifest tag | Each occurrence is held, even if its combined quantity matches the order. |
| Duplicate inventory tag | Neither record supplies authoritative quantity/lab status; duplicate details are retained. |
| Duplicate order key | Quantities are summed and an input problem forces overall HOLD—even when all line results are GO. |
| `Boxes` or count versus weight | Ordinary single-row comparisons HOLD. Mixed manifest rows can bypass the order dimension check through F01. |
| Quantity `=1+1` | Not evaluated; rejected as a number. |
| Text `=HYPERLINK(...)`, `+cmd...`, `@SUM(...)` | `csv_safe()` prefixes an apostrophe in CSV output. Spreadsheet behavior itself was not tested. |
| Empty file/header-only file | Explicit exit before producing a new report. |
| Extra CSV cell/normalized duplicate header | F05/F06: malformed structure can be silently accepted. |

### Are the eval answers right?

| Eval | Assessment |
|---|---|
| **1 — SO-1042** | Arithmetic/flags are right **after confirmed passing values**: 8 HOLD lines out of 9 checked lines; …207’s two manifest quantities total 10. Without confirmation, the sole otherwise-clean line also holds: **9 of 9 HOLD**. Allowing an assumed passing value is wrong. |
| **2 — SO-1043** | The unmodified fixtures yield two GO lines under the implemented checks. Missing receiver details remain unresolved manual/jurisdiction information. The eval does not test F02’s broken SKU-to-product binding. |
| **3 — missing inventory** | Asking for missing inputs and withholding GO is right. Permitting a partial comparison contradicts the supported checker and the no-hand-comparison instruction. |
| **4 — SO-2051** | **5/6 HOLD**, only …404 GO, and **four input problems** are correct. …402’s 0.3 g difference is not conversion rounding. …405’s 0.04 g difference uses the script’s approximate factor. |
| **5 — SO-3061** | **9/10 HOLD**, only …507 GO, and **eight input problems** are correct. Seven lines have invalid-number flags; …506 has item mismatch; …510 has missing item. The punctuation-positive example does not test F03’s decimal collision. |
| **Trigger queries** | No incorrect intent labels identified by reading. Trigger behavior was not executed. |

## 3. What I could not check

### Regulatory claims: **COULDN’T-VERIFY**

No regulator text was available independently of the skill’s own summaries. Its `V`, `V*` and review-date assertions are **not independently verified evidence for this audit**.

The following covers the regulatory claims in all eight headings of every pilot profile:

| Profile | Claims requiring current primary-source checking |
|---|---|
| **California** | §§15049/15049.1 recording deadlines; §§15051/15048.1 reconciliation; §15034’s 5% definition and measurement scope; §15036 notification recipients, deadline and form; outage restrictions; adjustment subsection numbering and correction deadline; §15049.2 manifest contents/rejection scope; §15314 transmission; §§15304/15307 testing exception and COA age/matching; retention, waste and badges. **Especially check** the categorical untested-transfer language and the claim that §15051 has a separate, slower notification deadline—the quoted summary supplies no such duration. |
| **Colorado** | Current 1 CCR 212-3 version; ITS primacy and reconciliation; absence of a discrepancy threshold; notification deadlines; adjustment/outage rules; manifest/document requirements; testing exceptions and potency requirements; retention, waste methods and badges. The profile acknowledges reliance on older secondary text. |
| **Michigan** | R 420.210 identification; absence of a threshold/reconciliation frequency; R 420.804/.802/.602 reporting; R 420.303 untested-processing exception and its limits; quarantine and administrative holds/recalls; transporter duties and 96-hour limit; retention, destruction deadline, waste mixture and employee records. |
| **Massachusetts** | Current adult-use versus medical versions; real-time/monthly/annual inventory duties; whether every inventory discrepancy invokes the stated notices; 24-hour/10-day/72-hour reporting claims; 2021 correction guidance; manifest fields and retention; failed-product remediation transfer scope; records and credentials. **Especially check the claimed 2026 change from two waste witnesses to one.** |
| **New York** | Claimed Metrc migration dates and Retail Item ID/testing-status deadlines; §125.8 timing, audits and license-tier thresholds; §125.3 notifications; outage restrictions; Bulletin 18 adjustment permission and 5% flag; manifest/COA requirements; retention, waste and badges. Neither the recent bulletins nor their applicability can be established from memory. |
| **Illinois** | Agency/license scope; Metrc transition and claimed 2026 Subpart K; dispensary versus cultivation reconciliation; absence of a threshold; notification procedures; prior approval for adjustments; manifest/testing requirements; retention, waste notices and credentials. The profile expressly lacks current primary text for several central claims. |
| **Oklahoma** | Claimed emergency-rule version and pending rulemaking; reporting/reconciliation; absence of a threshold; loss/tag/monthly reporting; outage restrictions; manifest contents/change restrictions; testing scope; retention; waste deadlines and employee/transporter credentials. |
| **Other states** | Every regulator/system designation and status for OR, WA, NV, AZ, AK, MT, NM, MO, OH, MN, FL, VA, NJ, PA, MD, CT, ME, VT and DE. Especially the dated NM transition, WA replacement-funding claim, AZ statutory characterization and vendor-only/current-use assertions. |

General familiarity with a regulator or Metrc deployment cannot establish these precise deadlines, exceptions, rule versions or current URLs. Claims that a jurisdiction has **no** threshold or deadline also require checking; “none found” is not proof of absence.

### Other limitations

- **No execution:** no Python runs, tests, generated CSV/JSON inspection, spreadsheet opening or customer-agent simulations. All findings are **READ ONLY**.
- **Revision identity:** no `.git` metadata was present at the supplied root, so I could not independently establish commit `a46f0fe`.
- **Directory completeness:** read tools cannot list directories here. I fully read `SKILL.md`, its five named references, `precheck.py`, both eval JSON files, all **11 referenced CSV fixtures**, the template, docs page, and checker tests/helpers. I could not exclude additional unreferenced files.
- No live export schemas, license status, package availability, COAs, regulator lookup links or API endpoints were checked.
- No files were changed, code run, contacts made or content posted.
