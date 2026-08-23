from __future__ import annotations

import argparse
import re
from pathlib import Path


COMMAND_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
CITE_RE = re.compile(r"\\cite(?:p|t|alp|alt)?(?:\[[^\]]*\]){0,2}\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|autoref|cref|Cref)\{([^}]+)\}")
BIB_RE = re.compile(r"@\w+\{([^,\s]+)")
BIBLIOGRAPHY_RE = re.compile(r"\\bibliography\{([^}]+)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
PLACEHOLDER_RE = re.compile(r"(?:\?\?|\bTODO\b|\bTBD\b|PLACEHOLDER|\\cite\{\})", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Static paper checks for missing TeX inputs, refs, and citations.")
    parser.add_argument("--main", type=Path, default=Path("main.tex"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.main.resolve().parent
    tex_files = collect_tex_files(args.main, root)
    tex_text = "\n".join(path.read_text(encoding="utf-8") for path in tex_files)

    label_list = LABEL_RE.findall(tex_text)
    labels = set(label_list)
    duplicate_labels = sorted(label for label in labels if label_list.count(label) > 1)
    refs = split_keys(REF_RE.findall(tex_text))
    missing_refs = sorted(ref for ref in refs if ref not in labels)

    bib_paths = bibliography_paths(args.main, root)
    bib_key_list: list[str] = []
    for path in bib_paths:
        if not path.exists():
            raise SystemExit(f"Missing bibliography file: {path}")
        bib_key_list.extend(BIB_RE.findall(path.read_text(encoding="utf-8")))
    bib_keys = set(bib_key_list)
    duplicate_bib_keys = sorted(key for key in bib_keys if bib_key_list.count(key) > 1)
    cites = split_keys(CITE_RE.findall(tex_text))
    missing_cites = sorted(cite for cite in cites if cite not in bib_keys)

    missing_inputs = [
        str(path)
        for path in referenced_inputs(args.main, root)
        if not path.exists()
    ]
    missing_graphics = [raw for raw in GRAPHICS_RE.findall(tex_text) if not graphic_exists(root, raw)]
    placeholders = sorted(set(match.group(0) for match in PLACEHOLDER_RE.finditer(tex_text)))

    print(f"tex_files={len(tex_files)}")
    print(f"labels={len(labels)} refs={len(refs)}")
    print(f"bib_keys={len(bib_keys)} cites={len(cites)}")
    if missing_inputs:
        print("Missing inputs:")
        for item in missing_inputs:
            print(f"  {item}")
    if missing_refs:
        print("Missing refs:")
        for item in missing_refs:
            print(f"  {item}")
    if missing_cites:
        print("Missing citations:")
        for item in missing_cites:
            print(f"  {item}")
    if missing_graphics:
        print("Missing graphics:")
        for item in missing_graphics:
            print(f"  {item}")
    if duplicate_labels:
        print("Duplicate labels:")
        for item in duplicate_labels:
            print(f"  {item}")
    if duplicate_bib_keys:
        print("Duplicate bibliography keys:")
        for item in duplicate_bib_keys:
            print(f"  {item}")
    if placeholders:
        print("Unresolved placeholders:")
        for item in placeholders:
            print(f"  {item}")
    if missing_inputs or missing_refs or missing_cites or missing_graphics or duplicate_labels or duplicate_bib_keys or placeholders:
        raise SystemExit(1)
    print("Static paper check passed.")


def collect_tex_files(main: Path, root: Path) -> list[Path]:
    files = [main]
    for path in referenced_inputs(main, root):
        if path.exists():
            files.append(path)
    return files


def referenced_inputs(main: Path, root: Path) -> list[Path]:
    text = main.read_text(encoding="utf-8")
    paths = []
    for raw in COMMAND_RE.findall(text):
        path = root / raw
        if path.suffix == "":
            path = path.with_suffix(".tex")
        paths.append(path)
    return paths


def bibliography_paths(main: Path, root: Path) -> list[Path]:
    text = main.read_text(encoding="utf-8")
    paths = []
    for group in BIBLIOGRAPHY_RE.findall(text):
        for raw in group.split(","):
            path = root / raw.strip()
            if path.suffix == "":
                path = path.with_suffix(".bib")
            paths.append(path)
    return paths


def split_keys(groups: list[str]) -> set[str]:
    keys: set[str] = set()
    for group in groups:
        keys.update(key.strip() for key in group.split(",") if key.strip())
    return keys


def graphic_exists(root: Path, raw: str) -> bool:
    path = root / raw
    if path.suffix:
        return path.exists()
    return any(path.with_suffix(suffix).exists() for suffix in (".pdf", ".png", ".jpg", ".jpeg", ".eps"))


if __name__ == "__main__":
    main()
