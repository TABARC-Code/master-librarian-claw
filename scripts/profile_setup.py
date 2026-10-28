#!/usr/bin/env python3
"""Display conservative Ollama settings for a local hardware profile. No changes made."""
import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "config" / "profiles"
CHOICES = ("mini", "small", "medium", "advanced")

def load_profile(name):
    if name not in CHOICES:
        raise ValueError("unknown profile")
    p = json.loads((BASE / (name + ".json")).read_text(encoding="utf-8"))
    if (p.get("profile_id") != name or not p.get("offline")
        or not p.get("no_cloud") or not p.get("read_only_default")
        or p.get("network_binding") != "127.0.0.1"):
        raise ValueError("unsafe profile")
    for field in ("ollama_parallel", "loaded_models", "agent_workers", "context_tokens"):
        if type(p.get(field)) is not int or p[field] < 1:
            raise ValueError("invalid resource limit: " + field)
    if p["ollama_parallel"] > 1 or p["loaded_models"] > 1 or p["agent_workers"] > 1:
        raise ValueError("initial profile must use sequential local inference")
    return p

def render(name):
    p = load_profile(name)
    return "\n".join((
        "Profile: " + p["label"],
        "Model: " + p["model"],
        "Fallback: " + p["fallback"],
        "Context target: " + str(p["context_tokens"]) + " tokens",
        "",
        "One-time download (internet required):",
        "  ollama pull " + p["model"],
        "",
        "Example service environment (not applied automatically):",
        "  OLLAMA_NUM_PARALLEL=1",
        "  OLLAMA_MAX_LOADED_MODELS=1",
        "  OLLAMA_CONTEXT_LENGTH=" + str(p["context_tokens"]),
        "  OLLAMA_NO_CLOUD=1",
        "  OLLAMA_HOST=127.0.0.1:11434",
        "",
        "Check actual RAM, GPU passthrough and tool-use reliability before enabling agents."
    ))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=CHOICES, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    p = load_profile(args.profile)
    print(json.dumps(p, indent=2) if args.json else render(args.profile))

if __name__ == "__main__":
    main()
