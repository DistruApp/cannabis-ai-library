# Route: Claude

For Claude models: Claude.ai, the Claude desktop app, Claude Code and Cowork.
Codex agents read [codex.md](codex.md) instead.

## Where the dashboard lives

| Host | Build | Live data |
| --- | --- | --- |
| Claude.ai or the desktop app, with artifacts | An interactive **artifact** | The artifact's connector access to the user's connected Distru app |
| Claude Code (CLI, desktop Code tab, IDE) | A single-file HTML page in the project, published as an artifact if the session can publish one | Only if the page has a supported live-data capability; otherwise a labelled snapshot |

Build prompt: [create-claude-artifact.txt](../prompts/create-claude-artifact.txt).
In Claude Code, read "artifact" there as "the page above".

## Artifacts (Claude.ai and the desktop app)

- Confirm artifacts and connected apps are available in this account, then find
  the connected Distru app and verify the company.
- Use the artifact runtime's documented connector interface. Do not guess
  JavaScript bridge APIs, reuse ChatGPT Sites server bindings, or put credentials
  in artifact code.
- As documented when this was written: artifacts can use custom connected apps,
  each viewer authorizes their own connections, and tools that need per-action
  approval do not run inside artifacts. If that blocks a read, report the exact
  limitation; do not change connector approval settings for the user.
- Make one in-artifact read (company or a bounded inventory page) and Refresh
  work before building the full page.
- Keep the user's sharing scope. Creating an artifact does not mean publishing it.

## Claude Code

- Start from [the reference dashboard](../assets/expiring-inventory-dashboard.html):
  its layout, brand and interactions are the target.
- Read the data through the session's Distru tools (MCP) at build time. A file on
  disk cannot refresh itself: label it a snapshot with its read time, and make
  "Refresh" mean re-running the build, unless the publishing host gives the page
  a supported live-data capability. Then use that and verify it.
- Verify the rendered page in a browser, not only the code.

## Handing the email to Claude

The dashboard opens the brief in Claude, the user sends it, and Claude drafts
the email in that chat. Offer:

1. **Open in Claude**: a link to `https://claude.ai/new?q=` + the URL-encoded
   brief. It opens a new chat with the brief in the composer and does not send.
   Verify it in the user's browser; very long briefs may be cut by URL limits,
   so fall back to Copy for those.
2. **Copy brief**: always present, for pasting into any Claude chat, including
   Claude Code.

Inside an artifact, use a documented handoff to the current conversation if the
runtime has one; otherwise the two options above. Never auto-submit, never
invent a bridge, never embed a separate model call to write the email.

The reference dashboard does this when opened with `?agent=claude`.

## Installing this skill in Claude

- Claude.ai / desktop: zip the `distru-expiring-inventory` folder (the folder
  itself, with `SKILL.md` at its top) and upload it under Settings → Capabilities
  → Skills. Check that it appears there; attaching a ZIP to a chat is not install.
- Claude Code: copy the folder to `~/.claude/skills/` (personal) or
  `.claude/skills/` in a project.
- `agents/openai.yaml` is Codex metadata; Claude ignores it.

Sources (checked November 5, 2026):
- [Artifacts and connected apps](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them)
- [Custom skill authoring](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Use and upload skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

These describe what the hosts support, not a completed live run of this skill.
