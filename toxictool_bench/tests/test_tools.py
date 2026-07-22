from __future__ import annotations

from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from tools import DataToolEnv  # noqa: E402


def test_data_tool_env_exposes_aux_tables_and_joinable_namespace(tmp_path):
    bench_dir = tmp_path / "bench"
    datasets = bench_dir / "datasets"
    datasets.mkdir(parents=True)

    (datasets / "main_orders.csv").write_text(
        "customer_id,order_value_usd\nC1,10\nC2,20\n",
        encoding="utf-8",
    )
    (datasets / "main_customers.csv").write_text(
        "customer_id,segment\nC1,Enterprise\nC2,SMB\n",
        encoding="utf-8",
    )

    task = {
        "task_id": "join_test",
        "dataset": "main_orders.csv",
        "aux_datasets": ["main_customers.csv"],
        "poison": {"enabled": False},
    }
    env = DataToolEnv(task=task, bench_dir=bench_dir, toxic=False)

    preview = env.preview(rows=2)
    assert "tables" in preview
    assert "main_customers" in preview

    output = env.python_exec(
        "joined = tables['main_orders'].merge(tables['main_customers'], on='customer_id')\n"
        "print(joined.groupby('segment')['order_value_usd'].sum().to_string())"
    )

    assert "Enterprise" in output
    assert "SMB" in output

    filename_output = env.python_exec(
        "import pandas as pd\n"
        "joined = tables['main_orders.csv'].merge(tables['main_customers.csv'], on='customer_id')\n"
        "print(pd.DataFrame({'segments': sorted(joined['segment'].unique())}).to_string(index=False))"
    )

    assert "Enterprise" in filename_output
    assert "SMB" in filename_output
