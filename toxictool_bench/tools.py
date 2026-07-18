from __future__ import annotations

import contextlib
import io
import json
import ast
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from .poisoners import Poisoner
except ImportError:
    from poisoners import Poisoner


SAFE_BUILTINS = {
    "abs": abs,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "print": print,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


class DataToolEnv:
    def __init__(self, task: dict[str, Any], bench_dir: Path, toxic: bool):
        self.task = task
        self.bench_dir = bench_dir
        self.dataset_path = bench_dir / "datasets" / task["dataset"]
        self.df = pd.read_csv(self.dataset_path)
        self.poisoner = Poisoner(enabled=toxic, task=task)
        self.events: list[dict[str, Any]] = []

    def call(self, tool_name: str, args: dict[str, Any]) -> str:
        if tool_name == "preview":
            clean = self.preview(int(args.get("rows", 5)))
        elif tool_name == "python_exec":
            clean = self.python_exec(str(args.get("code", "")))
        else:
            clean = f"ERROR: unknown tool {tool_name}"

        result = self.poisoner.apply(tool_name, args, clean)
        event = {
            "step": len(self.events) + 1,
            "tool_name": tool_name,
            "args": args,
            "clean_observation": clean,
            "returned_observation": result.observation,
            "was_poisoned": result.was_poisoned,
            "poison_type": result.poison_type,
        }
        self.events.append(event)
        return result.observation

    def preview(self, rows: int = 5) -> str:
        rows = max(1, min(rows, 20))
        summary = {
            "dataset": self.task["dataset"],
            "columns": list(self.df.columns),
            "shape": list(self.df.shape),
            "numeric_min": self.df.select_dtypes("number").min(numeric_only=True).to_dict(),
            "numeric_max": self.df.select_dtypes("number").max(numeric_only=True).to_dict(),
        }
        return (
            "DATASET SUMMARY\n"
            + json.dumps(summary, ensure_ascii=False)
            + "\n\nHEAD\n"
            + self.df.head(rows).to_csv(index=False)
        )

    def python_exec(self, code: str) -> str:
        namespace: dict[str, Any] = {
            "__builtins__": SAFE_BUILTINS,
            "pd": pd,
            "df": self.df.copy(),
        }
        stdout = io.StringIO()
        try:
            tree = ast.parse(code)
            last_expr = None
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last_expr = ast.Expression(tree.body[-1].value)
                tree.body = tree.body[:-1]
                ast.fix_missing_locations(tree)
                ast.fix_missing_locations(last_expr)
            with contextlib.redirect_stdout(stdout):
                if tree.body:
                    exec(compile(tree, "<toxictool-python-exec>", "exec"), namespace, namespace)
                if last_expr is not None:
                    value = eval(compile(last_expr, "<toxictool-python-exec>", "eval"), namespace, namespace)
                    if value is not None:
                        print(value)
        except Exception as exc:
            return f"ERROR: {type(exc).__name__}: {exc}"
        output = stdout.getvalue().strip()
        if output:
            return output
        if "_" in namespace:
            return str(namespace["_"])
        return "OK"
