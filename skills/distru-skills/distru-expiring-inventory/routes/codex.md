# Route: Codex

For OpenAI models: the Codex app, the Codex CLI, Codex in an IDE, and ChatGPT
with Sites. Claude agents read [claude.md](claude.md) instead.

## Where the dashboard lives

| Host | Build | Live data |
| --- | --- | --- |
| ChatGPT with Sites | A private **ChatGPT Site** | The Site's server connector binding to the user's Distru connector |
| Codex app, CLI or IDE (no Sites tools) | A single-file HTML page in the workspace | A labelled snapshot read through the Distru MCP at build time |

Build prompt: [create-chatgpt-site.txt](../prompts/create-chatgpt-site.txt).
In the Codex app or CLI without Sites, read "Site" there as "the page above".

## ChatGPT Sites

- Follow the current Sites authoring instructions and tools; this package does
  not include a Sites runtime.
- A fresh build is a new Site in a new source directory. Do not copy
  `.openai/hosting.json` or another Site's project identity. When updating a
  Site, keep its project ID.
- Check Sites plugin eligibility before declaring connectors. Map the allowed
  plugin and connector IDs to the native tools actually available; recheck after
  account or workspace changes and before publishing.
- Build a dynamic Site on the provided server connector binding. Keep tool
  choice on the server and inputs limited to the discovered read schemas. No
  provider calls from browser code with copied credentials.
- Local preview may use the owning chat's connection while hosted calls use the
  visitor's authorization: test both.
- Make one identity or inventory read work in the real runtime first. Confirm
  Refresh makes a new provider read, not a re-render of exported JSON.
- Keep the Site private; do not widen an audience without the user saying so.
  Return the real hosted URL. Publishing alone does not verify the connector.

## Codex app, CLI or IDE

- Start from [the reference dashboard](../assets/expiring-inventory-dashboard.html):
  its layout, brand and interactions are the target.
- Read the data through the Distru MCP tools in this session. A local file cannot
  refresh itself: label it a snapshot with its read time and make "Refresh" mean
  re-running the build. Do not call it live.
- Open the result in a browser and check the screens, not only the code.

## Handing the email to ChatGPT

The dashboard opens the brief in ChatGPT, the user sends it, and ChatGPT drafts
the email in that chat. Offer:

1. **Open in ChatGPT desktop**: `codex://new?prompt=` + the URL-encoded brief.
   It opens a new chat in the desktop app with the brief ready, unsent.
2. **Open in ChatGPT web**: `https://chatgpt.com/?q=` + the URL-encoded brief,
   in a new tab.
3. **Copy brief**: always present. Use it when a link is too long or the user is
   in another app.

Verify each link on the user's machine; they prefill a composer, nothing more.
Never auto-submit or assume a connector gets selected in the new chat. Inside a
Site, follow the current supported handoff; a private Site URL does not give a
chat access to its data.

The reference dashboard does this by default (no `?agent=` parameter).

## Installing this skill in Codex and ChatGPT

- Codex: copy the `distru-expiring-inventory` folder to `~/.codex/skills/`, or to
  the skills folder of the workspace, then invoke it as `$distru-expiring-inventory`.
  `agents/openai.yaml` supplies its display name and default prompt.
- ChatGPT workspace skills are installed separately from a local Codex skill. If
  this host cannot install workspace skills, hand over the folder and follow its
  instructions explicitly; do not claim it is installed.

Sources (checked November 5, 2026):
- [Sites connected data](https://learn.chatgpt.com/docs/sites/data-and-connections)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)

These describe what the hosts support, not a completed live run of this skill.
