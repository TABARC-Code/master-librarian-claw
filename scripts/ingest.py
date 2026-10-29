#!/usr/bin/env python3
"""Import a read-only inventory into SQLite and search catalogue records."""
import argparse, hashlib, json, sqlite3, sys
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

def connect(path):
    if not Path(path).is_file(): raise ValueError("Initialise the catalogue first")
    db=sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    if db.execute("PRAGMA user_version").fetchone()[0] not in (1,2):
        db.close();raise ValueError("Unsupported catalogue schema")
    return db

def ingest(db_path, inventory_path):
    data=json.loads(Path(inventory_path).read_text(encoding="utf-8"))
    if not isinstance(data,dict) or not isinstance(data.get("files"),list) or not isinstance(data.get("root"),str):
        raise ValueError("Invalid inventory")
    root=Path(data["root"])
    if not root.is_absolute(): raise ValueError("Inventory root must be absolute")
    if data.get("truncated"):raise ValueError("Incomplete inventory; refusing import")
    count=0
    with connect(db_path) as db:
        for item in data["files"]:
            if not isinstance(item,dict) or not isinstance(item.get("path"),str) or type(item.get("size")) is not int or item["size"] < 0:
                raise ValueError("Invalid inventory item")
            relative=Path(item["path"])
            if relative.is_absolute() or ".." in relative.parts or "." in relative.parts or not relative.parts or "\\" in item["path"] or "\x00" in item["path"] or any(part in ("", ".") for part in item["path"].split("/")):
                raise ValueError("Unsafe inventory path")
            path=str(root/relative)
            if not (Path(path).parent == root or root in Path(path).parents):
                raise ValueError("Inventory path outside root")
            digest=item.get("sha256")
            if digest is not None and (not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest)):
                raise ValueError("Invalid SHA-256")
            identifier=str(uuid5(NAMESPACE_URL,path))
            db.execute("""INSERT INTO file_instances(id,edition_id,path,size_bytes,sha256)
              VALUES(?,NULL,?,?,?)
              ON CONFLICT(path) DO UPDATE SET size_bytes=excluded.size_bytes,sha256=COALESCE(excluded.sha256,file_instances.sha256),
                  observed_at=CURRENT_TIMESTAMP""",(identifier,path,item["size"],digest))
            count+=1
        db.execute("INSERT INTO audit_events(action,details_json) VALUES(?,?)",
                   ("inventory_import",json.dumps({"root":str(root),"count":count})))
    return count

def search(db_path,term,limit=30):
    if not 1<=limit<=500:raise ValueError("Invalid search limit")
    pattern="%"+term.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")+"%"
    with connect(db_path) as db:
        rows=db.execute("""SELECT id,path,size_bytes,sha256 FROM file_instances
                           WHERE path LIKE ? ESCAPE '\\' ORDER BY path LIMIT ?""",(pattern,limit)).fetchall()
    return [{"id":a,"path":b,"size_bytes":c,"sha256":d} for a,b,c,d in rows]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db",required=True)
    subs=p.add_subparsers(dest="command",required=True)
    x=subs.add_parser("import");x.add_argument("inventory")
    x=subs.add_parser("search");x.add_argument("term");x.add_argument("--limit",type=int,default=30)
    a=p.parse_args()
    try:
        result=ingest(a.db,a.inventory) if a.command=="import" else search(a.db,a.term,a.limit)
        print(json.dumps(result,indent=2))
    except (OSError,ValueError,sqlite3.Error,json.JSONDecodeError) as exc:
        print(str(exc),file=sys.stderr);return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
