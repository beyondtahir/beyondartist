# Distribution validation

The first public release is **v1.0.0**. **v1.0.1** adds explicit native-first image-model discovery, connected-tool checks and editing/SVG fallback instructions. The shared workflow and library were developed through prior local iterations; their source evidence stays intact. Internal development reports are historical records, not extra public release versions.

## What the checks cover

- Complete skill/resources and release manifest consistency.
- All 1,038 shared retrieval records and source/index integrity.
- Personal/project memory persistence, profile/project scope, asset copying and actual approval declarations.
- Exactly sixteen user-selected showcase works and one identity banner, with original PNG checksums and dimensions.
- Local documentation/image links and the distribution boundary for private paths, attachment identifiers, runtime profiles and unexpected files.
- Skill-only and full-repository archives with byte-for-byte source parity.

Run from the repository root:

~~~sh
python3 scripts/validate_repo.py
python3 scripts/package.py
~~~

The tests use synthetic data and temporary directories, never the creator’s private profile or photographs. The installer can be smoke-tested with an explicit temporary destination; it refuses overwrites.

## What is a separate check

Behavioral design review inspects the actual artifact and context. Successful index/code tests do not establish artistic quality or audience results. Setup documentation is checked against primary sources, while production on another host still needs its own tools and runtime check.

The visual presentation uses the supplied logo/banner and artwork unchanged. GitHub’s native Markdown/HTML rendering carries the page; preview images preserve aspect ratios without cropping.

**[Shared-memory tests](../skills/beyondartist/tests/test_design_memory.py)** · **[Personal-memory tests](../skills/beyondartist/tests/test_user_memory.py)** · **[Source ledger](sources.md)**
