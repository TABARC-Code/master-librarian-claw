#!/usr/bin/env python3
"""Create or inspect a local SQLite catalogue. Never scans or changes collection files."""
import argparse
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "catalogue" / "schema_v1.sql"
VERSION = 2

def connect(path):
    connection = sqlite3.connect(str(path))
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=5000")
    return connection

def initialise(path):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > VERSION:
            raise RuntimeError("Catalogue created by a newer version; refusing downgrade")
        if version == 0:
            # Only initialise an entirely new database; migrations are separate.
            db.executescript(SCHEMA.read_text(encoding="utf-8"))
            db.execute("INSERT OR IGNORE INTO schema_version(version) VALUES (1)")
            db.execute("PRAGMA user_version=1")
        if version not in (0, 1, 2):
            raise RuntimeError("Unsupported catalogue version")
        results = db.execute("PRAGMA integrity_check").fetchone()
        if results[0] != "ok":
            raise RuntimeError("SQLite integrity check failed: " + str(results[0]))
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Foreign key check failed")
    return path

def stats(path):
    with connect(path) as db:
        return {table: db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                for table in ("works", "editions", "file_instances", "authorities", "relationships", "evidence")}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="SQLite database path (never point at a library file)")
    parser.add_argument("--init", action="store_true", help="Create database if necessary")
    args = parser.parse_args()
    path = Path(args.db).expanduser()
    if args.init:
        initialise(path)
        print("Catalogue ready:", path)
    elif not path.is_file():
        parser.error("Database not found; use --init for initial creation")
    print("Records:", stats(path))

if __name__ == "__main__":
    main()
