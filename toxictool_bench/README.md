# ToxicTool-Bench Pilot

This folder contains a runnable pilot benchmark for silent tool poisoning in data agents.

## Smoke test without network

```bash
python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile heuristic_naive \
  --env both \
  --limit 2
```

## List available models

```bash
python3 paper/iclr/toxictool_bench/run_bench.py --list-models
```

The script reads `paper/iclr/api` at runtime. It does not copy the API key into result files.

## Run representative agent profiles

Vanilla ReAct-style agent:

```bash
python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile react \
  --model gpt-5.4-mini \
  --env both
```

Cautious prompt baseline:

```bash
python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile caution \
  --model gpt-5.4-mini \
  --env both
```

IBF defense:

```bash
python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile ibf \
  --model gpt-5.4-mini \
  --env both
```

Prompt-style adapters for your existing agents:

```bash
python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile data2mcp_prompt \
  --model gpt-5.4-mini \
  --env both

python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile da_agent_prompt \
  --model gpt-5.4-mini \
  --env both
```

Representative public-agent styles:

```bash
python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile openhands_codeact \
  --model gpt-5.4-mini \
  --env both

python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile plan_execute \
  --model gpt-5.4-mini \
  --env both

python3 paper/iclr/toxictool_bench/run_bench.py \
  --agent-profile reflexion \
  --model gpt-5.4-mini \
  --env both
```

## Suggested experiment matrix

Run the five profiles on at least two model families:

```text
Profiles:
  react
  caution
  ibf
  openhands_codeact
  plan_execute
  reflexion
  data2mcp_prompt
  da_agent_prompt

Models:
  gpt-5.4-mini
  claude-sonnet-4-6
  Qwen3.6-35B-A3B-no-thinking
```

Primary table:

```text
Agent profile | Model | Clean TSR | Poisoned TSR | Delta TSR | BCR | ADR | VR | RR
```

For the paper, report BCR among tasks where the same agent/model succeeds in the clean environment.

## Run full framework adapters

These use complete framework code rather than prompt-only profiles.

LangGraph ReAct full adapter:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:baseline_agent/langgraph/libs/langgraph:baseline_agent/langgraph/libs/prebuilt \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --adapter langgraph_react_full \
  --model gpt-5.4-mini \
  --env both
```

Hugging Face smolagents ToolCallingAgent full adapter:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:baseline_agent/smolagents/src \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --adapter smolagents_toolcalling \
  --model gpt-5.4-mini \
  --env both
```

AutoGen AssistantAgent full adapter:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:baseline_agent/autogen/python/packages/autogen-core/src:baseline_agent/autogen/python/packages/autogen-agentchat/src:baseline_agent/autogen/python/packages/autogen-ext/src \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --adapter autogen_tool_agent \
  --model gpt-5.4-mini \
  --env both
```

data2mcp DataFrame full adapter:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:src \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --adapter data2mcp_dataframe \
  --model gpt-5.4-mini \
  --env both
```

PandasAI DataFrame full adapter:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:baseline_agent/pandas-ai:baseline_agent/pandas-ai/extensions/llms/litellm \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --adapter pandasai_dataframe \
  --model gpt-5.4-mini \
  --env both
```

DA-Agent full adapter:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:baseline_agent/da-agent \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --adapter da_agent_full \
  --model gpt-5.4-mini \
  --env both \
  --max-steps 10
```

## Expanded benchmark

The expanded task file contains 34 tasks:

```text
paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl
```

Run any full adapter on it with `--tasks`:

```bash
PYTHONPATH=paper/iclr/toxictool_bench:baseline_agent/langgraph/libs/langgraph:baseline_agent/langgraph/libs/prebuilt \
python3 paper/iclr/toxictool_bench/run_full_bench.py \
  --tasks paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl \
  --adapter langgraph_react_full \
  --model gpt-5.4-mini \
  --env both
```

Rescore expanded results with the same task file:

```bash
python3 paper/iclr/toxictool_bench/rescore_results.py \
  --tasks paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl \
  paper/iclr/toxictool_bench/results/RESULT.jsonl
```
