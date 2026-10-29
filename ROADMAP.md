# Development roadmap

The system is built bottom-up so a small computer can run one model and a more capable server can use the same data and instructions.

## 0.2.0 — Referral rules (current)
- Read-only validator: `scripts/route_case.py`
- Checks specialist IDs, connected routes, reverse hand-offs, repeated edges and hop limits
- Unit tests for accepted and rejected cases
- **Not** a transport, agent process launcher or OpenClaw API integration

### Acceptance gate
Run `python3 -m unittest discover -s tests -v` in a checkout. No live test has yet been recorded from the repository environment.

## 0.3.0 — Hardware profiles
- Validate and publish Mini, Small, Medium and Advanced JSON profiles
- Ollama model choice, RAM/VRAM guardrails and sequential inference limits
- Hardware discovery in advisory mode; never silently change configuration
- Tests for every profile and unknown profile names

## 0.4.0 — Persistent SQLite catalogue (initial schema committed)
- Initial schema for works, editions, file instances, authorities, evidence, relationships and audit events; subsequent migrations remain to be developed
- Foreign key enforcement, SQLite WAL and integrity verification in the local initialiser
- Store provenance, uncertainty and change history
- Backups, restoration test and schema checks
- No destructive file operations

## 0.5.0 — Local collection inventory
- Read-only walk with safety against symlink loops and changing file trees
- Optional hashes and file signatures
- Resume and cancellation; no unrestricted network-share scanning
- Test with mixed books, games, media and creative asset fixtures

## 0.6.0 — Coordinated queue (initial implementation)
- Persistent referral records and responses; live worker claiming and retries remain to be implemented
- Transactional manual claiming, status transitions, cancellation and repeated-referral detection; automatic retry is not implemented
- Single writer for catalogue publication, independent audit review
- CPU-only sequential dispatcher first; local Ollama optional

## 0.7.0 — Guided setup (diagnostics implemented)
- Read-only detection of operating system, Python, SQLite and presence of Ollama/OpenClaw executables; complete installation checking remains open
- Explain missing prerequisites clearly
- Local-only privacy settings and explicit folder allowlist
- Begin with a demo library and dry-run mode
- Avoid promising a universal one-command OpenClaw install without verified platform support

## 0.8.0 — Practical catalogue use (first workflows committed)
- Ingest scanner inventories and propose provisional classification evidence; edition matching and conflict reconciliation remain pending
- JSON output and simple path search; full-text search and CSV export remain pending
- Curated gaming/media/bibliographic samples to assess accuracy

## 0.9.0 — Migration planning
- Produce proposed renames and moves without executing them
- Detect path collisions, case-folding problems, dependencies and space constraints
- Manifests, approval boundaries and simulated rollback
- No file-changing engine until audited and separately authorised

## 1.0.0 — Tested local release
- Benchmarks on representative 8 GB CPU and 32 GB / 8 GB GPU environments
- Beginner installation and restoration tested in a clean environment
- Published integration limitations and reproducible test results

## Release discipline

Every substantive development stage should update `VERSION`, `README.md`, `DESCRIPTION.md` and relevant tests together. Separate commits must reflect real work. No fabricated activity, timestamps or release claims.

## 0.8.1 — Security and reliability audit

- Corrected catalogue version checks after schema-v2 migration
- Tightened import validation and preserved existing hashes when observations lack a digest
- Added no-follow safeguards for opening files during hashing (where supported)
- Added regression tests and Python CI configuration
- Outstanding: test the full suite in CI, improve hostile-directory traversal, strengthen concurrent task authorisation, add backup/migration failure simulations and validate installation commands
