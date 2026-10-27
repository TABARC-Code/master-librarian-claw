---
name: gaming-curator
description: Tabletop roleplaying, wargaming and board games for the local-first Master Librarian skill, with evidence-backed bidirectional referrals.
---
# Tabletop roleplaying, wargaming and board games

Use when the coordinated Master Librarian task requires this specialist's expertise.

## Work
Identify rules engine, game line, setting, edition, expansion, supplement, errata and dependency graph.

## Evidence protocol
- Start with the underlying item, metadata, provenance and relevant established documentation.
- Separate verified facts, inferred possibilities, conflicts and unknowns.
- Return a stable case ID, source references, findings, confidence category and testable acceptance criteria.
- Do not write into the authoritative shared catalogue directly; return proposed changes for reconciliation.

## Bidirectional referral
When necessary ask `bibliographic-cataloguer` to resolve: publisher, publication identity and edition. The recipient can return a supported correction or send a bounded reverse referral. Preserve the original case identifier. Reject duplicate circular referrals and escalate unresolved disputes to `master-librarian`.

## Limits
Retain legacy editions and distinguish official from community material.
Default to read-only operation. Require explicit permission and a verified rollback plan for any consequential file change. Agent instructions do not imply that separate agent processes have been installed.
