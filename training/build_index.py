#!/usr/bin/env python3
"""build_index.py -- scan the data drive once and write data_index.jsonl.

    python build_index.py configs/base.yaml
    python build_index.py configs/base.yaml data.root="D:/zeit-data"

Records every usable audio file with its role (speech / noise / rir), noise
class, split, sample rate and length. Training reads this instead of walking
100 GB of folders every time. Rerun whenever data is added.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from zeit import config                                       # noqa: E402
from zeit.data import build_index                             # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cfg = config.load(sys.argv[1], sys.argv[2:])
    out = cfg.data.index if os.path.isabs(cfg.data.index) else os.path.join(HERE, cfg.data.index)
    print(f"\n  scanning {cfg.data.root}\n")
    rows = build_index(cfg, out)
    by = {}
    for r in rows:
        k = (r["role"], r["split"])
        by[k] = by.get(k, 0) + 1
    print()
    for (role, split), n in sorted(by.items()):
        print(f"    {role:<7} {split:<6} {n:>9,}")
    missing = [s for s in ("train", "val", "test") if not any(r["split"] == s and r["role"] == "speech" for r in rows)]
    if missing:
        print(f"\n  !! no speech in split(s): {missing} -- training will refuse to start")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
