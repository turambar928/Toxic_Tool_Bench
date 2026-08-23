from __future__ import annotations

import argparse
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_DIR = Path(os.environ.get("TOXICTOOL_BASELINE_DIR", REPO_ROOT / "baseline_agent"))
@dataclass(frozen=True)
class AdapterCheck:
    name: str
    paths: tuple[Path, ...]
    imports: tuple[str, ...]
    note: str


CHECKS = (
    AdapterCheck(
        name="langgraph_react_family",
        paths=(
            BASELINE_DIR / "langgraph" / "libs" / "langgraph",
            BASELINE_DIR / "langgraph" / "libs" / "prebuilt",
        ),
        imports=("langgraph.graph",),
        note="LangGraph base, guard, ablation, and policy variants share this dependency surface.",
    ),
    AdapterCheck(
        name="smolagents_toolcalling",
        paths=(BASELINE_DIR / "smolagents" / "src",),
        imports=("smolagents",),
        note="smolagents local checkout.",
    ),
    AdapterCheck(
        name="pandasai_dataframe",
        paths=(
            BASELINE_DIR / "pandas-ai",
            BASELINE_DIR / "pandas-ai" / "extensions" / "llms" / "litellm",
        ),
        imports=("pandasai", "pandasai_litellm"),
        note="PandasAI local checkout and LiteLLM extension.",
    ),
    AdapterCheck(
        name="autogen_tool_agent",
        paths=(
            BASELINE_DIR / "autogen" / "python" / "packages" / "autogen-core" / "src",
            BASELINE_DIR / "autogen" / "python" / "packages" / "autogen-agentchat" / "src",
            BASELINE_DIR / "autogen" / "python" / "packages" / "autogen-ext" / "src",
        ),
        imports=("autogen_agentchat.agents", "autogen_ext.models.openai", "autogen_core.models"),
        note="AutoGen local checkout.",
    ),
    AdapterCheck(
        name="da_agent_full",
        paths=(BASELINE_DIR / "da-agent",),
        imports=(),
        note="DA-Agent local checkout; this adapter shells out through the local task runner.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local dependency readiness for ToxicBench full adapters.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any adapter is not ready.")
    return parser.parse_args()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    args = parse_args()
    print(f"baseline_dir={BASELINE_DIR}")
    missing_any = False
    for check in CHECKS:
        missing_paths = [path for path in check.paths if not path.exists()]
        for path in check.paths:
            if path.exists():
                sys.path.insert(0, str(path))
        missing_imports = []
        for module_name in check.imports:
            try:
                importlib.import_module(module_name)
            except Exception as exc:
                missing_imports.append(f"{module_name} ({type(exc).__name__}: {exc})")

        ready = not missing_paths and not missing_imports
        missing_any = missing_any or not ready
        status = "READY" if ready else "MISSING"
        print(f"[{status}] {check.name}")
        if missing_paths:
            print("  missing paths:")
            for path in missing_paths:
                print(f"  - {_display_path(path)}")
        if missing_imports:
            print("  missing imports:")
            for item in missing_imports:
                print(f"  - {item}")
        if not ready:
            print(f"  note: {check.note}")

    if args.strict and missing_any:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
