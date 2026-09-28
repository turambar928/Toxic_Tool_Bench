# 表格天蓝色数字高亮

## 样式与 Overleaf 同步

只给数字加浅天蓝底（RGB 184,225,250），保留原有字色和正常字重、不加粗，不铺满单元格，不改变模板。
`main.tex` 定义 `\best{...}`，例如 `\best{0.99}`。此命令只负责样式；高亮对象由明确的比较规则决定。

本次 Overleaf 需要同步以下五个文件，缺少主文件中的宏会导致 undefined control sequence：

- `main.tex`（也可以只复制新增的 `xcolor`、颜色和 `\best` 宏定义，保留自己的其他设置）
- `sections/05_experiments.tex`
- `sections/08_appendix_guard_details.tex`
- `sections/09_revision_validation.tex`
- `figures/cross_model_rates_table.tex`

不需要替换图片 PDF、模板或实验数据。旧 Overleaf 打包副本不再维护。

## 选择规则

当前九张对比表使用高亮：

| 表格标签 | 比较范围 | 高亮方向 |
|---|---|---|
| `tab:gpt-expanded-cross-agent-120` | 三个 adapter | TSR/RR 最大，下降量/BCR 最小 |
| `tab:cross-agent-model-full` | 每个模型内，数值与语义列分别比较 | TSR 最大，BCR 最小 |
| `tab:appendix-stronger-baselines` | 每个任务子集内 | TSR/RR 最大，BCR 最小 |
| `tab:appendix-guard-suite-breakdown` | 每个任务族内 | TSR/RR 最大，BCR 最小 |
| `tab:appendix-multiroute-stress` | 每个任务族内 | TSR/RR 最大，BCR/PAR/VPA 最小 |
| `tab:cross-model-rates` | 每个任务族内比较模型均值 | TSR 最大，BCR 最小 |
| `tab:appendix-latency-distribution` | 每个任务族内 | 时间和工具事件数最小；不是综合质量排名 |
| `tab:holdout-methods` | 每个设置、每种评分来源内 | TSR 最大 |
| `tab:holdout-scorer` | 每一行，同一指标的旧版/修订版之间 | Precision 分别比 Precision，Recall 分别比 Recall |

并列值按表格显示精度同时标记，不暗示未四舍五入的结果完全相等，也不表示统计显著性。
暴露条件下的 BCR/RR 等仍使用各自的暴露分母，高亮不把它们变成共同暴露集上的严格排名。
VR/PDR、样本量、置信区间、任务清单、审计标签分布、描述性的算子/证据条件统计不做最优值高亮。
评分器修订影响表保留前后箭头作为主要视觉线索，不用高亮暗示修改评分器导致了 agent 能力提升。

## 再生成与检查

主结果、defense 表和跨模型汇总表的生成入口已接入相同格式化函数。
只需重新应用样式时，不要重评分或重跑 agent：

```bash
python3 toxictool_bench/paper_table_highlights.py
python3 toxictool_bench/paper_table_highlights.py --check
python3 toxictool_bench/check_paper_static.py
```

格式化只添加或更新 `\best{}`，不修改数值、行序或原始实验产物；重复运行结果相同。
