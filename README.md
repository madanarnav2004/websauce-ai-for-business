# Websauce AI for Business

Practical, open-source ways for business owners to use AI. Start with a task you already do, try a small workflow, check the result, and keep what saves time or improves the work.

This is a Websauce education project for owners and small teams, including people who do not write code. It can hold plain-English guides, ChatGPT or Codex skills, reusable prompts, schedules, cloud examples and real case studies. Each item says what works today and what still needs building.

## Start here

1. Read [choose your first AI task](guides/choose-your-first-task.md). It helps you pick a repetitive, low-risk task with a clear result.
2. Use [the first-workflow worksheet](examples/first-workflow-worksheet.md) with your own non-sensitive example.
3. Follow [skill, schedule, or app?](guides/skill-schedule-or-app.md) to decide whether the workflow needs instructions, a timed run, or software.

You can use the guides with a chat assistant and copy the prompts directly. The Codex skill below is an optional deeper example.

## What is available

| Area | Resource | Status |
| --- | --- | --- |
| Getting started | [Pick a first task](guides/choose-your-first-task.md) and [worksheet](examples/first-workflow-worksheet.md) | **Ready**: manual exercise |
| Choosing a tool | [Skill, schedule, or app?](guides/skill-schedule-or-app.md) | **Ready**: plain-English guide |
| Marketing and enquiries | [Inbound engine skill](skills/inbound-engine/SKILL.md) with a [fictional example](examples/example-brief.md) and [worked output](examples/example-output.md) | **Ready**: agent instructions and local demo |
| Marketing operations | [Daily run template](docs/daily-run.md), [publication](docs/publication.md) and [measurement](docs/measurement.md) guides | **Ready**: templates, not installed automation |
| Real-world learning | [Websauce case study](docs/websauce-case-study.md) | **Dated example**: verify current facts before reuse |
| Customer support, internal operations, websites, cloud and data | [Roadmap](docs/roadmap.md) | **Planned**: no working module claimed yet |

## What we mean by a product

- A **guide** explains a task in ordinary language and gives a test a business owner can run.
- A **skill** is a reusable set of agent instructions and resources. The installed agent still needs the user's files, access and permission for external actions.
- A **schedule** asks an agent to return at a set time. It is not a background server and depends on the host, account sessions and available integrations.
- An **app or cloud workflow** is software that runs for users. We will label prototypes and deployed examples separately.

The [inbound-engine skill](skills/inbound-engine/SKILL.md) is the first skill here, not the subject of the whole repository. To try it from this clone, ask Codex to read that file and apply it to the fictional example. For repeated local use, copy the skill folder into your Codex skills directory (`~/.codex/skills/inbound-engine` on a default setup) and invoke `$inbound-engine`. Installing it does not publish content, connect an account or install a schedule.

## How we publish examples

Examples use synthetic information or clearly public Websauce work. We say when an action is a draft, a local queue item, a live publication or a measured result. The repository contains no private contacts, customer messages, credentials or live Websauce operating database. It does not promise leads, revenue or unattended operation.

Want to improve a guide or add a practical business use case? Read [contributing](CONTRIBUTING.md). This repository is MIT licensed; see [LICENSE](LICENSE).
