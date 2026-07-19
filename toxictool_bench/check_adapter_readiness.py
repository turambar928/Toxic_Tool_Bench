from __future__ import annotations

import argparse
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AdapterCheck:
    name: str
    paths: tuple[Path, ...]
    imports: tuple[str, ...]
    note: str


CHECKS = (
    AdapterCheck(
        name="langgraph_react_full",
        paths=(
            REPO_ROOT / "baseline_agent" / "langgraph" / "libs" / "langgraph",
            REPO_ROOT / "baseline_agent" / "langgraph" / "libs" / "prebuilt",
        ),
        imports=("langgraph.graph",),
        note="LangGraph local checkout.",
    ),
    AdapterCheck(
        name="smolagents_toolcalling",
        paths=(REPO_ROOT / "baseline_agent" / "smolagents" / "src",),
        imports=("smolagents",),
        note="smolagents local checkout.",
    ),
    AdapterCheck(
        name="data2mcp_dataframe",
        paths=(REPO_ROOT / "src",),
        imports=("data2mcp_v2.config", "fastmcp.tools"),
        note="data2mcp_v2 package and FastMCP dependencies.",
    ),
    AdapterCheck(
        name="data2mcp_dataframe_caution",
        paths=(REPO_ROOT / "src",),
        imports=("data2mcp_v2.config", "fastmcp.tools"),
        note="same dependency surface as base data2mcp.",
    ),
    AdapterCheck(
        name="data2mcp_dataframe_expectation_only",
        paths=(REPO_ROOT / "src",),
        imports=("data2mcp_v2.config", "fastmcp.tools"),
        note="same dependency surface as base data2mcp.",
    ),
    AdapterCheck(
        name="data2mcp_dataframe_verification_only",
        paths=(REPO_ROOT / "src",),
        imports=("data2mcp_v2.config", "fastmcp.tools"),
        note="same dependency surface as base data2mcp.",
    ),
    AdapterCheck(
        name="data2mcp_dataframe_guarded",
        paths=(REPO_ROOT / "src",),
        imports=("data2mcp_v2.config", "fastmcp.tools"),
        note="same dependency surface as base data2mcp.",
    ),
    AdapterCheck(
        name="data2mcp_dataframe_guarded_light",
        paths=(REPO_ROOT / "src",),
        imports=("data2mcp_v2.config", "fastmcp.tools"),
        note="same dependency surface as base data2mcp.",
    ),
    AdapterCheck(
        name="pandasai_dataframe",
        paths=(
            REPO_ROOT / "baseline_agent" / "pandas-ai",
            REPO_ROOT / "baseline_agent" / "pandas-ai" / "extensions" / "llms" / "litellm",
        ),
        imports=("pandasai", "pandasai_litellm"),
        note="PandasAI local checkout and LiteLLM extension.",
    ),
    AdapterCheck(
        name="autogen_tool_agent",
        paths=(
            REPO_ROOT / "baseline_agent" / "autogen" / "python" / "packages" / "autogen-core" / "src",
            REPO_ROOT / "baseline_agent" / "autogen" / "python" / "packages" / "autogen-agentchat" / "src",
            REPO_ROOT / "baseline_agent" / "autogen" / "python" / "packages" / "autogen-ext" / "src",
        ),
        imports=("autogen_agentchat.agents", "autogen_ext.models.openai", "autogen_core.models"),
        note="AutoGen local checkout.",
    ),
    AdapterCheck(
        name="da_agent_full",
        paths=(REPO_ROOT / "baseline_agent" / "da-agent",),
        imports=(),
        note="DA-Agent local checkout; this adapter shells out through the local task runner.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local dependency readiness for ToxicTool-Bench full adapters.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any adapter is not ready.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
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
                print(f"  - {path.relative_to(REPO_ROOT)}")
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
