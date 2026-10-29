"""Stress and failure-mode regression tests using isolated temporary catalogues."""
import concurrent.futures
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name, path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
catalogue=load('catalogue_stress','scripts/catalogue.py')
coord=load('coord_stress','scripts/coordination.py')
ingest=load('ingest_stress','scripts/ingest.py')

class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base=Path(temp.name)
        self.db=catalogue.initialise(self.base/'state.sqlite')
        coord.migrate(self.db)

    def test_parallel_task_creation(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            tasks=list(pool.map(lambda n:coord.create(self.db,f'Task {n}'),range(80)))
        self.assertEqual(len(set(tasks)),80)
        with coord.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM agent_tasks').fetchone()[0],80)
            self.assertEqual(db.execute('SELECT count(*) FROM agent_events').fetchone()[0],80)

    def test_parallel_claim_same_task_only_once(self):
        task=coord.create(self.db,'One claim')
        def attempt(_):
            try:
                coord.claim(self.db,task,'master-librarian')
                return True
            except (coord.CoordinationError,sqlite3.OperationalError):
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(attempt,range(12)))
        self.assertEqual(sum(results),1)

    def test_failed_import_rolls_back(self):
        file=self.base/'batch.json'
        file.write_text(json.dumps({'root':str(self.base),'truncated':False,'files':[
            {'path':'books/valid.pdf','size':5},
            {'path':'../escape.pdf','size':2}]}),encoding='utf-8')
        with self.assertRaises(ValueError):
            ingest.ingest(self.db,file)
        self.assertEqual(catalogue.stats(self.db)['file_instances'],0)

    def test_failed_migration_keeps_v1(self):
        original=self.base/'other.sqlite'
        catalogue.initialise(original)
        with sqlite3.connect(original) as db:
            db.execute('CREATE TABLE agent_tasks (wrong TEXT)')
        with self.assertRaises(sqlite3.OperationalError):
            coord.migrate(original)
        with sqlite3.connect(original) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT count(*) FROM schema_version WHERE version=2').fetchone()[0],0)

    def test_referral_state_after_reopening(self):
        task=coord.create(self.db,'Long-running review')
        coord.claim(self.db,task,'master-librarian')
        coord.refer(self.db,task,'master-librarian','gaming-curator','Verify the edition')
        self.assertEqual(coord.show(self.db,task)['referrals'][0]['response_status'],'pending')
        coord.respond(self.db,task,'gaming-curator','Verified by the title page')
        self.assertEqual(coord.show(self.db,task)['referrals'][0]['response_status'],'answered')

    def test_reject_unsupported_database_version(self):
        with sqlite3.connect(self.db) as db:
            db.execute('PRAGMA user_version=99')
        with self.assertRaises(ValueError):
            ingest.search(self.db,'game')
