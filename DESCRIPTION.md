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

**0.3.0:** Adds four local hardware profiles and a read-only configuration inspector, with profile tests. The 0.2.0 referral validator and eleven specialist skill definitions remain. Runtime integration, persistent SQLite catalogue and independent agent execution remain future work.
