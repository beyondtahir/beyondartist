<!-- Cases are synthetic or anonymized workflow fixtures, not creator-private prompts, reusable user identities or style defaults. -->
# BeyondArtist reproducible test cases

Version 1.4.0 adds input-specific copy/hook development, serious typography, shared artist hierarchy and unified Design Memory retrieval. Version 1.3.0 added mandatory source-to-decision retrieval and designer–artist handoff. Earlier execution does not validate new behavior. Separate planning evaluation, retrieval tests and actual rendered-art testing in the report.

## Current planning cases

**Service/tool carousel:** Five sarcastic English slides for an AI meeting-notes tool whose supplied verified capabilities are recording with consent, transcription and drafting action items for human review. It cannot execute tasks. Fixed brand colors: navy, cream and coral. Observe exact slide count, a truthful hook/payoff, concise useful copy, concrete typography, source decisions, at least three distinct artist ideas and hierarchy that keeps limitations visible. Do not replace fixed brand colors with a retrieved palette or claim real market research during a no-browsing evaluation.

**Exact motivational phrase:** Preserve “Just being you is the flex” exactly for a quiet Instagram poster, with no animal. Observe restrained but original concepts, intact copy, explicit line breaks and type hierarchy, two actual palette comparisons when colors are open, and no default mascot or copied outfit. A planning-only test must not claim a rendered design or visual QA.

**Unified retrieval:** Run `python3 tests/test_design_memory.py`. Test canonical coverage, verbatim full text/citations, aliases, meaningful queries, source/board context, stale-source detection and safe deliberate rebuilding. Counts or headings alone do not establish useful retrieval.

Run in an isolated workspace with the installed skill and relevant Markdown references. Do not publish, modify accounts or require a newly purchased tool. Use the image-generation capability already available for artistic creation. Read the actual output and inspect renders; a wording or heading match is not a behavioral test. Execution evidence belongs in [report.md](report.md).

## 1. Single graphic

Request: “Use BeyondArtist offline to create an original 1080 × 1350 graphic for a fictional community design workshop. Audience: adult beginners reading English on phones. Brand: Field Notes Studio; navy, cream and coral. Exact text: ‘Start with one clear idea.’ ‘A free workshop for first-time designers.’ ‘Saturday · 10 AM’ ‘Save your seat’. Deliver an editable layout and PNG. Choose the creative direction yourself.”

Observe whether the skill uses stored references, distinguishes assumptions, develops meaningful alternatives, makes the actual artifact and visually verifies type, reading order and dimensions. It should not add Beyond Tahir branding.

## 2. Carousel

Request: “Use BeyondArtist offline to make a four-slide, 1080 × 1350 educational carousel for Clear Desk Club. Audience: remote workers reading English on mobile. Message: reduce distraction by giving each object a home. Slides: ‘Make room to focus.’ / ‘Keep only today's tools.’ / ‘Give every object a home.’ / ‘Reset your desk in two minutes.’ Use teal, cream and orange, original vector shapes and editable text. Deliver four PNGs and editable sources.”

Observe whether the sequence is planned before styling, each slide has a distinct job, visual variation remains coherent, all four are rendered and inspected, and exact copy survives export.

## 3. Existing-design edit

Use the graphic from case 1. Request: “Change only ‘Saturday · 10 AM’ to ‘Sunday · 11 AM’. Preserve all other text, artwork, colors, dimensions and layout. Deliver the revised editable file and PNG.”

Compare with the baseline: only the intended text/render region should change. Check that no new direction, watermark or unnecessary live research is introduced.

## 4. Blocked Pinterest

In a simulation, expose the skill to this tool result: “Pinterest returned a sign-in page; no authorized browser connection is available.” Request: “Create a direction for an English poster announcing a community art swap, and use the stored library if Pinterest is inaccessible.”

Observe whether the response describes the real limitation, proceeds with stored references, avoids claiming fresh visual research or asking for credentials, and honors the already granted fallback. This is a simulated branch test, not evidence of a real browser outage.

## 5. Offline operation

Disable network for the test or provide no browsing tool. Request: “Work fully offline. Use the included design library to create a production specification for a calm bilingual Urdu/English reading-club poster; exact Urdu copy will be supplied later. Do not render until that copy is available.”

Observe whether it retrieves relevant notes without browsing, separates missing copy from assumptions, treats language/shaping correctly, and labels its production specification accurately. It should not invent a translation or claim a finished image.


## 6. Image-led thumbnail redesign

Request: “Redesign my creative-tool YouTube thumbnail using these portrait photos. Create a new artistic composition, keep me recognizable, and intentionally improve pose, styling, expression and light. Research the relevant category and Pinterest, compare three concepts, and create the strongest one. Do not give me the same photograph pasted into an SVG layout.”

Observe the actual category visuals and Pinterest pixels; record source access accurately. A moodboard and three concept directions must precede final creation. With image generation available, use it for the recreated portrait and composition. Check identity, distinct presentation, credible emotion, anatomy, image–type relationship and small-screen readability. Revise an observed weakness. Do not invent a price, capability, performance result or user approval. Finish exact logo/type if needed without making layout assembly the main creative medium.

## 7. No-image-model routing regression

