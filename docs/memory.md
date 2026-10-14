# Memory that grows with each user

BeyondArtist uses retrievable files rather than relying on an agent to recall every past chat. The shared knowledge travels with the skill. Personal and project records stay in a separately scoped store that each installer creates for themselves.

## Three layers, three jobs

| Layer | Location | Role |
|---|---|---|
| Shared Design Memory | <code>skills/beyondartist/references/</code> | Generalized instructions and source-linked lessons about design, art, typography, palette, hierarchy, format and research |
| Personal memory | Private profile outside the repo/skill | User-supplied identity, scoped preferences, brand rules, useful assets and actual approvals/rejections |
| Project memory | Records under that profile with a project ID | Working brief, observations, concepts, handoffs, outputs, revisions and feedback for one job |

Shared study counts: 95 foundations, 700 Pinterest previews, 54 style panels, seven seeds and 100 qualified thumbnail references. Preview scope and metric limits remain part of each source. The library is written knowledge with a derived retrieval index, not model-weight training or a pretrained likeness model.

## A normal job

The agent retrieves relevant private context before asking known questions, then searches shared lessons by the needed decision. It saves consequential answers and assumptions, creates the handoff, records outputs as drafts and updates feedback when the user actually approves or rejects them. An approved series may define consistency for that project; it must not become a global style for everybody.

Each record has a stable ID, type, scope, tags, text/data, provenance, status and revision history. Copied assets retain a checksum and profile-relative path. The helper searches tags, titles and text; shared retrieval uses deterministic lexical ranking. Neither is visual-similarity or semantic search.

## Initialize your own profile

From the repo root, with Python 3.9+:

~~~sh
python3 skills/beyondartist/scripts/user_memory.py init \
  --person local-user --name "Local User" \
  --project launch-series --project-name "Launch series"

python3 skills/beyondartist/scripts/user_memory.py context \
  --person local-user --project launch-series --query "brand palette" --limit 4

python3 skills/beyondartist/scripts/retrieve_library.py \
  --query "carousel hook narrative payoff" --corpus guides --limit 3 --full
~~~

The default root is <code>~/.beyondartist/memory</code>. A leading <code>--root /path/to/private/persistent-memory</code> or <code>BEYONDARTIST_MEMORY_HOME</code> can select another writable durable location. Do not put it inside this repository or the installed skill. Python is optional for manual Markdown/JSON reading; the helpers need only its standard library.

## Save useful records and assets

Use a scoped JSON record following [the canonical schema](../skills/beyondartist/references/personal-and-project-memory.md), then:

~~~sh
python3 skills/beyondartist/scripts/user_memory.py put \
  --person local-user --project launch-series --input decision.json

python3 skills/beyondartist/scripts/user_memory.py put \
  --person local-user --project launch-series --input reference.json \
  --asset /absolute/path/to/your-reference.png

python3 skills/beyondartist/scripts/user_memory.py validate --person local-user
~~~

An artifact is a draft until there is actual user-approval evidence. Reusing an ID retains revision history. Store copied assets when they are authorized and needed, so losing the original path does not silently break the project.

## Offline and cross-host operation

With no browser, use private context plus shared lessons and state that research is offline. Do not present dated observations as current trends. If a host cannot persist files, export the memory JSON and assets for the user to retain; do not promise future automatic recall. To move between machines, privately transfer the complete profile and referenced assets, configure the same memory root and validate it. Hosted chats may require re-uploading this export.

Installation does not provide a daemon, background capture, automatic cloud sync or account-level access controls. Profile scoping keeps records organized; the host’s filesystem permissions protect access. Memory is read and updated when the skill runs.

## What this public repository contains

Only reusable workflow knowledge, source-linked written studies, synthetic examples, code, the authorized logo/banner and the selected finished showcase images. No creator-private photographs, personal creative prompts, transcripts, chat exports, account data or prepopulated runtime profiles. Showcase identities are portfolio evidence, not personal-memory seeds.

Private memory is excluded from release packaging and ignored by Git. Keep real user records outside the repo. To forget an item, follow the manual deletion/rebuild procedure in [the canonical guide](../skills/beyondartist/references/personal-and-project-memory.md); the current helper has no delete command.
