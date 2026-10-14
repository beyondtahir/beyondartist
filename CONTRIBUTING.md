# Contribute a lesson that changes the work

Useful contributions improve a real decision: intake, evidence, creative angle, typography, hierarchy, color roles, artist craft, medium fidelity, retrieval or final review. Explain the observed problem, the proposed change and how it was checked. Keep references source-linked and distinguish observation from interpretation.

Do not submit private portraits, client briefs, transcripts, analytics, account identifiers, chats or runtime memory. Use synthetic fixtures for behavioral checks. Public showcase changes require explicit asset authorization; images are not automatically reusable because they are online.

Update canonical references rather than creating contradictory copies. Rebuild the shared index only after reviewing the change:

~~~sh
python3 skills/beyondartist/scripts/retrieve_library.py --rebuild-index
python3 scripts/validate_repo.py
~~~

Run the relevant tests. Host installation documentation should cite opened primary sources and record its review date. Documentation review, local smoke testing and actual production use are different levels of verification.
