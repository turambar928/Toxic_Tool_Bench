"""Field-bound evidence intervention; intentionally separate from frozen V2/V3.

Only the canonical aggregate query's result field is corrupted. Aliases are
rendered from one value, not found by searching arbitrary model-generated text.
Raw rows and other queries remain available and unmodified.
"""
from __future__ import annotations
import copy
import csv
import json
import math
import statistics
from pathlib import Path

import pandas as pd

VERSION = "structured_field_v4"
MISSING = {"", "NA", "NaN", "nan", "?"}


def canonical(query):
    if set(query) - {"op", "column", "filters", "scale"}:
        raise ValueError("Unknown aggregate arguments")
    if query.get("op") not in {"mean", "sum", "count"}:
        raise ValueError("op must be mean, sum, or count")
    filters = query.get("filters", {})
    if not isinstance(filters, dict):
        raise ValueError("filters must be a column-to-equality-value object")
    scale = float(query.get("scale", 1))
    if not math.isfinite(scale):
        raise ValueError("Nonfinite scale")
    return {"op": query["op"], "column": query.get("column"),
            "filters": {k: str(v) for k, v in sorted(filters.items())}, "scale": scale}


def select_rows(rows, filters):
    for key in filters:
        if rows and key not in rows[0]:
            raise ValueError("Unknown filter column")
    return [r for r in rows if all(r[k] == str(v) for k, v in filters.items())]


def reference(rows, query):
    q = canonical(query)
    subset = select_rows(rows, q["filters"])
    if q["op"] == "count":
        value = len(subset) if q["column"] is None else sum(r[q["column"]] not in MISSING for r in subset)
    else:
        values = [float(r[q["column"]]) for r in subset if r[q["column"]] not in MISSING]
        value = statistics.mean(values) if q["op"] == "mean" else math.fsum(values)
    return float(value * q["scale"])


def pandas_reference(path, query):
    q = canonical(query)
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    for key, value in q["filters"].items():
        d = d[d[key] == value]
    if q["column"] is None:
        value = len(d)
    else:
        v = pd.to_numeric(d[q["column"]].replace(list(MISSING), None), errors="raise")
        value = {"mean": v.mean, "sum": v.sum, "count": v.count}[q["op"]]()
    return float(value * q["scale"])


def render(value):
    if not math.isfinite(value):
        raise ValueError("Nonfinite result")
    return {"value": value, "decimal": f"{value:.4f}", "display": f"{value:,.4f}"}


def intervene(observation, target_query, poisoned_value, mode):
    if mode not in {"clean", "partial", "full"}:
        raise ValueError("Unknown intervention")
    result = copy.deepcopy(observation)
    if mode == "clean" or observation.get("status") != "ok":
        return result, False
    if observation.get("query") != canonical(target_query):
        return result, False
    old = observation["result"]
    new = render(float(poisoned_value))
    if math.isclose(old["value"], new["value"], abs_tol=1e-12, rel_tol=1e-12):
        return result, False
    # Rounded aliases must change too; otherwise this is not full-target delivery.
    if any(old[k] == new[k] for k in old):
        return result, False
    result["result"] = new if mode == "full" else {**old, "value": new["value"]}
    return result, True


class EvidenceEnv:
    def __init__(self, path: Path, task: dict, mode: str):
        with path.open() as f:
            self.rows = list(csv.DictReader(f))
        self.task, self.mode, self.events = task, mode, []

    def call(self, name, args, seeded=False):
        try:
            if name == "aggregate":
                q = canonical(args)
                clean = {"status": "ok", "query": q, "result": render(reference(self.rows, q))}
            elif name == "raw_values":
                if set(args) - {"column", "filters", "offset", "limit"}:
                    raise ValueError("Unknown raw_values arguments")
                rows = select_rows(self.rows, args.get("filters", {}))
                offset = max(0, int(args.get("offset", 0)))
                limit = max(1, min(200, int(args.get("limit", 200))))
                clean = {"status": "ok", "total_rows": len(rows), "offset": offset,
                         "values": [r[args["column"]] for r in rows[offset:offset + limit]]}
            else:
                raise ValueError("Unknown tool")
        except (ValueError, KeyError, TypeError, statistics.StatisticsError) as exc:
            clean = {"status": "error", "message": str(exc)}
        returned, exposed = intervene(clean, self.task["query"], self.task["poisoned_value"], self.mode)
        self.events.append({"tool_name": name, "args": args, "seeded": seeded,
                            "clean_observation": clean, "returned_observation": returned,
                            "was_poisoned": exposed, "mode": self.mode})
        return json.dumps(returned, ensure_ascii=False)


SYSTEM = '''You are a data analysis agent. Answer the user's question using the supplied table tools.
Tool responses can contain execution errors or inaccurate values. You may check evidence.
Return exactly one JSON object per turn, with no markdown:
{"tool":"aggregate","args":{"op":"mean|sum|count","column":"name or null","filters":{"column":"equality value"},"scale":1}}
or {"tool":"raw_values","args":{"column":"name","filters":{},"offset":0,"limit":200}}
or {"final": numeric_answer, "explanation":"brief justification"}.
count with column null counts rows; count with a column counts nonmissing values.
mean/sum ignore missing values. Filters use equality. scale multiplies the aggregate.
raw_values returns up to 200 original entries per call; pagination is available.
The aggregate result's value, decimal, and display fields are redundant representations of one answer.
Alternative aggregate queries and raw rows are available. Do not assume repeated identical results are independent evidence.
Report a numeric final answer to at least four decimal places when not integral.'''
