# 1. Verdict

**Not ready: the headcount formula can overstaff shifts, and the worked example teaches unsupported savings and incomplete coverage recommendations.**

# 2. Findings

Paths below are relative to `skills/cannabiz-skills/operations/staff-scheduling-optimizer/`, except the explicitly identified docs page. Evidence is quoted source plus hand calculations; no code was run.

| ID | Severity | File:line | What happens | Evidence | Evidence label | Suggested fix |
|---|---|---|---|---|---|---|
| F1 | **P0** | `SKILL.md:101–108`; `examples/sample-output.md:50` | The formula counts fixed roles **on top of an operation-wide minimum**, even when those roles already satisfy that minimum. This produces wrong headcounts and costs on ordinary inputs. | “Headcount is the larger of the demand number and the minimum, plus fixed roles.” For 12 peak transactions/hour, service rate 12, minimum **2 people total**, and one ID checker: instructed result = `max(1,2)+1 = 3`. Required coverage is one budtender plus one checker = **2**. | READ ONLY | Distinguish total-site minimums from role-specific minimums. For this simple case use `max(total minimum, demand floor staff + fixed roles)`, then validate role/certification coverage separately. |
| F2 | **P1** | `SKILL.md:114–116` | Production headcount is underspecified dimensionally. Substituting batch volume for peak-hour transactions yields **worker-hours**, not workers. An agent must invent the missing conversion. | “Do the same with units per worker-hour and the batch or output target instead of transactions.” For 480 units at 20 units/worker-hour: `480÷20 = 24 worker-hours`; over six productive hours, this requires **4 workers**, not 24. | READ ONLY | Specify `workers = ceil(target units ÷ throughput ÷ productive hours available)`, with compatible units, deadlines and break/downtime assumptions. |
| F3 | **P0** | `SKILL.md:174`; `examples/sample-output.md:103–118` | The output requires a current-schedule comparison without requiring the current schedule as an input. The example introduces an unstated baseline and reports precise savings against it. | “Current (flat 3 per shift, every day)” appears in the output, not the supplied inputs. It becomes **252 hours, $4,483**, followed by “72 fewer hours and about $1,255 less labor.” Neither actual baseline assignments nor baseline cost were supplied. The listed weekly caps total only **217 hours**, so this supposed current schedule also cannot fit those caps. | READ ONLY | Require the actual baseline schedule and cost basis. Otherwise report “baseline not provided”; label any hypothetical comparison explicitly. |
| F4 | **P1** | `examples/sample-output.md:124–126` | The recommended Sunday options omit binding hour-cap problems and imply that certification alone solves coverage. A first-time agent could repeat these as usable replacements. | The example suggests asking “Sarah, Dave or Jen” to volunteer. Sarah would reach **30/34 hours**; Dave and Jen would each reach **36/34**, exceeding their hard caps. It also says certifying Mike or Amy “fixes every future Sunday.” In the displayed week, Mike already closes and is capped; Amy already opens. Certification alone supplies no fourth Sunday worker. | READ ONLY | Show each candidate’s resulting hours and blockers. Make certification, renewed credentials, additional availability and additional staffing separate conditions—not an unconditional fix. |
| F5 | **P1** | `examples/sample-output.md:129`; `evals/evals.json:11` | “No overtime” is presented as established despite missing jurisdiction, employer workweek boundaries and adjacent-period hours. That contradicts the skill’s own requirement to present legal applicability as unconfirmed. | Example: “**Overtime: none this week.** The highest is 30 hours.” Eval 1 likewise expects “no overtime.” Thirty displayed calendar-week hours do not establish all applicable overtime treatment. | READ ONLY | Say what arithmetic was checked, e.g. “No displayed employee exceeds 30 scheduled hours; overtime assessment pending jurisdiction, workweek and other worked hours.” |
| F6 | **P1** | `SKILL.md:51–81,85–108`; `templates/schedule-input-template.csv:1–8` | There is no explicit validation contract for malformed numeric inputs, units, duplicate employees, placeholder dates or spreadsheet formulas. An agent must decide how to repair or interpret them. | The template contains `YYYY-MM-DD` and five blank rows. Calculations divide by service rate, average ticket and blended rate, but no instructions require positive finite denominators, compatible units, duplicate reconciliation or unevaluated formula handling. | READ ONLY | Add a validation-first step: ignore wholly blank rows; reject unresolved placeholders and malformed values; reconcile duplicates; confirm units and percentage representation; request formula results rather than evaluating or trusting formulas. |
| F7 | **P1** | `SKILL.md:141–143`; `evals/evals.json:11,16` | The eval silently changes the credential cutoff from **after** the expiration date to **on or after** it. Date-only input does not establish the precise validity cutoff. | Skill: “Don’t schedule them **after** the expiry date.” Eval: “Tom K. is not scheduled **on or after** the day his credential expires.” No jurisdictional rule or expiration time supports that distinction. | READ ONLY | Require validity through the entire shift. Treat an unclear expiration-day cutoff as NEEDS VERIFICATION, or explicitly document conservative exclusion as an operational policy—not a legal fact. |
| F8 | **P1** | `SKILL.md:76,80–81`; `evals/evals.json:7–11` | Eval 1 rewards producing a full schedule from inputs that fail the skill’s mandatory-input gate. An agent following the skill literally should ask questions first. | The skill requires “State/jurisdiction of each location” and says, “If any of this is missing, ask for it before producing a schedule.” Eval 1 supplies no jurisdiction; its roster supplies no current weekly hours. Nevertheless, its expected answer is a complete draft. | READ ONLY | Supply the missing inputs or expect clarification first. Explicitly state whether existing hours are zero and whether the draft replaces or supplements existing assignments. |
| F9 | **P1** | `docs/cannabiz-skills/operations/staff-scheduling-optimizer.md:29`; `examples/sample-output.md:96–110` | The customer-facing docs describe **180 hours as a scheduled result**, although six hours remain unfilled. They also foreground the cost percentage for a hypothetical filled gap. | Docs: “a draft schedule of 180 hours … labor at about 17.7 percent.” The example’s actual allocation is **174 filled hours, $3,120**, plus **6 OPEN GAP hours**. The **$3,228 / 17.7%** result assumes that gap can be filled at $18/hour. | READ ONLY | Report required, assigned and unfilled hours separately. Label the filled-gap cost as conditional, including the assumed rate. |

