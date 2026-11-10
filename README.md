<p>
  <a href="https://www.distru.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="./assets/distru-logo-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="./assets/distru-logo-light.svg">
      <img alt="Distru" src="./assets/distru-logo-light.svg" width="248">
    </picture>
  </a>
</p>

# Cannabis AI Library

Agent skills for running a licensed cannabis business, from [Distru](https://www.distru.com).

**Website:** [distru.com](https://www.distru.com)

Each skill is a small folder with a `SKILL.md` and whatever scripts, references and templates it needs. They work in Claude, ChatGPT/Codex and any agent that supports the Agent Skills format. Most need no connectors: you upload your own exports (Metrc, BioTrack, POS, ERP) and the skill does the rest. Where math matters, a bundled Python script does it, so the numbers come out the same every run.

These skills are built for operators, not engineers. They never submit anything to a state system, never send email, and never fill in a missing rate or regulation by guessing. Anything they can't verify is flagged for a human to confirm.

## Installation

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add DistruApp/cannabis-ai-library
claude plugin install cannabis-ai-library@distru
```

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add DistruApp/cannabis-ai-library
codex plugin add cannabis-ai-library@distru
```

</details>

<details>
<summary><strong>Claude.ai or Claude Desktop</strong></summary>

Zip the skill folder you want (for example `skills/cannabiz-skills/compliance/cannabis-state-rules-lookup`) and upload it under **Settings → Capabilities → Skills**.

</details>

<details>
<summary><strong>Any other agent</strong> (Cursor, OpenCode and others)</summary>

```bash
npx skills@latest add DistruApp/cannabis-ai-library
```

</details>

## Reference

All skills below are model-invoked: you can call them by name, and the agent will also reach for them when your request fits. They live in two areas:

| Area | What's in it | Needs |
| --- | --- | --- |
| [Cannabiz skills](./skills/cannabiz-skills/README.md) | General skills for any licensed cannabis business | Nothing beyond your own exports |
| [Distru skills](./skills/distru-skills/README.md) | Skills that work with your Distru data | A Distru account connected to your agent (Distru MCP) |

## Cannabiz skills

### Compliance

State rules, inspections, traceability and transfers.

- **[cannabis-state-rules-lookup](./skills/cannabiz-skills/compliance/cannabis-state-rules-lookup/SKILL.md)**: Answer state cannabis rule questions with a cited, dated answer from primary sources. Flags anything it can't verify instead of guessing.
- **[cannabis-inspection-readiness](./skills/cannabiz-skills/compliance/cannabis-inspection-readiness/SKILL.md)**: Prepare for a state inspection or audit with a readiness checklist, binder index, gap list with owners and due dates, and mock inspection questions.
- **[cannabis-traceability-reconciliation](./skills/cannabiz-skills/compliance/cannabis-traceability-reconciliation/SKILL.md)**: Compare a Metrc or BioTrack export with a physical count or ERP export and produce a discrepancy report with likely causes. Adjustments are drafts only.
- **[cannabis-transfer-manifest-precheck](./skills/cannabiz-skills/compliance/cannabis-transfer-manifest-precheck/SKILL.md)**: Check an outgoing B2B transfer against the sales order and active inventory with lab status. Returns GO or HOLD per line with the fix needed.
- **[cannabis-sop-generator-trainer](./skills/cannabiz-skills/compliance/cannabis-sop-generator-trainer/SKILL.md)**: Turn a described process into a licensing-ready SOP, then build a training packet with a quick reference, comprehension check and sign-off log.

### Operations

Cost, yield, purchasing and staffing.

- **[cannabis-batch-cogs](./skills/cannabiz-skills/operations/cannabis-batch-cogs/SKILL.md)**: Calculate the true cost of a manufacturing batch from its BOM, labor, overhead and testing, with cost per unit, yield variance and a sensitivity table.
- **[cannabis-harvest-yield-analysis](./skills/cannabiz-skills/operations/cannabis-harvest-yield-analysis/SKILL.md)**: Analyze harvests by batch, strain and room: dry-down, yield per plant, square foot and light, flower and trim mix, and cost per gram.
- **[cannabis-replenishment-planner](./skills/cannabiz-skills/operations/cannabis-replenishment-planner/SKILL.md)**: Turn sales and on-hand exports into a reorder plan with days of supply, stockout and dead stock flags, and a draft PO by vendor.
- **[staff-scheduling-optimizer](./skills/cannabiz-skills/operations/staff-scheduling-optimizer/SKILL.md)**: Recommend staffing by shift from real demand, a labor budget and availability. Flags overtime risk, coverage gaps and agent card expirations.

## Distru skills

These read your live Distru data through the Distru MCP. Connect your Distru account to Claude or ChatGPT first.

- **[distru-expiring-inventory](./skills/distru-skills/distru-expiring-inventory/SKILL.md)**: Build a dashboard of stock about to expire, the customers who already buy it, and a promo email brief for each one that your agent drafts for you to review. Never sends or changes Distru.

## Contributing

Suggestions and bug reports are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE)

## Disclaimer

These skills are not legal, tax or compliance advice. Every regulatory citation, threshold and deadline a skill produces should be confirmed with your compliance lead, counsel or CPA before you act on it.
