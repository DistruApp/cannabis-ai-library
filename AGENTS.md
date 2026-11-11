Skills are organized into two areas under `skills/`:

- `cannabiz-skills/`: general skills for any licensed cannabis business, working from uploaded files with no connectors. Split into buckets:
  - `cannabiz-skills/compliance/`: state rules, inspections, traceability, transfers and SOPs
  - `cannabiz-skills/operations/`: cost, yield, purchasing and staffing
- `distru-skills/`: skills that read the user's Distru data through the Distru MCP. One folder per skill, no buckets yet.

Beta or unreleased skills are developed in the internal staging repo, not here.

Every skill in `cannabiz-skills/` or `distru-skills/` (the **promoted** areas) must have a reference in the top-level `README.md` and an entry in the `skills` array of both `.claude-plugin/plugin.json` (Claude Code) and `.codex-plugin/plugin.json` (Codex). Both plugins ship exactly the promoted set, and the two arrays must match. Keep `version` and `description` the same in both manifests.

`.claude-plugin/marketplace.json` is the repo's own marketplace. Claude Code and Codex both read it. Run `claude plugin validate . --strict` after touching any manifest.

Everything in this repo is MIT licensed (see `LICENSE`). A skill's `license` frontmatter, when present, says `MIT`.

Each skill entry in the top-level `README.md` must link the skill name to its `SKILL.md`.

Each area and bucket folder has a `README.md`. The `README.md` that directly contains skills lists every one of them with a one-line description, with the skill name linked to its `SKILL.md`.

Promoted skills also have a human-facing docs page whose path mirrors the skill's path under `skills/`: `docs/cannabiz-skills/<bucket>/<skill-name>.md` or `docs/distru-skills/<skill-name>.md`. These pages are the source for the Cannabis AI Library on distru.com. When you add, rename, or change the behaviour of a promoted skill, create or re-sync its docs page. A page carries four sections: **What it does**, **When to use it**, **How to use it**, and **Example**.

A skill's folder name must match the `name` in its `SKILL.md` frontmatter.

Skills here are public-facing. Before adding or changing one, check that it contains no customer names, real customer data, API keys, or internal links. Test fixtures use fictional businesses and `example` domains.

To (re)link every skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current; re-run the script after adding, removing, or renaming a skill.

Before finishing any change, run `python3 scripts/check_repo.py` and `scripts/test-scripts.sh`, and fix what fails. A change to a bundled script needs a test in `tests/`. Releases follow `RELEASING.md`: never call a skill ready from reading it; say which evidence label (RUN, SCRIPT-TESTED, SOURCE-CHECKED, READ ONLY, NOT TESTED) backs each claim.
