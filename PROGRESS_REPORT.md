# ToxicTool-Bench Progress Report

Last updated: 2026-07-19

## 现在到哪一步了

当前已经完成了从 benchmark 原型、正式实验、guarded defense ablation 到论文主线整理的闭环：

- Benchmark 框架已经能运行 clean/toxic paired evaluation。
- 6 个 full-agent adapter 已经接入并完成 `gpt-5.4-mini` expanded 实验。
- 5 个非 DA-Agent adapter 已经完成 `gpt-5.4-mini`、`claude-sonnet-4-6`、`Qwen3.6-35B-A3B-no-thinking` 三模型 cross-model 实验。
- 指标漏洞已经审计并修复，当前表格使用 `.rescored.jsonl` 结果。
- 论文的 benchmark section、experiment section、结果说明和运行命令已经更新。
- 论文 qualitative analysis 已经压缩为主文版本，额外 light-guard / overhead / framework-boundary 内容已移动到 appendix section。
- `EXPERIMENT_RESULTS.md` 已经改成正式 expanded/cross-model 结果入口，旧 4-task pilot 已归档到 `PILOT_RESULTS.md`。
- semantic/schema poisoning 已扩展到 24 个任务、14 个 CSV、5 类 poisoner，并完成 `gpt-5.4-mini`、`claude-sonnet-4-6`、`Qwen3.6-35B-A3B-no-thinking` 三模型 practical-speed adapter 实验。
- `data2mcp_dataframe_guarded` 和 `data2mcp_dataframe_guarded_light` 已经完成 semantic/schema 与 numerical ablation。
- guarded overhead/case-study artifacts 和 bootstrap confidence intervals 已经生成。
- abstract / introduction / method / experiments 已经统一成 “ToxicTool-Bench 暴露 blind compliance + guarded verification 降低 BCR” 的论文主线。

## 已经完成的搭建内容

### Benchmark Core

目录：

```text
paper/iclr/toxictool_bench/
```

已完成：

- `DataToolEnv` clean/toxic 工具观测代理。
- paired clean/toxic runner。
- poisoning operators:
  - `aggregate_scale`
  - `sign_flip`
  - `rank_swap`
  - `label_swap`
  - `treatment_control_flip`
  - `column_semantic_swap`
  - `stale_metadata`
  - `biased_retrieval`
- evaluator metrics:
  - Clean TSR
  - Poisoned TSR
  - Delta TSR
  - BCR
  - ADR
  - VR
  - RR
- rescoring:
  - `rescore_results.py`
- result summarization:
  - `summarize_results.py`
- case-study extraction:
  - `extract_case_studies.py`
- guard ablation analysis:
  - `analyze_guard_ablation.py`
- bootstrap confidence intervals:
  - `bootstrap_ci.py`

### Task Suite

当前正式 expanded task file：

```text
paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl
```

规模：

- 34 tasks
- 11 CSV datasets

覆盖任务类型：

- mean / sum / count
- group ranking
- growth rate
- sign-sensitive calculation
- ratio / per-unit metric
- retention rate
- defect rate
- support queue statistics

当前 semantic/schema expansion：

```text
paper/iclr/toxictool_bench/tasks/semantic_schema.jsonl
```

规模：

- 24 tasks
- 14 CSV datasets

覆盖 poisoning 类型：

- treatment/control 或 label flip
- column semantic swap
- stale metadata / stale data dictionary
- biased retrieval evidence

### Full-Agent Adapters

已完成并可运行：

- `langgraph_react_full`
- `smolagents_toolcalling`
- `data2mcp_dataframe`
- `data2mcp_dataframe_guarded`
- `data2mcp_dataframe_guarded_light`
- `pandasai_dataframe`
- `da_agent_full`
- `autogen_tool_agent`

重要说明：

