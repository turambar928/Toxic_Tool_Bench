#!/usr/bin/env python3
"""Scan tracked release files for secrets and machine-local information."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    # Variable names such as api_key are expected in the client code. Detect
    # credential-shaped values rather than configuration terminology.
    "api-token": re.compile(r"(?:sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})", re.I),
    "absolute-home": re.compile(r"/home/[A-Za-z0-9_.-]+"),
    "private-endpoint": re.compile(r"https?://(?:10\.|127\.|192\.168\.|localhost)", re.I),
}


def main() -> int:
    files = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    findings: list[str] = []
    for name in files:
        path = ROOT / name
        if not path.is_file() or path.stat().st_size > 20_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {name}")
    if findings:
        print("Release audit findings:")
        print("\n".join(sorted(set(findings))))
        return 1
    print(f"Release audit passed for {len(files)} visible files; ignored secrets were not scanned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
