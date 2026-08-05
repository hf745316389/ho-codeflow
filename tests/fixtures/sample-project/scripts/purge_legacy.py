"""Permanently delete archived event files.

There is no undo and no backup. Once a legacy file is removed the events in
it are gone.

Usage: python scripts/purge_legacy.py
"""

import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    removed = []
    for path in glob.glob(os.path.join(ROOT, "data", "legacy_events_*.json")):
        os.remove(path)
        removed.append(os.path.basename(path))
    print("purged: " + (", ".join(removed) if removed else "(nothing)"))


if __name__ == "__main__":
    main()
