#!/usr/bin/env python3
"""Read-only file inventory. Symbolic links are never followed."""
import argparse, hashlib, json, os, stat, sys
from pathlib import Path

def inspect_tree(root, hash_files=False, max_files=100000, max_depth=32):
    root = Path(root).expanduser().absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Root must be an existing ordinary directory")
    if max_files < 1 or max_depth < 0:
        raise ValueError("Invalid scanning limit")
    files, issues, stack = [], [], [(root, 0)]
    while stack:
        folder, depth = stack.pop()
        try:
            entries = sorted(os.scandir(folder), key=lambda entry: entry.name)
        except OSError as exc:
            issues.append({"path": str(folder), "error": type(exc).__name__})
            continue
        for entry in entries:
            try:
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    issues.append({"path": entry.path, "error": "symlink_skipped"})
                    continue
                if stat.S_ISDIR(info.st_mode):
                    if depth >= max_depth:
                        issues.append({"path": entry.path, "error": "depth_limit"})
                    else:
                        stack.append((Path(entry.path), depth + 1))
                    continue
                if not stat.S_ISREG(info.st_mode):
                    issues.append({"path": entry.path, "error": "special_file_skipped"})
                    continue
                if len(files) >= max_files:
                    issues.append({"path": entry.path, "error": "file_limit"})
                    return {"root": str(root), "files": files, "issues": issues, "truncated": True}
                item = {"path": str(Path(entry.path).relative_to(root)), "size": info.st_size, "modified_ns": info.st_mtime_ns}
                if hash_files:
                    digest = hashlib.sha256()
                    with open(entry.path, "rb") as stream:
                        for block in iter(lambda: stream.read(1048576), b""):
                            digest.update(block)
                    after = entry.stat(follow_symlinks=False)
                    if (after.st_size, after.st_mtime_ns) != (info.st_size, info.st_mtime_ns):
                        issues.append({"path": entry.path, "error": "changed_during_hash"})
                    else:
                        item["sha256"] = digest.hexdigest()
                files.append(item)
            except OSError as exc:
                issues.append({"path": entry.path, "error": type(exc).__name__})
    files.sort(key=lambda item: item["path"])
    return {"root": str(root), "files": files, "issues": issues, "truncated": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root")
    parser.add_argument("--hash", action="store_true")
    parser.add_argument("--max-files", type=int, default=100000)
    parser.add_argument("--max-depth", type=int, default=32)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_tree(args.root, args.hash, args.max_files, args.max_depth), indent=2))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
