# Start creating with BeyondArtist

Host documentation checked **15 October 2026**. These routes are based on official documentation; runtime production was not tested on every listed host. BeyondArtist supplies the creative workflow and memory helpers. Your agent supplies the model, image/design tools, browser, vision, credentials and scheduler.

## Get the complete skill

Clone or download this repository. Keep the full <code>skills/beyondartist</code> directory: its references and scripts are part of the skill.

~~~sh
git clone https://github.com/beyondtahir/beyondartist.git
cd beyondartist
~~~

For an account upload, download the **skill-only ZIP** from [Releases](https://github.com/beyondtahir/beyondartist/releases). It has one top-level <code>beyondartist/</code> folder containing <code>SKILL.md</code> and all supporting files. The full repository ZIP is a separate download and includes the showcase.

## Codex — desktop, CLI or IDE

From the repository root:

~~~sh
python3 scripts/install.py --host codex
~~~

The installer copies the full skill into <code>~/.agents/skills/beyondartist</code> and refuses to overwrite an existing installation. A project-scoped alternative is <code>.agents/skills/beyondartist</code>. Use <code>$beyondartist</code> or select it from <code>/skills</code>; restart if discovery does not refresh. [Official local discovery and invocation](https://learn.chatgpt.com/docs/build-skills).

~~~text
$beyondartist Create one thumbnail for [known video topic]. Use my attached
references, propose a fitting title and handle the creative decisions.
~~~

## Claude Code

Install and authenticate Claude Code first using its [official setup](https://code.claude.com/docs/en/quickstart), then:

~~~sh
python3 scripts/install.py --host claude
claude
~~~

Invoke <code>/beyondartist</code>. Claude Code discovers the personal folder <code>~/.claude/skills/beyondartist</code>; repository-scoped skills go in <code>.claude/skills</code>. A fresh session should discover the full directory. Confirm the actual image tool before requesting finished raster work. [Claude Code skills](https://code.claude.com/docs/en/skills).

## Claude Cowork

Enable **Code execution and file creation** where required. Open **Customize → Skills → + → Create skill → Upload a skill**, upload the skill-only ZIP and enable it. Start a new Cowork session and request BeyondArtist. Cowork uses account-enabled skills; it does not load your local Claude Code skill folder. Organization settings can restrict uploads. [Account skill upload](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [Cowork loading](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions).

## ChatGPT Work

In the desktop app, use the accessible local skill and select it with <code>@beyondartist</code> when it appears in Skills. For a file-based start, attach the skill-only ZIP to Work and ask it to unpack/read <code>SKILL.md</code> and the supporting references before the brief. Confirm file access and available creation tools.

Native cross-surface distribution uses enabled plugins. This repo includes a portable plugin manifest; that does **not** mean it has been accepted into the universal plugin directory. Where a workspace supports local/custom plugin installation, follow its supported route; otherwise use accessible files. A hosted session does not automatically inherit your local private memory folder. [Skills versus plugin distribution](https://learn.chatgpt.com/docs/build-skills), [Work with files](https://learn.chatgpt.com/docs/artifacts-viewer?surface=app).

## Gemini Apps — native Skills

At <code>gemini.google.com</code>, open **Customize → Skills** (or **More → Customize**), choose **Upload**, select the complete skill folder or skill ZIP, review the instructions and choose **Create**. In a chat, select it through the skill shortcut shown by your account (<code>/</code> or <code>@</code>).

Availability depends on rollout/account eligibility. Official guidance currently specifies personal accounts, age 18+ and Keep Activity enabled; uploads have a 100 MB total limit. Uploaded scripts cannot make internet requests or perform external-site actions. The included memory/retrieval helpers are local, but durable storage still needs verification. [Gemini Apps Skills](https://support.google.com/gemini/answer/17094296?hl=en).

For accounts still using Gems, create a **New Gem**, add the workflow instructions and relevant Knowledge files, then save. This is a transitional adaptation; Google documents the personal-account move toward Skills from November 2026. [Gems setup](https://support.google.com/gemini/answer/15146780?hl=en), [transition](https://support.google.com/gemini/answer/18560919?hl=en). Use the host’s available [image generation/editing](https://support.google.com/gemini/answer/14286560?hl=en).

## Gemini CLI

Install the CLI using its [official prerequisites](https://geminicli.com/docs/get-started/installation/), then link from the repository root:

~~~sh
gemini skills link ./skills/beyondartist --scope user
gemini
~~~

Run <code>/skills reload</code> and <code>/skills list</code>, then request the beyondartist skill. Activation and workspace access follow the CLI’s consent/trust controls. The CLI needs a configured image/design service for finished visuals. [Gemini CLI skill management](https://geminicli.com/docs/cli/using-agent-skills/).

## Hermes Agent

Configure Hermes and a working model/provider using its [quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart), then:

~~~sh
python3 scripts/install.py --host hermes
hermes skills list
hermes
~~~

Invoke <code>/beyondartist</code> in a fresh session. The default copy destination is <code>~/.hermes/skills/beyondartist</code>; for another profile use the installer’s explicit <code>--destination</code>. A supported remote alternative is:

~~~sh
hermes skills install beyondtahir/beyondartist/skills/beyondartist
~~~

Configure image generation through <code>hermes tools</code> if needed. Providers, credentials, editing support and costs belong to the host configuration. [Hermes skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills), [image setup](https://hermes-agent.nousresearch.com/docs/user-guide/features/image-generation).

## Dots and Grok Bot

**Dots:** set up your dot, enable its permitted plugins and connect the computer containing the local skill when local access is needed. Ask it to confirm BeyondArtist’s files and image/design tools are accessible. A repository URL alone is not an installed integration. Account access is rollout-dependent. [Dots setup](https://learn.chatgpt.com/docs/dots/getting-started), [computers and skills](https://learn.chatgpt.com/docs/dots/computers-and-apps).

**Grok Bot:** attach the workflow and supporting files, run one concrete job, then ask the Bot to save the reusable workflow as a skill named beyondartist. Select it with <code>/</code>; enable the private skill for that Bot if needed. This uses Grok Bot’s native saved-skill workflow, not an asserted lossless GitHub importer. [Official Grok Bot setup](https://cursor.com/docs/grok-bot/get-started), [skills and work](https://cursor.com/docs/grok-bot/work).

## First-use check

Ask your agent to confirm it can read the instructions and selected full library records; retrieve or initialize your own personal/project memory; inspect the supplied references; identify an actual image/design tool; and render/inspect the final work. Give it your platform, topic, audience, language and constraints when known.

If Python is unavailable, use the canonical Markdown and memory JSON manually. If browsing is unavailable, saved knowledge supports offline work with dated claims clearly labeled. If rendering is unavailable, the deliverable must say **Production specification — not a rendered design**. An uninspected render stays an unverified draft.

**[Starter briefs](../examples/briefs.md)** · **[Memory setup](memory.md)** · **[Daily automation](automation.md)** · **[Source ledger](sources.md)**
