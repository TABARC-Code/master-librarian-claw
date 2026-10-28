"""Checks that hardware profile recommendations preserve the safety baseline."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("profile_setup", Path(__file__).resolve().parents[1] / "scripts" / "profile_setup.py")
profiles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profiles)

class ProfileTests(unittest.TestCase):
    def test_four_profiles(self):
        self.assertEqual(profiles.CHOICES, ("mini", "small", "medium", "advanced"))

    def test_safe_defaults(self):
        for name in profiles.CHOICES:
            with self.subTest(profile=name):
                p = profiles.load_profile(name)
                self.assertTrue(p["read_only_default"])
                self.assertTrue(p["no_cloud"])
                self.assertEqual(p["network_binding"], "127.0.0.1")
                self.assertEqual(p["ollama_parallel"], 1)
                self.assertEqual(p["loaded_models"], 1)
                self.assertEqual(p["agent_workers"], 1)

    def test_recommended_models(self):
        self.assertEqual([profiles.load_profile(n)["model"] for n in profiles.CHOICES],
            ["qwen3:0.6b", "qwen3:1.7b", "qwen3:4b", "qwen3:8b"])

    def test_output(self):
        self.assertIn("OLLAMA_NO_CLOUD=1", profiles.render("mini"))
        self.assertIn("not applied automatically", profiles.render("medium"))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            profiles.load_profile("../other")
