# Contributing

Distru builds, tests and maintains the skills in this library.

## Suggest a skill or report a problem

Open a [GitHub issue](https://github.com/DistruApp/cannabis-ai-library/issues). Tell us:

- what you were trying to do, and in which app (Claude, ChatGPT/Codex, or another agent);
- which skill you used and what it produced;
- for a bug, the input that caused it. Remove customer names and other real data first.

## Pull requests

Small fixes are welcome: typos, broken links, clearer wording. For a new skill or a change to how a skill behaves, open an issue first so we can agree on the approach before you spend time on it.

Every file in a pull request must follow these rules:

- No API keys, tokens or credentials. Use environment variables.
- No real customer or business data, including in test fixtures. Use clearly fictional names (for example "Example Leaf Provisions") and `example` email domains.
- A skill's folder name matches the `name` in its `SKILL.md`.
- Everything is MIT licensed (see [LICENSE](./LICENSE)).
