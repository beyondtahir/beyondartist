# Sources and verification

Host documentation was checked against opened primary pages on **15 October 2026**. This verifies the written setup route, not successful image production on every host. The local skill tests and release checks are documented separately in [validation](validation.md).

## Host setup and automation

All pages below were actually opened on 2026-10-15. Commands and UI labels should be rechecked when updating the distribution; installation itself was not executed.

| Primary source | Verified use |
| --- | --- |
| [Claude Code quickstart](https://code.claude.com/docs/en/quickstart) | Native installer, launch, authentication |
| [Claude Code skills](https://code.claude.com/docs/en/skills) | Discovery paths, symlinks, invocation, Cowork account loading |
| [Claude custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) | Packaging structure and metadata constraints |
| [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) | Upload UI, enablement, policies |
| [Customize Cowork](https://academy.claude.com/tutorials/customize-claude-cowork) | Connector/plugin versus skill responsibilities |
| [Gemini CLI installation](https://geminicli.com/docs/get-started/installation/) | npm installation, Node prerequisite |
| [Gemini CLI skill management](https://geminicli.com/docs/cli/using-agent-skills/) | Link command, user/workspace scope, reload, activation consent |
| [Gemini CLI skill tutorial](https://geminicli.com/docs/cli/tutorials/skills-getting-started/) | Frontmatter, discovery, trusted workspace |
| [Gemini Apps Skills](https://support.google.com/gemini/answer/17094296?hl=en) | Native upload, account availability, shortcuts, 100 MB, script restrictions |
| [Use Gemini Gems](https://support.google.com/gemini/answer/15146780?hl=en) | Gem creation and knowledge files |
| [Gems transition](https://support.google.com/gemini/answer/18560919?hl=en) | November 2026 / 2027 transition |
| [Gemini Apps images](https://support.google.com/gemini/answer/14286560?hl=en) | Host generation/editing and download workflow |
| [Hermes quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Installer and model setup |
| [Working with Hermes skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills) | Standard directory, invocation, session refresh |
| [Hermes Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | GitHub path installs and supporting folders |
| [Hermes tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) | Configured image tool and credentials |
| [Hermes image generation](https://hermes-agent.nousresearch.com/docs/user-guide/features/image-generation) | Provider setup, editing and output limitations |
| [Hermes cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Gateway requirement, attached skills, create/manage/status commands |
| [Meet dots](https://learn.chatgpt.com/docs/dots) | Official product identity, cloud computer, gradual access |
| [Dots setup](https://learn.chatgpt.com/docs/dots/getting-started) | Device setup and connected-computer requirements |
| [Dots apps/computers](https://learn.chatgpt.com/docs/dots/computers-and-apps) | Enabled plugins and local-skill environment requirement |
| [Dots tasks/memory](https://learn.chatgpt.com/docs/dots/tasks-and-memory) | Recurring schedules and notification controls |
| [Grok Bot announcement](https://x.ai/news/introducing-grok-bot) | Official identity and always-on cloud agent |
| [Grok Bot setup](https://cursor.com/docs/grok-bot/get-started) | Supported app setup and account access |
| [Work with Grok Bot](https://cursor.com/docs/grok-bot/work) | Attachments, save/invoke native skill, private skill enablement |
| [Grok Bot routines](https://cursor.com/help/grok-bot/routines) | Schedule UI, time zone, testing, management |

Additional OpenAI sources opened during repository preparation:

- [Build skills](https://learn.chatgpt.com/docs/build-skills): local discovery, invocation and plugin distribution.
- [Package a plugin](https://developers.openai.com/plugins/build/plugins): portable manifest and relative asset paths.
- [Skills and Plugins](https://learn.chatgpt.com/docs/skills-and-plugins): workflow and tool packaging distinctions.
- [Work with files](https://learn.chatgpt.com/docs/artifacts-viewer?surface=app): accessible file-based context and review.
- [Scheduled tasks](https://learn.chatgpt.com/docs/automations): desktop/web scheduling and runtime context.

## Design knowledge

The shared library preserves the original source links, inspection depth, dates, observation/interpretation distinction and metric limits in each canonical study. [Library index](../skills/beyondartist/references/library-index.md) and [methodology](../skills/beyondartist/references/methodology.md) explain coverage. Repository preparation did not repeat live Pinterest research or re-inspect every historical source image. The artist reviewed the actual supplied showcase and rendered page.

[Back to BeyondArtist](../README.md)
