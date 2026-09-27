# Websauce GTM

An open, agent-first playbook for building an inbound loop with Codex. This repository is a **working method and reusable skill**, not a hosted lead-generation product.

The loop is: learn from real work → publish a useful answer → offer one clear next step → check that enquiries arrive → measure conversations → improve the next piece. Websauce is the public case study. The reusable [inbound-engine skill](skills/inbound-engine/SKILL.md) has no Websauce account or customer data.

## Start in five minutes

1. Clone this repository and read [the example brief](examples/example-brief.md).
2. Give Codex this prompt: **“Use the inbound-engine skill in this repository to create an inbound experiment from examples/example-brief.md. Save the output locally; do not publish.”**
3. Review the resulting topic, draft, landing-page check and measurement plan.
4. Replace the example with your own business facts and real customer questions.

A [worked example](examples/example-output.md) shows the expected shape without accessing any account.

For repeated use in Codex, copy `skills/inbound-engine` into your Codex skills directory (`~/.codex/skills/inbound-engine` on a default local setup), then invoke `$inbound-engine`. You can also ask Codex to read the skill file directly from this clone. Installing the skill does not install a schedule or connect an account.

The skill can research, draft, check and learn. Publishing, sending messages and changing live pages require the user's authorization and the available account access. There is **no paid API, scraper, background server or account login** in this repository. The example works as a local planning run.

## What's here

- [Inbound engine skill](skills/inbound-engine/SKILL.md): the reusable agent workflow.
- [Daily operating template](docs/daily-run.md): a bounded manual or scheduled run.
- [Publication protocol](docs/publication.md): avoid duplicate posts and misleading success claims.
- [Measurement guide](docs/measurement.md): count actual enquiries and qualified conversations.
- [Websauce case study](docs/websauce-case-study.md): what has really happened, without private records.
- [Example brief](examples/example-brief.md): fictional inputs to try the workflow.
- [Product roadmap](docs/roadmap.md): what's next and what is still missing.

## Scope

“Inbound” here means content and discoverability connected to a working enquiry path. Cold outreach is a separate channel. A generated post is an asset, not demand; an enquiry is not revenue. At the time of this first release, the Websauce operator records work in a private local ledger and runs from a personal Codex schedule. That ledger and its real records are not in this repository, and this repo does not create a schedule automatically.

## Contributing

Small, tested improvements to the skill, examples and documentation are welcome. Use synthetic examples. Do not add real leads, customer messages, private identifiers, authentication data, browser exports or unlicensed media.

MIT licensed; see [LICENSE](LICENSE).
