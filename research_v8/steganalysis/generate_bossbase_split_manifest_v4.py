#!/usr/bin/env python3
"""Regenerate the frozen BOSSBase V4 split manifest exactly.

The split was frozen before V4/V5/V6/V8 headline evaluation and depends only
on image filenames, never on image content or detector outcomes.
"""
from __future__ import annotations
import argparse, csv, hashlib
from pathlib import Path

SALT = "IG-CACHIN-BOSSBASE-V4-20260910"
EXPECTED_SHA256 = "d132a45c62dd6ea8c6f9a1a0aa088f56d84ad1ffe8bc11e5054f280d8f6ed631"
N_IMAGES = 10000
N_FIT = 3500
N_CAL = 1500
N_HOLDOUT = 5000

def rank_hash(name: str) -> str:
    return hashlib.sha256(f"{SALT}|{name}".encode("utf-8")).hexdigest()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def build(out: Path) -> None:
    names = [f"{i}.pgm" for i in range(1, N_IMAGES + 1)]
    ranked = sorted(((rank_hash(name), name) for name in names), key=lambda x: (x[0], x[1]))
    split = {}
    for j, (_, name) in enumerate(ranked):
        if j < N_FIT:
            split[name] = "fit"
        elif j < N_FIT + N_CAL:
            split[name] = "calibration"
        else:
            split[name] = "holdout"

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["image", "split", "rank_hash"])
        for name in names:
            w.writerow([name, split[name], rank_hash(name)])

    got = sha256(out)
    if got != EXPECTED_SHA256:
        raise RuntimeError(f"manifest SHA-256 mismatch: {got} != {EXPECTED_SHA256}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    build(args.out)
    print(f"PASS {args.out} sha256={sha256(args.out)}")

if __name__ == "__main__":
    main()
