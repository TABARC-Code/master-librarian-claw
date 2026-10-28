"""Inventory smoke tests."""
import hashlib, importlib.util, tempfile, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("inventory", Path(__file__).resolve().parents[1] / "scripts" / "inventory.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)

class InventoryTests(unittest.TestCase):
    def test_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/"book.pdf").write_bytes(b"book")
            data=inventory.inspect_tree(p, hash_files=True)
            self.assertEqual(data["files"][0]["sha256"], hashlib.sha256(b"book").hexdigest())
    def test_limit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/"a").touch(); (p/"b").touch()
            self.assertTrue(inventory.inspect_tree(p, max_files=1)["truncated"])
    def test_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/"a").touch()
            try: (p/"link").symlink_to(p/"a")
            except (OSError,NotImplementedError): self.skipTest("No symlinks")
            data=inventory.inspect_tree(p)
            self.assertEqual(len(data["files"]),1)
            self.assertTrue(any(x["error"]=="symlink_skipped" for x in data["issues"]))
    def test_bad_root(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): inventory.inspect_tree(Path(d)/"missing")
    def test_depth(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/"nested").mkdir(); (p/"nested"/"a").touch()
            self.assertEqual(inventory.inspect_tree(p,max_depth=0)["files"],[])
