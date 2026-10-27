# Master Librarian Claw

**Current version: 0.1.0 — foundation and specialist skill instructions.**

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

## Operating model

The librarian keeps classification and audit decisions separate from file-changing operations. Specialist instructions specify bidirectional referrals and bounded loops; the executable router and its tests have not yet been published. Files are inspected read-only unless permission for a specific change has been granted.

Agent templates do not automatically become running agents. SQLite persistence, live routing and a complete installer are planned work, not working features.

## Development

Python helpers and their tests are still to be added. When published, run `python3 -m unittest discover -s tests -v`. The project uses British English. Classification relies on evidence; Dewey schedules may require licensing.

[OpenClaw documentation](https://docs.openclaw.ai/tools/skills) · [Repository description](DESCRIPTION.md) · [Beginner's guide](QUICKSTART.md)

MIT licence applies to the original project code and documentation when the licence file is present.
