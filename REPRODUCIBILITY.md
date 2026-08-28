# Reproducibility

## Environment

The validated public-adapter environment is recorded in `requirements.txt`.
Install it with:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The benchmark does not require the ignored `api` file to run its scorer or tests.
Model runs require a local API configuration with a supported model and endpoint;
the configuration is deliberately excluded from the repository.

## Determinism

All bootstrap commands default to seed `13`. Probabilistic poisoning derives its
gate from a SHA-256 digest of task ID, tool name, call index, and arguments.
Tasks, raw logs, summaries, and their checksums are listed in
`toxictool_bench/results/paper_run_manifest.csv` and
`toxictool_bench/results/artifact_sha256.csv`.

## Verification runs

The complete repeated-observation matrix is launched by:

```bash
MODEL=gpt-5.4-mini bash toxictool_bench/run_full_verification_stress.sh
```

This matrix uses the same source tables for both routes. It tests repeated
returned-observation corruption, not source-independent or Byzantine corruption.
For a budget-matched control, use adapter
`langgraph_react_double_pass`; it executes two ordinary routes without guard
expectations or access to the primary answer.

## External checkouts

Adapters that rely on source checkouts accept `TOXICTOOL_BASELINE_DIR`. Their
expected import paths are documented in `RUN_COMMANDS.md`. A release should
record the exact checkout commit for every external adapter before archival;
the current experiments use installed public packages for the adapters listed
in `requirements.txt` and do not vendor those repositories.

## Release audit

Run the following before publishing:

```bash
python3 toxictool_bench/release_audit.py
python3 toxictool_bench/build_artifact_checksums.py
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
```
