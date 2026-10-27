"""Unit tests for the bounded, read-only referral validator."""
import unittest
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("route_case", Path(__file__).resolve().parents[1] / "scripts" / "route_case.py")
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)

class ReferralTests(unittest.TestCase):
    def case(self, hops):
        return {"case_id": "collection-0001", "hops": hops}

    def test_empty_case(self):
        self.assertEqual(route.validate_route(self.case([]))["hop_count"], 0)

    def test_reverse_referral(self):
        hops = [
            {"from": "gaming-curator", "to": "bibliographic-cataloguer", "question": "Which edition?"},
            {"from": "bibliographic-cataloguer", "to": "gaming-curator", "question": "Is this compatible?"},
        ]
        self.assertEqual(route.validate_route(self.case(hops))["current_agent"], "gaming-curator")

    def test_duplicate_loop(self):
        edge = {"from": "gaming-curator", "to": "knowledge-architect", "question": "Check the link"}
        back = {"from": "knowledge-architect", "to": "gaming-curator", "question": "More evidence?"}
        with self.assertRaisesRegex(route.ReferralError, "repeated"):
            route.validate_route(self.case([edge, back, edge]))

    def test_self_referral(self):
        with self.assertRaises(route.ReferralError):
            route.validate_route(self.case([{"from": "office-manager", "to": "office-manager", "question": "Why?"}]))

    def test_broken_chain(self):
        with self.assertRaisesRegex(route.ReferralError, "disconnected"):
            route.validate_route(self.case([
                {"from": "gaming-curator", "to": "dewey-classifier", "question": "Subject?"},
                {"from": "office-manager", "to": "collections-auditor", "question": "Review?"},
            ]))

    def test_hop_limit(self):
        with self.assertRaisesRegex(route.ReferralError, "hop limit"):
            route.validate_route(self.case([
                {"from": "gaming-curator", "to": "dewey-classifier", "question": "Subject?"}
            ]), max_hops=0)

    def test_reject_invalid_identity(self):
        with self.assertRaises(route.ReferralError):
            route.validate_route(self.case([{"from": "unknown", "to": "gaming-curator", "question": "Hello"}]))

if __name__ == "__main__":
    unittest.main()