- `pandasai_dataframe` 是完整 PandasAI agent run，但 poisoning 发生在 chat-result boundary，不是内部 code-execution observation boundary。
- `da_agent_full` 已接入真实 DA-Agent action loop，但跨模型实验吞吐太慢；目前只纳入 `gpt-5.4-mini` 主表。
- OpenHands / de-agent 已经作为后续方向记录，但还没有完成 full adapter。

## 已完成的实验

### gpt-5.4-mini

完成范围：

- 34-task expanded suite
- 6 个 full adapters 全部完成

结果摘要：

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR |
| --- | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.41 | 0.59 | 0.68 |
| `smolagents_toolcalling` | 0.97 | 0.62 | 0.35 | 0.32 |
| `data2mcp_dataframe` | 0.65 | 0.47 | 0.18 | 0.24 |
| `pandasai_dataframe` | 1.00 | 0.47 | 0.53 | 0.65 |
| `da_agent_full` | 0.85 | 0.53 | 0.32 | 0.32 |
| `autogen_tool_agent` | 0.97 | 0.56 | 0.41 | 0.47 |

### claude-sonnet-4-6

完成范围：

- 34-task expanded suite
- 5 个非 DA-Agent full adapters

结果摘要：

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR |
| --- | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 0.88 | 0.76 | 0.12 | 0.18 |
| `smolagents_toolcalling` | 1.00 | 0.82 | 0.18 | 0.12 |
| `data2mcp_dataframe` | 0.85 | 0.62 | 0.24 | 0.24 |
| `pandasai_dataframe` | 0.97 | 0.32 | 0.65 | 0.76 |
| `autogen_tool_agent` | 0.91 | 0.82 | 0.09 | 0.24 |

未完成：

- `da_agent_full`

原因：

- Claude 上 DA-Agent 跑到 5/68 environment instances 后手动停止，速度不适合当前 cross-model batch。

### Qwen3.6-35B-A3B-no-thinking

完成范围：

- 34-task expanded suite
- 5 个非 DA-Agent full adapters

结果摘要：

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR |
| --- | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.44 | 0.56 | 0.59 |
| `smolagents_toolcalling` | 0.82 | 0.65 | 0.18 | 0.18 |
| `data2mcp_dataframe` | 0.32 | 0.24 | 0.09 | 0.06 |
| `pandasai_dataframe` | 1.00 | 0.26 | 0.74 | 0.76 |
| `autogen_tool_agent` | 0.94 | 0.76 | 0.18 | 0.29 |

运行说明：

- 第一次 Qwen 批量实验遇到 HTTP 429。
- 已在 `llm_client.py` 中加入 429/5xx retry + exponential backoff。
- 修复后非 DA-Agent batch 已完成。

## 当前主要结论

- 高 clean TSR 不代表抗毒化能力强；多个 agent 在 clean 接近满分时 toxic TSR 大幅下降。
- `rank_swap` 平均 BCR 最高，说明“排序/标签被替换”是最容易骗过 agent 的毒化方式。
- `aggregate_scale` 也有稳定破坏性，agent 经常直接复述被放大的数值。
- `sign_flip` 相对更容易被发现或恢复。
- PandasAI 在当前 coarse poisoning 设置下非常脆弱，三个模型上 BCR 都很高。
- data2mcp 的结果强依赖底层模型；Qwen 下 clean TSR 很低，说明目前 router/tool execution setup 还需要针对该模型调参。
- DA-Agent 在 GPT 上有更明显的 validation/recovery 行为，但跨模型吞吐是当前瓶颈。

## Semantic/Schema Cross-Model Results

完成范围：

- 24-task semantic/schema suite
- 5 个 practical-speed full adapters
- 3 个模型：`gpt-5.4-mini`、`claude-sonnet-4-6`、`Qwen3.6-35B-A3B-no-thinking`

结果入口：

```text
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_poison_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv
```

摘要：

