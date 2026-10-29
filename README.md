# Master Librarian Claw

**Current version: 0.8.2 — verified migration and test fixes.**

**One librarian, eleven specialist departments, and a fairly healthy suspicion of `final-final-v3.pdf`.**

Master Librarian is a local-first OpenClaw skill for cataloguing books, PDFs, tabletop games, RPGs, films, television, music, audiobooks, design assets and software archives. The principal skill coordinates eleven specialist playbooks with evidence-led, bidirectional referrals.

## Installation for beginners

See [QUICKSTART.md](QUICKSTART.md). Read the [project description](DESCRIPTION.md) for its current limits.

```sh
git clone https://github.com/TABARC-Code/master-librarian-claw.git
cd master-librarian-claw
openclaw skills install . --as master-librarian
```

The root `SKILL.md` and eleven specialist `SKILL.md` files are present. Installation and live agent dispatch still require testing against the installed OpenClaw version. Do not assume installation means twelve running agent processes.

## Hardware profiles

| Tier | Typical machine | RAM | Candidate Ollama model |
|---|---|---|---|
| Mini | Raspberry Pi | 4–8 GB | `qwen3:0.6b` |
| Small | NUC or mini PC | 8–16 GB | `qwen3:1.7b` |
| Medium | Desktop or accelerated VM | 16–32 GB | `qwen3:4b` |
| Advanced | Workstation or server | 32–64 GB+ | `qwen3:8b` |

These are starting points, not guaranteed runtime requirements. Models and context sizes need testing against actual free RAM and usable GPU memory.

## Inspect a local hardware profile

Run `python3 scripts/profile_setup.py --profile mini` (or `small`, `medium`, `advanced`). Add `--json` for structured output. The inspector prints recommendations without modifying Ollama or OpenClaw. The four profiles keep inference sequential and the service bound to loopback by default. Profile recommendations have not been benchmarked on the target machines.

## Local catalogue (early implementation)

Create an empty metadata database with `python3 scripts/catalogue.py --db ./state/library.sqlite --init`. The command creates an SQLite catalogue, enables foreign keys and WAL, and checks database integrity. It does not scan, rename or delete your library files. The initial schema has works, editions, file instances, authority records, relationships, evidence and audit events; ingestion and migrations beyond schema v1 are still to come.

## Operating model

The librarian keeps classification and audit decisions separate from file-changing operations. A read-only Python validator checks bidirectional referral chains, repeated loops and invalid agents. This is not yet a live agent dispatcher. Files are inspected read-only unless permission for a specific change has been granted.

Agent templates do not automatically become running agents. SQLite persistence, live routing and a complete installer are planned work, not working features.

## Development

Run `python3 -m unittest discover -s tests -v` for referral, profile and catalogue checks. Newly published tests still require execution against a clean checkout. The project uses British English. Classification relies on evidence; Dewey schedules may require licensing.

[Development roadmap](ROADMAP.md) · [OpenClaw documentation](https://docs.openclaw.ai/tools/skills) · [Repository description](DESCRIPTION.md) · [Beginner's guide](QUICKSTART.md)

MIT licence applies to the original project code and documentation when the licence file is present.

## Collection inventory (v0.5.0)

Run `python3 scripts/inventory.py ./sample-folder` for a JSON listing, or add `--hash` for SHA-256 digests. Use `--max-files` and `--max-depth` to limit the scan. Symbolic links and special files are skipped. This does not move, rename, delete or update library files. Output currently goes to standard output; it does not yet ingest records into SQLite. Avoid hashing enormous NAS collections until the next stage adds streaming output and resumable checkpoints.

Five inventory tests were run locally against the scanner implementation. The complete repository test suite still needs an independent checkout run.

## Persistent specialist referrals (v0.6.0)

Once you have initialised your local catalogue, upgrade the schema:

```sh
python3 scripts/catalogue.py --db ./state/library.sqlite --init
python3 scripts/coordination.py --db ./state/library.sqlite migrate
python3 scripts/coordination.py --db ./state/library.sqlite create "Identify a game supplement"
```

The final command prints a task ID. Use that ID in subsequent `claim`, `refer`, `respond`, `finish` and `show` commands. For example, `claim TASK_ID master-librarian`, then `refer TASK_ID master-librarian gaming-curator "Which edition?"`. A specialist must answer a pending question before forwarding another. Completion requires a Master Librarian review state. Events and responses persist in SQLite.

The coordinator is a local, explicit command-line task engine, **not** an autonomous OpenClaw dispatcher or a running background service. It neither invokes Ollama nor modifies library files. Schema upgrade changes the catalogue database: back it up first if you have valuable records.

Run `python3 -m unittest discover -s tests -v` to check the repository. The coordinator logic passed a separate seven-test local prototype; tests against this exact published revision and the full prior schema still require a complete checkout run.

## Local setup diagnostics (v0.7.0)

Run `python3 scripts/setup_doctor.py --profile small` and select `mini`, `small`, `medium` or `advanced` as needed. The command checks operating-system details, Python, SQLite, and whether Git, Ollama and OpenClaw are on your command path. It does **not** install dependencies, test model inference, modify settings or start any services. See `QUICKSTART.md` for first-run guidance. The setup doctor passed three local unit tests; there has not yet been an end-to-end installation test with OpenClaw.

## Catalogue workflows (v0.8.0)

Create a database, scan a test directory and import its inventory:

```sh
python3 scripts/catalogue.py --db ./state/library.sqlite --init
python3 scripts/inventory.py ./your-test-folder > ./state/inventory.json
python3 scripts/ingest.py --db ./state/library.sqlite import ./state/inventory.json
python3 scripts/ingest.py --db ./state/library.sqlite search "rules"
python3 scripts/classification_review.py --db ./state/library.sqlite list
```

Use the file ID returned by search to propose a classification:

```sh
python3 scripts/classification_review.py --db ./state/library.sqlite propose FILE_ID "Possible tabletop game rules" --source "Local title-page inspection"
```

The example inventory under `examples/` is illustrative metadata and not a real collection. All classifications remain provisional; the system does not yet approve or reconcile them automatically. Imports change the **local SQLite database**, never source documents. Only complete inventory reports are accepted. Reimports update file observations but do not delete missing records. Search currently matches file paths, not document contents. The full suite still needs a verified clean-checkout run.

## Audit fixes (v0.8.1)

Fixed reopening schema-v2 catalogues through the v1/v2-aware catalogue inspector. Import rejects negative sizes and additional unsafe inventory paths. Repeat imports without hashes now preserve recorded SHA-256 values. Hashing opens files with no-follow protection where supported and compares file identity and metadata around reading. These improvements reduce, but do not eliminate, time-of-check/time-of-use risks on mutable directory trees. The scanner still needs directory-descriptor-based traversal for stronger hostile-tree protection.

A Python compilation and unit-test workflow has been added for pull requests and pushes. Its first run has not been observed; a green CI result is **not** claimed. OpenClaw/Ollama runtime integration and end-to-end NAS testing remain unverified.

## Patch release 0.8.2

Corrected the initial schema-history record to version 1 so the SQLite v1→v2 upgrade does not collide with an incorrectly inserted version 2. Corrected the hop-limit test's expected error message. GitHub Actions unit tests now pass on Python 3.10, 3.12 and 3.13 for the corrected source revision. These checks cover the automated suite, not live Ollama/OpenClaw installation, NAS stress tests or an adversarial filesystem security audit.
