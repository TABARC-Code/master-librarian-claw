# Repository description

**GitHub short description**

Local-first library management for OpenClaw: specialist agents, bidirectional referrals, Dewey-aware cataloguing, media and tabletop libraries, safe file audits and lightweight Ollama profiles.

## About

A librarian for collections that grew out of control somewhere between the third hard drive and the sixth revision of a rulebook.

Master Librarian is a skill and collection-management toolkit for books, PDFs, audiobooks, films, music, tabletop games, design projects and software archives. Its specialist playbooks can return questions to earlier reviewers, dispute uncertain metadata and follow evidence rather than relying on filenames alone.

The system is designed to run locally, from Raspberry Pi hardware to an accelerated workstation. A single skill can consult the specialist playbooks sequentially. Separate agent workspaces are optional templates and require explicit OpenClaw configuration. It won't silently start twelve services.

Default policy: read-only. Classification may be clever; deleting somebody's campaign archive without permission is not.

## Suggested repository topics

`openclaw`, `ollama`, `digital-library`, `metadata`, `dewey-decimal`, `rpg`, `wargaming`, `cataloguing`, `local-first`, `python`, `archiving`

## Current release

**0.4.0:** Adds a local SQLite catalogue schema and integrity-checked initialiser, following the 0.3.0 hardware profiles and 0.2.0 referral validator. Ingestion, robust schema migrations, live agent transport and automatic agent registration remain unimplemented.

## Version 0.5.0

Adds a read-only local inventory command with optional SHA-256 hashing, scan limits, symlink avoidance and basic tests. It does not import scan results into the catalogue or manage files automatically.