| Model | Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR |
| --- | --- | ---: | ---: | ---: | ---: |
| GPT | `langgraph_react_full` | 1.00 | 0.79 | 0.21 | 0.21 |
| GPT | `smolagents_toolcalling` | 1.00 | 0.46 | 0.54 | 0.50 |
| GPT | `data2mcp_dataframe` | 0.92 | 0.29 | 0.62 | 0.62 |
| GPT | `pandasai_dataframe` | 1.00 | 0.25 | 0.75 | 0.75 |
| GPT | `autogen_tool_agent` | 1.00 | 0.71 | 0.29 | 0.21 |
| Claude | `langgraph_react_full` | 1.00 | 0.96 | 0.04 | 0.00 |
| Claude | `smolagents_toolcalling` | 1.00 | 0.71 | 0.29 | 0.25 |
| Claude | `data2mcp_dataframe` | 1.00 | 0.46 | 0.54 | 0.54 |
| Claude | `pandasai_dataframe` | 1.00 | 0.29 | 0.71 | 0.75 |
| Claude | `autogen_tool_agent` | 1.00 | 0.96 | 0.04 | 0.38 |
| Qwen | `langgraph_react_full` | 1.00 | 0.79 | 0.21 | 0.21 |
| Qwen | `smolagents_toolcalling` | 1.00 | 0.46 | 0.54 | 0.38 |
| Qwen | `data2mcp_dataframe` | 0.54 | 0.33 | 0.21 | 0.04 |
| Qwen | `pandasai_dataframe` | 0.83 | 0.21 | 0.62 | 0.67 |
| Qwen | `autogen_tool_agent` | 1.00 | 0.75 | 0.25 | 0.25 |

## 已生成的文档和产物

核心结果：

```text
paper/iclr/EXPERIMENT_RESULTS.md
paper/iclr/PILOT_RESULTS.md
paper/iclr/NEXT_EXPERIMENT_PLAN.md
paper/iclr/toxictool_bench/results/cross_model_summary.csv
paper/iclr/toxictool_bench/results/poison_type_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_poison_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_poison_summary.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_semantic_ablation_summary.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_numerical_ablation_summary.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_overhead_summary.csv
paper/iclr/toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_bootstrap_ci.csv
```

论文 section：

```text
paper/iclr/sections/03_toxictool_bench.tex
paper/iclr/sections/04_method_ibf.tex
paper/iclr/sections/05_experiments.tex
paper/iclr/sections/06_qualitative_analysis.tex
paper/iclr/sections/07_discussion_limitations.tex
paper/iclr/sections/08_appendix_guard_details.tex
```

运行说明：

```text
paper/iclr/RUN_COMMANDS.md
```

当前状态：

```text
paper/iclr/CURRENT_STATUS.md
paper/iclr/PROGRESS_REPORT.md
```

Case studies：

```text
paper/iclr/CASE_STUDIES.md
paper/iclr/GUARDED_CASE_STUDIES.md
paper/iclr/toxictool_bench/extract_case_studies.py
paper/iclr/toxictool_bench/analyze_guard_ablation.py
paper/iclr/sections/06_qualitative_analysis.tex
```

## 验证状态

已运行：

```bash
python3 -m pytest paper/iclr/toxictool_bench/tests -q
python3 -m compileall -q paper/iclr/toxictool_bench
```

结果：

```text
12 passed
compileall passed
```

## 还缺少什么

### 论文实验层面

- 已经把 `CASE_STUDIES.md` 中的代表性样例整理为 `sections/06_qualitative_analysis.tex` 初稿。
- 已经把旧 pilot 结果从 `EXPERIMENT_RESULTS.md` 拆出到 `PILOT_RESULTS.md`。
- 已经把 semantic/schema 跨模型结果和 guarded `data2mcp` ablation 写入 `EXPERIMENT_RESULTS.md` 和 `sections/05_experiments.tex`。
- 已经实现 `data2mcp_dataframe_guarded`，并完成 `gpt-5.4-mini` semantic/schema 24-task ablation：BCR 0.62 -> 0.00，poisoned TSR 0.29 -> 0.83，clean TSR 0.92 -> 0.83。
- 已经完成 `gpt-5.4-mini` numerical 34-task guarded ablation：BCR 0.24 -> 0.00，clean TSR 0.65 -> 0.79，poisoned TSR 0.47 -> 0.74。
- 已经实现并跑完整 `data2mcp_dataframe_guarded_light`：
  - semantic/schema: clean 0.83, toxic 0.71, BCR 0.00, RR 0.71
  - numerical: clean 0.68, toxic 0.65, BCR 0.00, RR 0.65
