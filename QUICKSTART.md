# Setup for complete beginners

This is the straightforward route. None of these commands moves or deletes files in your library.

## 1. Get the files

Install Git, then open a terminal (PowerShell on Windows):

```sh
git clone https://github.com/TABARC-Code/master-librarian-claw.git
cd master-librarian-claw
```

Alternatively use **Code → Download ZIP** on GitHub, then extract the folder.

## 2. Install Python 3 (optional for helper scripts)

Get Python from https://www.python.org/downloads/ if it is not already installed.

Check:

```sh
python3 --version
```

On Windows, try `py -3 --version` if `python3` is not recognised.

## 3. Choose hardware capacity

- **Mini:** Raspberry Pi, 4–8 GB. Smallest model and sequential scanning.
- **Small:** NUC/mini PC, 8–16 GB. One small model at a time.
- **Medium:** desktop or virtual machine, 16–32 GB. Stronger everyday model.
- **Advanced:** workstation/server, 32–64 GB or more. More involved analysis, subject to GPU limits.

Inspect a recommendation with:

```sh
python3 scripts/profile_setup.py --profile medium
```

These profiles are recommendations, not automatic settings.

## 4. Install Ollama for local models (optional)

Get Ollama from https://ollama.com/download and verify:

```sh
ollama --version
ollama pull qwen3:1.7b
```

The 1.7B model is a starting point for smaller hardware; medium installations may try `qwen3:4b`. Model download requires internet, but local model inference does not. Disable remote fallback providers if you need to keep requests local. Don't expose the Ollama service to the public internet.

## 5. Install OpenClaw

Use the official steps for your operating system at https://docs.openclaw.ai/start/getting-started. During onboarding, configure the local model provider.

The root `SKILL.md` is present. For installation, check your installed OpenClaw version's skill commands and supported source types first:

```sh
openclaw skills install . --as master-librarian
openclaw skills check
```

OpenClaw also supports `openclaw skills install git:TABARC-Code/master-librarian-claw@main`.

**Important:** one installed skill can consult eleven specialist playbooks. It does not automatically create eleven running agents. The agent workspaces are templates that need separate routing, permissions and registration.

## 6. Check the scripts

Run the published tests and inspect a safe sample directory:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/setup_doctor.py --profile small
python3 scripts/inventory.py ./your-test-folder
```

The inventory helper is read-only. Hashing large media collections can take time.

## 7. Start on a test folder

Ask the librarian to inspect a small collection without changing it. Review its findings, proposed categories, uncertain editions and duplicate candidates. Never start by giving unrestricted write access to your complete NAS.

## Before trying anything on a real collection

Copy a few non-sensitive test files into a separate directory. Do not give tools unrestricted access to your original documents or NAS. The setup doctor only reports available commands; it does not prove that OpenClaw supports the installation command in this guide. Consult the installed version's help output if the syntax differs.

## What's still being built?

The repository now has a basic SQLite catalogue and manual coordination CLI. Agent auto-registration, live Ollama/OpenClaw dispatch, collection ingestion and safe migration execution remain unfinished. A schema is not a database; a playbook is not a running agent. The README will distinguish finished features from planned ones.

## 8. Try catalogue ingestion

Make a separate test directory and add a few files. From the project root, run:

```sh
mkdir -p state
python3 scripts/catalogue.py --db state/library.sqlite --init
python3 scripts/inventory.py ./your-test-folder > state/inventory.json
python3 scripts/ingest.py --db state/library.sqlite import state/inventory.json
python3 scripts/ingest.py --db state/library.sqlite search "pdf"
```

These steps record file paths and sizes in a local SQLite catalogue. They do not change your documents. The `examples/sample_inventory.json` file shows representative metadata, not actual media or rulebooks. Review classifications using `scripts/classification_review.py` rather than accepting guessed subject labels.
