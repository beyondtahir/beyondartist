# Adaptive intake and brief development

Read before every new design/redesign, after resolving the active user and relevant memory under SYS-023. The creator requests a simple starting questionnaire because users may only have a rough idea. The agent supplies the design thinking; a user should not need to write a production prompt, choose fonts or know art terminology. This check belongs inside step 1 of the existing nine-step workflow, not a second mandatory approval chain.

## Ask only what changes the result

First extract supplied answers and scoped personal/project defaults. Classify platform, format, content category and tone separately. Mark each important value as user-supplied, remembered within scope, inferred or proposed. Current directions override old defaults. A familiar subject does not mean the current job shares the last mood, palette or message.

Run a brief completeness check before each task. If the essentials are already clear, summarize the direction in one sentence and proceed. If something consequential is missing, ask one compact batch of one to three plain questions covering the missing decisions. Do not ask all questions below by rote, repeat known answers, demand an elaborate prompt, or ask the user to do the designer's work. Bundle related fields naturally. Gather a useful first answer before asking a second round; follow up only when an answer exposes a genuinely consequential ambiguity.

Essential before committing structure/render: platform/format, the actual content/message and intended viewer payoff or purpose. Exact copy, mandatory brand constraints and required identity assets must also be resolved where they are binding. Audience, language, mood, quantity and assets often change the result; ask if unknown and consequential, otherwise use a fitting stated proposal. An unavailable title is not an unavailable topic. A vague “viral” alone leaves the content/message unresolved.

If the user explicitly says to choose or not ask, resolve routine choices and state the assumed brief. Do not invent unseen content or a faithful identity from an unavailable face reference. Ask for an essential missing asset when necessary. For optional clarification, give a reasonable opportunity to answer while doing independent retrieval/research; use a stated assumption if no answer arrives. Missing essential answers remain missing; elapsed time is not consent or confirmation. A bounded correction inherits the approved brief and asks only about its actual ambiguity; no fresh questionnaire for a spelling fix.

Use the host's concise input tool where available, or a short conversational question when it is not. If a text-only widget cannot accept files, request an essential attachment through ordinary chat rather than the widget. Make suggested choices mutually clear and include a way to answer in the user's words. Do not force an enum to capture nuanced humor or purpose. Avoid implementation/credit/account questions unless a specific authorized tool action actually requires them.

## Thumbnail questions

Select from these according to the gaps, rather than sending them all:

- “Where will this thumbnail appear: YouTube long-form, Shorts, or somewhere else?” A supplied YouTube/long-form context answers this already; don't ask it again.
- “What happens in the video, and what should viewers learn or feel? A sentence or a few bullets is enough.” Ask for category/niche only when the content does not establish it.
- “Do you already have a title or script? Share it if you do; I can develop the title and thumbnail hook if you don't.” This is optional once content is established, not a blocker demanding a finished title.
- “Who is this for, and should it feel funny, shocking, serious or something else?” Ask only unknown parts and preserve a supplied tone.
- “Should it feature you, a product, a character or another subject? Is there wording or branding that must stay?” Use available inspected assets and scoped brand memory; don't request the same photos again when a saved usable reference exists.

Example sparse request, “Make a thumbnail”: ask platform plus video topic/payoff, and optionally title/subject in the same small batch. Continue independent shared-memory retrieval, but don't render a made-up video premise. Example complete request, “One YouTube thumbnail for my beginner sourdough tutorial; gentle humor, no face, headline optional”: the task has sufficient essentials. Choose a grounded title/hook through relevant memory and category research, then proceed; “what platform?” would be needless.

When title is absent, read SYS-025 and [thumbnail packaging](thumbnail-packaging.md). From known content, audience and factual limits, develop a few meaningfully different title–image–overlay pairs internally, select one and label the title a proposal. Preserve exact supplied title/copy when fixed. A thumbnail-only request can use a working title for alignment without turning into an unwanted script or a long title report. No title-generation tool is compulsory if ordinary grounded writing suffices.

## Carousel questions

Determine platform, audience/language, topic and desired payoff, then count and tone where needed:

- “Where will this carousel be posted, and what's the topic or message?” Don't repeat Instagram if supplied.
- “Should viewers learn something, recognize a funny situation, feel motivated, or take an action? Who is it for?” If this is already a clearly stated educational or meme brief, ask only a consequential remaining gap.
- “What language and roughly how many slides? What humor or mood do you want?” Offer fitting examples such as relatable everyday humor, sarcasm, cultural memes or serious editorial storytelling without making humor mandatory.
- If named characters/quotes matter: establish exact quotation versus adapted joke, verify attribution where required and label adaptations. Don't silently turn original work humor into a purported famous dialogue.

Build the actual cover-to-payoff sequence through SYS-005, then exact copy/type roles and the artist handoff. A user list needs item counting and an agreed meaning of slide count: clarify “8 slides” versus “cover plus 8” when ambiguous. Do not create disconnected posters or add a CTA that displaces requested content. The category is what the carousel communicates, not the word “carousel.”

## Single posts and other visuals

Ask the missing platform/format, message/purpose and intended viewer/context first. Use the appropriate content route: a phrase needs its human meaning; motivation needs the actual friction; a service needs its useful outcome and verified limits; a meme needs its relatable setup/reaction; a portrait needs intended emotion and identity/reference needs. Resolve binding language/copy/brand rules and quantity. Let the designer/artist select concept, palettes and art form from relevant knowledge and research instead of requesting a font/palette shopping list from an inexperienced user.

For a fully specified visual structure, carry it into A faithfully and use permitted creative room for B under SYS-018. An explicit one-output request overrides B. For an existing approved edit, inherit its project memory and preserve unrequested elements.

## Turn answers into a working brief and save them

Write a concise brief before planning: platform/format; category; audience; useful/emotional payoff; language; quantity; title/current copy; tone; required assets/identity; binding brand/exact copy; and flexible creative choices. Separate confirmed requirements from assumptions and artist proposals. Fix unknowns that change the communication destination before generation; resolve optional style details through designer judgment.

Use `user_memory.py put --person <active-person> --project <project> --input <record.json>` to save the evolving `brief` record. Keep questions/answers, scope and source references in `data`, not hidden reasoning transcripts or an indiscriminate conversation dump. A compact example of the `data` part is:

```json
{
  "platform": "YouTube",
  "format": "long-form-thumbnail",
  "category": "beginner cooking tutorial",
  "audience": "first-time home bakers",
  "payoff": "understand the first loaf process",
  "language": "English",
  "quantity": 1,
  "tone": "gentle humor",
  "title": null,
  "title_status": "not-supplied",
  "fixed": ["no face"],
  "intake": {
    "questions": [],
    "answered_from": ["current user brief"],
    "missing_required": [],
    "assumptions": ["designer may propose headline and working title"]
  }
}
```

This synthetic example is a project brief, not a user default or template everyone must reproduce. Use the full canonical record schema with title/kind/tags/provenance. Save title/hook alternatives and the selected pair as a scoped `decision`, still unapproved unless the user actually approves it. Save researched category/Pinterest/vidIQ lessons and actual review feedback as separate project records with dates and source identifiers. Promote an enduring user preference only when its scope supports personal reuse; never promote private creative briefs/photos into the shared library. Record actual executed tools versus stored/public guidance. Then continue steps 2–9 and update memory at delivery/feedback.