- 已经生成 guarded overhead 统计和 case studies：
  - `paper/iclr/toxictool_bench/results/data2mcp_guarded_overhead_summary.csv`
  - `paper/iclr/GUARDED_CASE_STUDIES.md`
- 已经生成 bootstrap CI：
  - `paper/iclr/toxictool_bench/results/numerical_gpt_bootstrap_ci.csv`
  - `paper/iclr/toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv`
  - `paper/iclr/toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv`
  - `paper/iclr/toxictool_bench/results/data2mcp_guarded_bootstrap_ci.csv`
- qualitative examples 已经压缩为主文版本，light-guard failure、overhead 和 framework-boundary 细节已放入 `sections/08_appendix_guard_details.tex`。
- DA-Agent 当前策略：保留 GPT 主表，跨模型遗漏作为 throughput limitation 报告。
- bootstrap CI 已完成；只有在最终关键 claim 的 CI 仍显得过宽时，才需要 optional rerun。
- stronger ablation 已完成第一轮：
  - full guard: 主 defense result
  - light guard: appendix/tradeoff result
  - overhead summary: `data2mcp_guarded_overhead_summary.csv`
- 仍可作为后续扩展的 ablation：
  - poison severity
  - poison once vs repeated poison
  - selective guard activation

### Benchmark 层面

- 当前 34-task numerical + 24-task semantic/schema 已搭建，并完成 cross-model / guarded ablation / CI。正式投稿若时间允许，可继续扩展到 60-100 tasks。
- semantic/schema poisoning 第一版已完成：
  - column semantic swap
  - treatment/control flip
  - stale metadata
  - biased retrieval evidence
- 需要新增 instruction-poisoned data tasks：
  - metadata instruction
  - row-level instruction
  - retrieved chunk instruction

### Adapter 层面

- OpenHands full adapter 还没有完成；当前建议作为 future work，不阻塞主表。
- PandasAI poisoning boundary 需要更细，最好能拦截内部 code execution result。
- data2mcp + Qwen 的 max-turn / tool-use 行为需要单独 debug，否则会压低 clean TSR 并影响横向比较。
- DA-Agent 的 cross-model throughput 需要优化，或者作为明确 limitation 处理。

## 建议的下一步

当前下一步是 **submission package 前的全文一致性检查**，不是继续跑主实验。

具体顺序：

1. 检查 `main.tex` 或最终论文入口是否按正确顺序 include：
   - `00_abstract.tex`
   - `01_introduction.tex`
   - `02_problem_setup.tex`
   - `03_toxictool_bench.tex`
   - `04_method_ibf.tex`
   - `05_experiments.tex`
   - `06_qualitative_analysis.tex`
   - `06_related_work.tex`
   - `07_discussion_limitations.tex`
   - appendix 中 include `08_appendix_guard_details.tex`
2. 检查符号一致性：
   - `\benchmarkname{}`
   - `\methodname{}`
   - TSR / BCR / ADR / VR / RR
3. 检查表格引用和 artifact 对应关系：
   - numerical cross-model
   - semantic/schema cross-model
   - guarded full ablation
   - light guard appendix
   - bootstrap CI appendix
4. 检查是否需要 optional rerun：
   - 只在某个关键 claim 的 bootstrap CI 太宽时才补跑。
5. 准备最终 ICLR submission package：
   - 主 tex
   - sections
   - appendix
   - result artifact list
   - reproducibility commands

优先顺序：

1. 全文一致性检查。
2. 主文篇幅压缩。
3. appendix include / artifact list。
4. optional rerun 判断。
5. submission package 打包。
