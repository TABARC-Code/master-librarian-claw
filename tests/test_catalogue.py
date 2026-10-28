"""Smoke tests for SQLite catalogue schema and integrity."""
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("catalogue", Path(__file__).resolve().parents[1] / "scripts" / "catalogue.py")
catalogue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogue)

class CatalogueTests(unittest.TestCase):
    def test_create_and_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state" / "library.sqlite"
            catalogue.initialise(path)
            catalogue.initialise(path)
            self.assertEqual(catalogue.stats(path)["works"], 0)

    def test_work_edition_and_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = catalogue.initialise(Path(directory) / "library.sqlite")
            with catalogue.connect(path) as db:
                db.execute("INSERT INTO works(id,title) VALUES(?,?)", ("w1", "A book"))
                db.execute("INSERT INTO editions(id,work_id) VALUES(?,?)", ("e1","w1"))
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute("INSERT INTO editions(id,work_id) VALUES(?,?)", ("e2","missing"))
            self.assertEqual(catalogue.stats(path)["editions"], 1)

    def test_newer_version_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = catalogue.initialise(Path(directory) / "library.sqlite")
            with catalogue.connect(path) as db:
                db.execute("PRAGMA user_version=99")
            with self.assertRaises(RuntimeError):
                catalogue.initialise(path)
