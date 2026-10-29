"""Ingestion and provisional-classification tests."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
cat=load("catalogue","scripts/catalogue.py")
ing=load("ingest","scripts/ingest.py")
rev=load("classification_review","scripts/classification_review.py")
class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.db=self.base/"library.db";cat.initialise(self.db)
        self.inv=self.base/"inventory.json"
    def write(self,files):
        self.inv.write_text(json.dumps({"root":str(self.base),"files":files,"truncated":False}))
    def test_import_and_search(self):
        self.write([{"path":"Gaming/Core Rules.pdf","size":200}])
        self.assertEqual(ing.ingest(self.db,self.inv),1)
        self.assertEqual(len(ing.search(self.db,"Core Rules")),1)
        self.assertEqual(ing.ingest(self.db,self.inv),1)
        self.assertEqual(len(ing.search(self.db,"Core Rules")),1)
    def test_provisional_review(self):
        self.write([{"path":"Books/History.pdf","size":44}]);ing.ingest(self.db,self.inv)
        identifier=ing.search(self.db,"History")[0]["id"]
        rev.run(self.db,"propose",identifier,"Medieval history","Title page")
        self.assertEqual(rev.run(self.db,"list")[0]["status"],"provisional")
    def test_reject_parent_path(self):
        self.write([{"path":"../private.txt","size":5}])
        with self.assertRaises(ValueError):ing.ingest(self.db,self.inv)
    def test_reject_truncated(self):
        self.inv.write_text(json.dumps({"root":str(self.base),"files":[],"truncated":True}))
        with self.assertRaises(ValueError):ing.ingest(self.db,self.inv)
    def test_search_literal_wildcards(self):
        self.write([{"path":"Rules/100% Complete.pdf","size":1},{"path":"Rules/100x Complete.pdf","size":2}])
        ing.ingest(self.db,self.inv)
        self.assertEqual(len(ing.search(self.db,"100%")),1)
