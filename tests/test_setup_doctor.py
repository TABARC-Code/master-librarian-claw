"""Basic safety and profile checks for the local setup doctor."""
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('setup_doctor',ROOT/'scripts'/'setup_doctor.py')
MOD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
class DoctorTests(unittest.TestCase):
    def test_profiles(self):
        for name in MOD.PROFILES:
            with self.subTest(profile=name):
                self.assertEqual(MOD.check(name)['profile'],name)
    def test_no_changes(self):
        result=MOD.check()
        self.assertIs(result['setup_actions_taken'],False)
        self.assertIn('sqlite',result)
    def test_invalid_profile(self):
        with self.assertRaises(ValueError): MOD.check('../bad')
