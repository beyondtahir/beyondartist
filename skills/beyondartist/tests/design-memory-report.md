# Design Memory retrieval validation

Validated 2026-10-13 on the current local host.

- `--validate-index`: passed; cached records match reparsed canonical Markdown and all source hashes.
- `python3 tests/test_design_memory.py`: **20 tests passed**. Exact source-line fidelity is checked for every record.
- Corpus: **906 records** — 95 foundation studies, 700 Pinterest previews (694 distinct source URLs), 54 style panels, 7 seed studies, 47 operating-guide sections (including SYS-001–016), 3 provenance sections.
- Legacy `ZIP-*` lookups resolve to `FND-*` with no duplicated study records.
- Source/board context is searchable at low weight and distinguished from section evidence in query output.
- Stale, missing and newly discovered sources, cache corruption, dynamic SYS sections and new guide files are covered by tests.
- Index bytes: 8399639.

## Local timing sample

Five complete CLI searches, including interpreter startup, index loading, source-file hash checks and ranking, for `typography major decision` in `guides`: **129.0, 100.5, 89.1, 94.6, 98.0 ms**. Median **98.0 ms**. Top result: `SYS-009`.

These are local timing samples, not a cross-host speed guarantee. Query speed does not imply visual quality or audience performance. The tool retrieves saved text; no cloud embeddings, model training, live research or original-image revalidation is claimed.
