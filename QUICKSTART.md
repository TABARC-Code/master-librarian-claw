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

Once scripts have been added, inspect a recommendation with:

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

Install this repository as a skill only **after the root `SKILL.md` has been published**:

```sh
openclaw skills install . --as master-librarian
openclaw skills check
```

OpenClaw also supports `openclaw skills install git:TABARC-Code/master-librarian-claw@main`.

**Important:** one installed skill can consult eleven specialist playbooks. It does not automatically create eleven running agents. The agent workspaces are templates that need separate routing, permissions and registration.

## 6. Check the scripts

Once the scripts and tests have been published:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/route_case.py examples/handoffs.json
python3 scripts/inventory.py ./examples
```

The inventory helper is read-only. Hashing large media collections can take time.

## 7. Start on a test folder

Ask the librarian to inspect a small collection without changing it. Review its findings, proposed categories, uncertain editions and duplicate candidates. Never start by giving unrestricted write access to your complete NAS.

## What's still being built?

The instruction system and read-only tools precede the production SQLite catalogue, continuous message queue, automatic agent registration and migration engine. A schema is not a database; a playbook is not a running agent. The README will distinguish finished features from planned ones.
