"""Persistent coordination smoke tests."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,relative):
    s=importlib.util.spec_from_file_location(name,ROOT/relative)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
catalogue=load('catalogue','scripts/catalogue.py')
coord=load('coordination','scripts/coordination.py')
class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'library.sqlite'
        catalogue.initialise(self.path);coord.migrate(self.path)
    def active(self):
        t=coord.create(self.path,'Edition classification')
        coord.claim(self.path,t,'master-librarian')
        return t
    def test_upgrade_reopen(self):
        self.assertFalse(coord.migrate(self.path))
        with coord.connect(self.path) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_round_trip(self):
        t=self.active()
        coord.refer(self.path,t,'master-librarian','gaming-curator','Which edition?')
        coord.respond(self.path,t,'gaming-curator','Second')
        coord.refer(self.path,t,'gaming-curator','bibliographic-cataloguer','Publication year?')
        coord.respond(self.path,t,'bibliographic-cataloguer','1994')
        coord.refer(self.path,t,'bibliographic-cataloguer','gaming-curator','Is it compatible?')
        coord.respond(self.path,t,'gaming-curator','Yes')
        self.assertEqual(len(coord.show(self.path,t)['referrals']),3)
    def test_unanswered_rejected(self):
        t=self.active();coord.refer(self.path,t,'master-librarian','gaming-curator','Edition?')
        with self.assertRaises(coord.CoordinationError):coord.finish(self.path,t,'master-librarian')
    def test_duplicate_referral(self):
        t=self.active();coord.refer(self.path,t,'master-librarian','gaming-curator','Edition?')
        coord.respond(self.path,t,'gaming-curator','Old')
        coord.refer(self.path,t,'gaming-curator','master-librarian','Why?')
        coord.respond(self.path,t,'master-librarian','Check again')
        with self.assertRaises(coord.CoordinationError):
            coord.refer(self.path,t,'master-librarian','gaming-curator',' edition? ')
    def test_review_gate(self):
        t=self.active()
        with self.assertRaises(coord.CoordinationError):coord.finish(self.path,t,'master-librarian','completed')
        coord.finish(self.path,t,'master-librarian','review')
        coord.finish(self.path,t,'master-librarian','completed')
        self.assertEqual(coord.show(self.path,t)['task']['status'],'completed')
    def test_unknown_agent(self):
        with self.assertRaises(coord.CoordinationError):coord.create(self.path,'Test','made-up-agent')
    def test_missing_database(self):
        with self.assertRaises(coord.CoordinationError):coord.connect(Path(self.temp.name)/'missing.sqlite')