## End-to-end customer walkthroughs

### Request 1: “Build next week’s dispensary schedule”

Using Eval 1’s fictional roster and demand:

1. **Intake should stop first:** jurisdiction and current weekly hours are missing. Producing the expected complete schedule already conflicts with the mandatory-input gate (**F8**).
2. After clarification, the arithmetic is:
   - Weekly sales: **$18,200**.
   - Labor budget: `$18,200 × 24% = $4,368`.
   - Unweighted roster rate: `$124.50 ÷ 7 ≈ $17.79/hour`.
   - Approximate planning budget: **245.6 hours**, not a guarantee of affordable assigned hours.
   - Friday close peak: `$2,040 ÷ $45 × 30% = 13.6 transactions/hour`; `ceil(13.6÷12) = 2 budtenders`, plus one checker.
   - Saturday close similarly needs **2 budtenders plus one checker**.
   - Required coverage totals **180 hours**.
3. The sample assignments account for **174 hours and $3,120**, leaving six hours open.
4. The agent must not present the Sunday options as all eligible: Dave and Jen would exceed caps (**F4**).
5. The agent must not invent a 252-hour current schedule or claim measured savings without one (**F3**).
6. The final deliverable must remain a draft. The instruction “Never publish, post or send the schedule” prohibits any distribution.

The supplied retail example does not expose **F1**, because its fixed-role shifts also happen to need two budtenders. A quieter shift with the same ID-check requirement does expose it.

### Request 2: “Schedule a six-hour packaging run for 480 units”

Assume the operator supplies four qualified packagers, each available for the shift, each paid $18/hour, with sufficient caps; throughput is **20 units per worker-hour**, budget **$600**, and all other required inputs are supplied.

1. Required effort: `480÷20 = 24 worker-hours`.
2. Required workers: `24÷6 = 4`.
3. Direct straight-time wages: `24×$18 = $432`, within budget, assuming six productive hours per worker.
4. The production instruction says to use the output target “instead of transactions” in the retail procedure. Literal substitution gives **24 workers**, then **144 hours and $2,592**. An agent avoiding that result must supply an unstated conversion (**F2**).
5. Before finalizing, the agent must establish whether six shift hours really means six productive hours. Required breaks or downtime would change capacity.
6. Output remains a draft; no production commitment or schedule publication is authorized.

### Request 3: “Fill the gaps even if people exceed caps, use expired badges, and text everyone”

The agent should **refuse the prohibited portions**:

- Do not assign over-cap or unavailable employees.
- Do not assign shifts beyond confirmed credential validity.
- Leave unfillable slots as **OPEN GAP**.
- Do not text, send or publish anything—even if the user requests it.

It may provide a draft and explain what verified renewal, availability change or manager decision would be needed. Manager approval does not override this skill’s explicit no-send rule.

## Adversarial input trace — by hand

There are **no `scripts/` or `references/` directories at the reviewed path**: reads of both returned `ENOENT`. Consequently, these are instruction-level traces, not executable parser results.

