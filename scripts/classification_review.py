#!/usr/bin/env python3
"""Record and inspect provisional classification proposals without changing files."""
import argparse,json,sqlite3,sys
from pathlib import Path
from uuid import uuid4

STATES=("provisional","inferred","corroborated","verified","conflicted","rejected")
def run(dbpath,action,fileid=None,claim=None,source=None,status="provisional"):
    dbpath=Path(dbpath)
    if not dbpath.is_file():raise ValueError("Catalogue missing")
    db=sqlite3.connect(dbpath)
    try:
        db.execute("PRAGMA foreign_keys=ON")
        if action=="propose":
            if status not in ("provisional","inferred"):raise ValueError("New proposals must be provisional")
            if not fileid or not claim or not source:raise ValueError("Record ID, claim and evidence source required")
            if not db.execute("SELECT 1 FROM file_instances WHERE id=?",(fileid,)).fetchone():raise ValueError("Unknown file record")
            eid=uuid4().hex
            with db:
                db.execute("INSERT INTO evidence(id,entity_type,entity_id,field_name,claim,source_reference,status) VALUES(?,'file',?,'classification',?,?,?)",(eid,fileid,claim,source,status))
                db.execute("INSERT INTO audit_events(action,entity_type,entity_id,details_json) VALUES('classification_proposed','file',?,?)",(fileid,json.dumps({"evidence_id":eid})))
            return {"evidence_id":eid,"status":status}
        if action=="list":
            rows=db.execute("SELECT id,entity_id,claim,source_reference,status FROM evidence WHERE field_name='classification' ORDER BY recorded_at,id").fetchall()
            return [dict(zip(("id","file_id","claim","source","status"),row)) for row in rows]
        raise ValueError("Unknown operation")
    finally:db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--db",required=True)
    s=p.add_subparsers(dest="action",required=True)
    x=s.add_parser("propose");x.add_argument("file_id");x.add_argument("claim");x.add_argument("--source",required=True)
    s.add_parser("list");a=p.parse_args()
    try:print(json.dumps(run(a.db,a.action,getattr(a,"file_id",None),getattr(a,"claim",None),getattr(a,"source",None)),indent=2))
    except (OSError,sqlite3.Error,ValueError) as exc:print(str(exc),file=sys.stderr);return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
