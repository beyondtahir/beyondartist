# Personal and project memory validation — 1.7.0

Reviewed 15 October 2026 in the current local Codex environment. All runtime test data was synthetic and stored in isolated temporary/working folders. No creator photos, actual installer profiles, network research, generated graphics or audience results were used in these tests.

## Executed regression checks

`python3 tests/test_user_memory.py` passed all 18 checks. They exercise independent-process resume, separate people with the same project ID, personal/project retrieval scopes, independent same-named records across projects, Unicode/tag/kind retrieval, copied assets surviving original-file removal and profile transfer, missing/checksum-mismatched assets, correction history, generated-draft and explicit-approval handling, rejected/superseded filtering, honest empty results, damaged/missing cache repair, non-destructive failure on corrupted canonical JSON, path/unknown-project/package-root protection, separate installer roots, six concurrent subprocess writers, retrieval with a blocked socket fixture, and CLI input failure without adding records.

The 29 existing shared-library tests also passed after the final helper and guidance changes. These exercise exact canonical source preservation, lexical relevance, provenance/metric boundaries, stale/new/missing-source failures and cache integrity. A complete shared-index validation found 1,026 records: 95 foundations, 700 Pinterest previews, 54 style panels, seven seeds, 100 thumbnail studies, 67 guide sections and three provenance sections. All 14 canonical visual-study Markdown files remain byte-for-byte identical to the 1.6.2 pre-update snapshot; no original image/Pinterest reinspection is claimed.

Skill Creator frontmatter/scaffold validation passed using the existing local PyYAML dependency. Relative Markdown file targets resolve. SYS-023 is returned first by the executed targeted memory/offline retrieval query. The installed alternate skill-path symlink still resolves to the same updated folder. Fresh app-session skill discovery and execution in Claude/Cowork/Hermes or an ephemeral cloud host were not tested.

## Behavioral review

A separate agent ran case 13 through actual CLI calls with synthetic Mira/Noor profiles and an isolated persistent root. A fresh subprocess resumed Mira's Instagram project, retrieved revision-2 oval-glasses context and the binding brand, found both project IDs in the catalog, and read nine shared full records for a concrete designer-to-artist handoff. Round glasses remained only in canonical revision history. Noor's same-named project and Mira's separate zine preferences were excluded from the active project's retrieval. Both copied text assets survived removal of their synthetic originals; the delivered specification remained a draft, and an agent-only approval update failed. The resumed handoff was saved to project memory and retrieved again. No blocking workflow defect was found.

The review noted that normal context omits revision history (inspect canonical JSON for an audit), scoped overrides still require the agent to interpret the brief, and forget/remove uses documented file cleanup rather than a dedicated CLI command. These are disclosed operating limits. This was an independent memory/brief exercise, not a generated graphic, live research, host-authentication test or audience-performance test. The coordinator read the review and resulting handoff.

## Scope of persistence

The helper uses local canonical JSON, a derived lexical cache and copied assets. The agent initializes and updates this storage while the skill is used. A host must provide durable accessible files; the helper does not install a daemon, auto-capture unrelated conversations or synchronize across accounts/devices. Separate profiles preserve retrieval scope but do not replace host authentication on an untrusted shared server. Approved status requires declared user-approval provenance; the agent remains responsible for checking that declaration against actual human feedback.

The portable package carries shared knowledge, instructions and helpers. Runtime profiles/assets are outside it and are not redistributed. Package verification checks file parity and ZIP integrity; it does not prove behavior on every possible host.
