#!/usr/bin/env python3
"""Build SHA-256 checksums for paper-facing ToxicBench artifacts."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "toxictool_bench/results"
MANIFEST = RESULTS / "paper_run_manifest.csv"
OUTPUT = RESULTS / "artifact_sha256.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    paths = {
        ROOT / "toxictool_bench/evaluator.py",
        ROOT / "toxictool_bench/poisoners.py",
        MANIFEST,
    }
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            paths.add(ROOT / row["source"])
            paths.update(ROOT / task for task in row["tasks"].split(";"))
    paths.update(RESULTS.glob("*.csv"))
    paths.discard(OUTPUT)

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["path", "sha256", "bytes"])
        for path in sorted(paths):
            if not path.is_file():
                raise FileNotFoundError(path)
            writer.writerow([path.relative_to(ROOT), sha256(path), path.stat().st_size])
    print(f"Wrote checksums for {len(paths)} artifacts to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
