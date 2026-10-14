# Put the creative workflow to work daily

BeyondArtist can be the design workflow inside a recurring agent job. The host owns the schedule and execution environment. Install/access the skill, test one ordinary run, then explicitly request the schedule, time zone, output destination, budget and notification behavior.

## Useful recurring jobs

| Job | Input | Reviewable result |
|---|---|---|
| Weekly creative radar | Niche, audience and permitted research sources | Dated references, observed mechanisms and three original creative angles |
| Daily post draft | Approved content queue and brand context | One finished draft and a concise art-direction note |
| Client campaign batch | Accepted brief, formats and asset permissions | Consistent draft variants and exports for client review |
| Carousel production | Verified topic material and desired slide count | A complete sequence with exact copy and visual checks |
| Feedback learning | User-supplied approvals, rejections or real metrics | Scoped preference/project updates with actual provenance |

Use an inbox or review folder as the default result destination. Publishing or client delivery is a separate requested action. The workflow can generate daily art only when the scheduler’s environment has working generation, file and vision tools. Do not schedule an image job that can only produce text.

## One reusable recurring-job prompt

~~~text
Use BeyondArtist for [project]. At [cadence, time and time zone], read the next
approved item from [accessible queue]. Retrieve this user's brand and project
memory. Research relevant examples when browsing is available; label offline
research otherwise. Create [deliverable and count] with the available tools.
Inspect exact copy, hierarchy and medium at full and realistic viewing size.
Save the draft, decision note and memory update to [destination].
Stop and report if the brief, source facts or required tools are missing.
Use [explicit generation budget]. Notify me when a draft is ready or needs input.
Do not publish or send it to a client as part of this job.
~~~

This is a synthetic recipe. Fill its variables and test it before scheduling. The system learns from actual feedback; it does not invent audience results.

## ChatGPT Work / Codex desktop

Ask ChatGPT to create the recurring task with BeyondArtist explicitly selected in the prompt. Review it in **Scheduled**. Desktop jobs that use local projects need that computer and the app running; web jobs use accessible uploads/connected sources and do not keep a local folder between runs. Codex CLI/IDE can prepare a job but do not supply the Scheduled management UI. [Official scheduled-task guidance](https://learn.chatgpt.com/docs/automations).

## Dots

Ask your dot to run the workflow at the stated cadence and confirm the saved schedule. Review it in **Scheduled**, with the required files/tools available through its installed plugins or connected computer. State the notification rule in ordinary language. [Dots tasks and memory](https://learn.chatgpt.com/docs/dots/tasks-and-memory).

~~~text
Every Monday at 9 AM [my time zone], use BeyondArtist to inspect references for
[niche] and return a source-linked creative brief here. Notify me when it is
ready or an essential input is missing. Confirm the saved schedule.
~~~

## Hermes

Hermes’ gateway runs its cron scheduler. Start it, then create an explicitly requested job from another terminal:

~~~sh
hermes gateway
~~~

~~~sh
hermes cron create "0 9 * * 1" \
  "Use BeyondArtist to research the supplied niche. Return dated sources and three creative angles here. No paid generation or publishing." \
  --skill beyondartist --name "BeyondArtist weekly creative radar"
hermes cron list
hermes cron status
~~~

Verify the configured time zone, gateway uptime and tools. Use <code>hermes cron pause &lt;job_id&gt;</code> or <code>hermes cron remove &lt;job_id&gt;</code> to manage the job. [Official Hermes cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron).

## Grok Bot

After saving the BeyondArtist workflow as a native skill, ask the Bot to run it at the desired cadence. Inspect **Details → Routines**, including **Instruction** and **When to run**, and confirm **Settings → Bot → Timezone**. Use its Test/Pause/Resume controls as appropriate; Test executes real work. [Grok Bot routines](https://cursor.com/help/grok-bot/routines).

## Claude Cowork / Gemini

Where the account exposes scheduling, attach the enabled workflow to its supported task mechanism and confirm the tools and context available during unattended runs. Cowork uses account-enabled skills in scheduled sessions, rather than the local Claude Code folder. The Gemini Skills upload route alone does not establish a recurring image-production scheduler. [Cowork skill loading](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions).

**[Installation](getting-started.md)** · **[Memory](memory.md)** · **[Production process](creative-system.md)**
