#!/usr/bin/env python3
"""Bounded, local-only referrals between Master Librarian specialists."""
import argparse
import json
import sys

SPECIALISTS = frozenset((
    "master-librarian", "dewey-classifier", "bibliographic-cataloguer",
    "media-archivist", "gaming-curator", "digital-asset-manager",
    "software-archivist", "file-forensics", "knowledge-architect",
    "office-manager", "collections-auditor", "methods-researcher",
))

class ReferralError(ValueError):
    pass

def validate_route(case, max_hops=8):
    """Validate a history of referrals; never execute, send or modify anything."""
    if not isinstance(case, dict) or not isinstance(case.get("case_id"), str) or not case["case_id"].strip():
        raise ReferralError("case_id must be a non-empty string")
    if not isinstance(max_hops, int) or isinstance(max_hops, bool) or max_hops < 1:
        raise ReferralError("max_hops must be a positive integer")
    hops = case.get("hops", [])
    if not isinstance(hops, list):
        raise ReferralError("hops must be a list")
    if len(hops) > max_hops:
        raise ReferralError("hop limit exceeded")
    seen = set()
    previous = None
    for index, hop in enumerate(hops):
        if not isinstance(hop, dict):
            raise ReferralError("hop must be an object")
        source, target, question = (hop.get(key) for key in ("from", "to", "question"))
        if source not in SPECIALISTS or target not in SPECIALISTS:
            raise ReferralError("unknown specialist")
        if source == target:
            raise ReferralError("self-referral is not permitted")
        if previous is not None and source != previous:
            raise ReferralError("disconnected hand-off")
        if not isinstance(question, str) or not question.strip():
            raise ReferralError("referral needs a question")
        # The same edge and normalised question cannot circulate twice in a case.
        signature = (source, target, " ".join(question.casefold().split()))
        if signature in seen:
            raise ReferralError("repeated referral loop")
        seen.add(signature)
        previous = target
    return {"case_id": case["case_id"], "status": "valid", "hop_count": len(hops), "current_agent": previous}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", help="Path to a JSON case containing case_id and hops")
    parser.add_argument("--max-hops", type=int, default=8)
    args = parser.parse_args(argv)
    try:
        with open(args.case, encoding="utf-8") as handle:
            result = validate_route(json.load(handle), max_hops=args.max_hops)
    except (OSError, json.JSONDecodeError, ReferralError) as exc:
        print(json.dumps({"status": "rejected", "reason": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
