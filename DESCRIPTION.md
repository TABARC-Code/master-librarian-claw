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

## Version 0.6.0

Introduces persistent SQLite task states, bidirectional referrals, specialist replies, loop and hop controls, review gates and event history. Local CLI commands only: no autonomous dispatcher, remote services or file-changing actions.

## Version 0.7.0

Adds a read-only setup diagnostic command, four-profile inspection and accompanying unit tests. Guided instructions are updated, but automated dependency installation and live service integration are not yet available.

## Version 0.8.0

Connects the read-only inventory report to SQLite, adds path-based catalogue search, and records provisional classifications with source references. Includes sample book, RPG, wargame and media inventory entries. No file reorganisation, full-text search or automatic classification approval.

## Version 0.8.1

A maintenance release covering SQLite schema-v2 reopening, inventory path and size validation, hash preservation across subsequent scans, safer hash file opening and additional regression tests. Adds a Python CI workflow. Live integration is still incomplete; no collection files are modified.

## Version 0.8.2

Fixes the SQLite v1→v2 upgrade regression found by GitHub Actions and corrects a faulty referral-test expectation. Python 3.10, 3.12 and 3.13 unit-test steps passed for the corrected source revision.
