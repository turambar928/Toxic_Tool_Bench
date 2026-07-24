# ToxicBench Pilot Results

This file archives the early 4-task pilot runs. These results are useful for development history, but they should not be cited as the main paper evidence. The formal results are in `EXPERIMENT_RESULTS.md`.

## Prompt-Profile Pilot

Date: 2026-07-06

Model: `gpt-5.4-mini`

Tasks: 4 numerical silent-poisoning tasks

Environments:

- `clean`: normal tool observations.
- `toxic`: selected tool observations silently poisoned while keeping valid return format.

### Agent Profiles

These were prompt-level representative profiles run through the same tool loop:

- `react`: standard ReAct-style tool-use agent.
- `openhands_codeact`: OpenHands/CodeAct-style profile, representing code-action agents.
- `plan_execute`: plan-and-execute profile.
- `reflexion`: reflection/critique profile.
- `caution`: generic caution prompt.
- `ibf`: Implicit Bias Filter profile.

Note: `openhands_codeact` was a profile adapter, not the full OpenHands runtime.

### Rescored Summary

The first scoring pass had a false-positive bug for short labels such as `C`, because substring matching could match words such as `conversion`. The table below uses the corrected evaluator and `.rescored` files.

| Agent profile | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `react` | 0.75 | 0.50 | 0.25 | 0.00 | 0.00 | 0.25 | 0.25 |
| `openhands_codeact` | 0.75 | 0.50 | 0.25 | 0.50 | 0.00 | 0.00 | 0.00 |
| `plan_execute` | 1.00 | 0.50 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 |
| `reflexion` | 0.75 | 0.50 | 0.25 | 0.25 | 0.00 | 0.00 | 0.00 |
| `caution` | 1.00 | 1.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 |
| `ibf` | 0.75 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

### Result Files

```text
20260706-181734_react_gpt-5.4-mini_both.rescored.jsonl
20260706-181932_openhands_codeact_gpt-5.4-mini_both.rescored.jsonl
20260706-182046_plan_execute_gpt-5.4-mini_both.rescored.jsonl
20260706-182217_reflexion_gpt-5.4-mini_both.rescored.jsonl
20260706-182315_caution_gpt-5.4-mini_both.rescored.jsonl
20260706-182438_ibf_gpt-5.4-mini_both.rescored.jsonl
```

## Four-Task Full-Adapter Pilot

After the prompt-profile pilot, the following full framework adapters were implemented and run on the same 4 numerical tasks:

- `langgraph_react_full`: real LangGraph `StateGraph` loop with benchmark tools.
- `smolagents_toolcalling`: real Hugging Face `ToolCallingAgent` with benchmark tools.
- `data2mcp_dataframe`: real `data2mcp_v2.Router` with its DataFrame agent tool and poisoned FastMCP tool observations.
- `pandasai_dataframe`: real PandasAI `Agent.chat()` with benchmark dataframe and coarse poisoned chat-result observation.
- `da_agent_full`: real DA-Agent `DAAgentEnv + PromptAgent` action loop with poisoned environment observations.
- `autogen_tool_agent`: real AutoGen `AssistantAgent` with OpenAI-compatible model client and benchmark function tools.

Model: `gpt-5.4-mini`

Corrected scoring: for segment-selection tasks, success requires the correct segment label, not just the correct numeric value.

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.25 | 0.75 | 0.50 | 0.00 | 0.00 | 0.00 |
| `smolagents_toolcalling` | 1.00 | 0.75 | 0.25 | 0.25 | 0.00 | 0.00 | 0.00 |
| `data2mcp_dataframe` | 0.75 | 0.25 | 0.50 | 0.75 | 0.00 | 0.00 | 0.00 |
| `pandasai_dataframe` | 1.00 | 0.25 | 0.75 | 0.75 | 0.00 | 0.00 | 0.00 |
| `da_agent_full` | 1.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.75 | 0.50 |
| `autogen_tool_agent` | 1.00 | 0.50 | 0.50 | 0.75 | 0.00 | 0.00 | 0.00 |

### Result Files

```text
paper/iclr/toxictool_bench/results/20260707-005754_langgraph_react_full_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-005947_smolagents_toolcalling_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-051901_data2mcp_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-054833_pandasai_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-055518_da_agent_full_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-061147_autogen_tool_agent_gpt-5.4-mini_both.rescored.jsonl
```
