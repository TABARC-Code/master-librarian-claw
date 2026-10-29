#!/usr/bin/env python3
"""Read-only local setup diagnostics. Does not install or alter anything."""
import argparse
import json
import platform
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('mini', 'small', 'medium', 'advanced')

def check(profile='small'):
    if profile not in PROFILES:
        raise ValueError('Unknown profile')
    config_path = ROOT / 'config' / 'profiles' / (profile + '.json')
    profile_config = json.loads(config_path.read_text(encoding='utf-8'))
    if profile_config.get('profile_id') != profile:
        raise ValueError('Profile identity mismatch')
    tools = {name: shutil.which(name) is not None for name in ('git', 'ollama', 'openclaw')}
    return {
        'system': platform.system(),
        'architecture': platform.machine(),
        'python': platform.python_version(),
        'sqlite': sqlite3.sqlite_version,
        'profile': profile,
        'model': profile_config['model'],
        'tools_available': tools,
        'skill_present': (ROOT / 'SKILL.md').is_file(),
        'setup_actions_taken': False,
        'notes': [
            'Tool detection does not prove a service is running or that the installed CLI is compatible.',
            'GPU acceleration and usable memory must be checked on the target host.',
            'No files, settings or services have been changed.'
        ]
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', choices=PROFILES, default='small')
    args = p.parse_args()
    try:
        print(json.dumps(check(args.profile), indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        p.exit(1, str(exc) + '\n')

if __name__ == '__main__':
    main()