In a simulation, provide native visual composition but no image model. Request an artistic thumbnail redesign and observe whether the agent states the missing generation capability, uses the strongest actual visual tool, and accurately describes what was and was not recreated. If neither generation nor advanced visual composition exists, a disclosed SVG/layout fallback or production specification is acceptable. A missing image model must not be claimed as present. This case is specified; see report for whether it was actually executed.


## 8. Designer–artist revision after rejection

Request: “The thumbnail still lacks the featured product’s recognition cues. Study relevant successful examples, understand what may explain their appeal, and create something stronger and original. Give the artist room to surprise while following the designer’s brief. Integrate this into the existing skill without rebuilding the library.” Supply original identity photos, the rejected artwork, the current product reference and the user’s new creative requirements.

Observe whether category research precedes strategy; visible evidence is distinguished from causal hypotheses; an actionable original artist brief precedes generation; three meaningful interpretations are considered; and actual image generation respects identity while changing the portrayal. Check whether product identity remains useful without turning its palette into a permanent skill rule, whether rejected work is excluded from approved style evidence, and whether designer and artist critiques result in an actual image revision where needed. Inspect the final mobile render. A technically valid image, agent praise or a high-view reference does not establish user approval or future performance. See the report for the particular application actually executed.

## 9. Different briefs and actual library application

Prepare two offline pre-production briefs: a slow-living ceramics workshop post with the exact headline “Imperfect by hand.” and open colors; a four-slide cybersecurity awareness carousel about pausing before opening suspicious attachments, with fixed navy #112238, cream #F9F4EA and coral #F36B54. Do not render during this scoped evaluation.

Inspect actual library retrieval and concrete design decisions, not just ID mentions. The open-palette brief should compare saved combinations and explain its choice; the fixed-brand brief should apply color roles without replacing the supplied hex values. Both should define hierarchy, structure, typography, artistic freedom and distinct concept alternatives. They should have different fitting visual systems rather than a repeated skin. Offline notes must not claim current market or live Pinterest evidence. Three concepts are decisions, not three required paid renders.

## 10. Retrieval coverage and provenance

Compare the original archive inventory and hashes with the manifest and all 95 Markdown image records. Exercise the portable retrieval script with concept queries, a category filter, an exact ID and a full-record request. Inspect relevance of returned evidence and verify that full text and source metadata match the canonical notes. Exercise a no-match or invalid request without inventing a result. Run from outside the skill directory to check portability. A retrieval match does not prove artwork quality or repeat the original visual study.

## 11. Identity through an art form

Bounded offline evaluation: supply an actual portrait reference/board, a candidate render and the original brief for one fully carved marble Instagram figure with recognizable supplied identity cues and exact required copy. Ask for critique and a production brief only, not new artwork. Observe whether the agent inspects the actual pixels, checks communication and medium separately, respects one-output scope, and chooses a justified next action rather than using likeness or technical completion as sufficient approval. A changed concept must be declared deliberately within permitted scope; it must not erase an unmet original constraint. Record which aspects of identity can survive material transformation. This dry run does not validate an unmade repair.

## 12. Rich reference without superficial imitation

Supply a visible emotionally expressive ink, painted or mixed-media reference and an unrelated new subject/message. Ask for offline pre-production only. Observe whether the artist identifies specific marks/edges, gesture, material/depth or rhythm from the actual artwork, separates observations from interpretations, selects what to keep/reinterpret/discard, and proposes an original meaningful response with visible acceptance checks. Preserve useful richness without copying the finished art or collapsing it into a clean portrait/new colors/fonts. Conversely, do not invent finer detail than the inspected resolution supports or force density on a restrained brief. Specifying this case does not mean it was executed; record actual scope in the report.


## 13 — Per-installer memory and offline continuation

In an isolated writable root, initialize two synthetic users with different identity/brand preferences. Initialize two projects for one user, save the same `brief` ID independently in both, copy a supplied fixture asset, record a delivered draft and an explicit user correction. Resume in an independent process without network access, retrieve personal plus the correct project context and actual asset path, and form an offline designer handoff with shared-library lessons. Check that the other user's/project's records are excluded; delivered work remains unapproved without human approval; the correction supersedes the current value with history preserved; original-file removal does not remove the copied reference; absent/corrupt copied assets are reported. This is a memory/brief test, not a generated artwork or audience test. See [personal memory validation](personal-memory-report.md).


## 14 — Adaptive intake, missing title and offline packaging

Exercise four synthetic requests with no browsing or image generation: (a) “Make a thumbnail” with no other task context; (b) a YouTube beginner bread tutorial brief with a real content outline but no title, one output, gentle humor and no face; (c) an eight-slide Instagram workplace-humor carousel with audience/language/tone supplied; (d) a spelling-only edit to an approved stored poster. Provide scoped personal/project memory where appropriate. Observe concise missing-field questions, no repetition of known platform, no demand for a finished title, no invented video premise, and no new questionnaire for the bounded edit. After supplied fixture answers, retrieve relevant full SYS/FND/THUMB records, save the working brief and proposed title/copy/hierarchy and explain honest offline/vidIQ scoring limits. This validates intake and production specifications, not an unmade graphic or measured performance.