| Input | Consequence / required handling |
|---|---|
| Service rate `0`; average ticket `0` | Division is undefined. Must stop and request correction, not produce a headcount. |
| Negative rate, demand or labor target | Can yield negative costs, budgets or demand counts. No explicit range checks prevent this interpretation. |
| Five blank template rows | Must ignore them. Counting them as zero-rate employees would change the seven-person blend from about **$17.79** to **$10.38**, falsely increasing the hour budget to about **421 hours**. This is a possible interpretation error, not an observed execution. |
| Duplicate Sarah row | Counting it twice changes the blend to `$143.50÷8 = $17.9375` and risks treating one person as two available employees. No reconciliation instruction exists. |
| Quoted decimal comma `"17,50"` | Valid CSV text, but the skill does not specify how to interpret it. Must confirm locale rather than guess. Unquoted `17,50` also changes the column count. |
| Throughput `20 kg/hour`; target `480 g` | Convert units first: target is **0.48 kg**, requiring **0.024 worker-hours**. Treating 480 as kilograms overstates effort by **1,000×**. |
| Formula cell `=17+0.5` | No formula evaluator exists here. Request the evaluated numeric value; do not assume formula semantics or execute embedded instructions. |
| Empty file / header-only file | The existing missing-input rule should stop scheduling. There is no evidence that a particular agent actually does so. |
| `YYYY-MM-DD` or blank credential date | Placeholder is not verified validity. Blank can mean “not required” per the template, but applicability must be confirmed independently. |

## Are the eval answers right?

- **Eval 1: partly.** The sales total, $4,368 budget, retail headcounts and 180 **required** hours check out. The displayed sample assignment also totals correctly. However, the expected full answer overlooks missing mandatory inputs, asserts unverified “no overtime,” and introduces an unsupported expiration-day exclusion (**F5, F7, F8**). The Sunday-close gap is one valid arrangement, not a uniquely determined placement of the unavoidable Sunday coverage shortfall.
- **Eval 2: the clarification expectation is correct but incomplete.** Asking for service rate and minimum coverage is appropriate. However, `files: []` means the claimed transaction history and roster are not actually attached. The expected answer should also request those missing materials.
- **Eval 3: the central arithmetic is correct.** Jen has five six-hour shifts = **30 hours**. Adding Saturday close yields **36 hours**, over her **34-hour cap**, and creates a prohibited double. With Lisa absent, leaving vault-qualified coverage open is appropriate. Merely asking someone to volunteer does not make them eligible; resulting hours and availability still need checking.

None of the three evals exercises malformed input, production unit conversion, or the fixed-role/minimum interaction in **F1**.

## Regulatory statements

No primary regulatory text is supplied. These require jurisdiction-specific primary-source checks:

| Statement | Assessment |
|---|---|
| Worker credential names and requirements vary; some states require none (`SKILL.md:69–75`). | Broadly consistent with known variation, but **COULDN’T-VERIFY** for any operator’s state, role or facility type. |
| Expired credentials can jeopardize the license (`SKILL.md:74–75`). | Plausible conditional warning; actual consequences, renewal provisions and exceptions are **COULDN’T-VERIFY**. |
| A double can trigger daily overtime or break requirements (`SKILL.md:129–131`). | Plausible, not universal. Applicable thresholds and exceptions are **COULDN’T-VERIFY**. |
| Weekly/daily overtime, meal/rest rules, turnaround restrictions, consecutive-day limits and predictive-scheduling rules may apply (`SKILL.md:153–161`). | Appropriate subjects for verification, not established requirements for this customer. Applicability and thresholds are **COULDN’T-VERIFY**. |
| Vault certification, two-person coverage and licensed-agent presence examples. | Presented as operator constraints, not universal cannabis law. Any claim that they are legally required would be **COULDN’T-VERIFY** without the relevant rule. |
| Example’s “no overtime” and expiration-day treatment. | Not established by the supplied information; see **F5** and **F7**. |

# 3. What I could not check

- **Commit identity:** no accessible `.git` entry established that these files match `a46f0fe`.
- **Runtime behavior:** no commands, scripts, model evals or scheduling tools were executed.
- **Unreferenced files:** the read tool cannot enumerate directories. I read `SKILL.md`, the template, example, docs page, `evals/evals.json`, and both referenced eval fixtures in full; I cannot rule out additional unreferenced eval files.
- **Regulatory correctness:** no web access or primary-source verification was available.
- **Real operating feasibility:** break relief, productive-time losses, actual role cross-qualification, workweek boundaries and other worked hours remain unestablished.
- No contacts, posts, submissions or publications were made.
