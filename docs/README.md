# 项目文档导航

整理日期：2026-09-28。论文相关文件集中在 `paper/`，根目录不再保留论文主文件或 Bib 文件；实验代码、数据和冻结人工材料保持原位置。

## 从哪里开始

- [项目概览](../README.md)
- [实验状态（最后实验更新：2026-09-21）](experiments/CURRENT_STATUS.md)
- [已完成的人工评估报告](../output/human_validation_20260920/README_CN.md)
- [逐任务可执行验收结果](../output/task_acceptance_v1/README_CN.md)
- [论文目录与编译说明](../paper/README.md)
- [参考文献核查清单](../paper/docs/REFERENCE_LINKS_CN.md)
- [运行命令](reproducibility/RUN_COMMANDS.md)

本文档下的代码块、命令和反引号中的项目路径，除非另有说明，均以仓库根目录为起点；可点击链接则按各 Markdown 文件位置解析。

## 文档分类与原文件去向

文档名保持不变，以下按目录列出。历史文档中的“当前”“待完成”等用语反映原记录日期，不是今天的状态；不把旧计划和旧结果包装成最新实验结论。

### 复现与运行

- [ARTIFACT_MANIFEST.md](reproducibility/ARTIFACT_MANIFEST.md)
- [REPRODUCIBILITY.md](reproducibility/REPRODUCIBILITY.md)
- [RUN_COMMANDS.md](reproducibility/RUN_COMMANDS.md)

### 实验与修订

- [CURRENT_STATUS.md](experiments/CURRENT_STATUS.md)
- [EVIDENCE_CONTROLS_V4_CN.md](experiments/EVIDENCE_CONTROLS_V4_CN.md)
- [SCORER_REPAIR_EXECUTION_CN.md](experiments/SCORER_REPAIR_EXECUTION_CN.md)
- [SCORER_REPAIR_PLAN_CN.md](experiments/SCORER_REPAIR_PLAN_CN.md)
- [SUBMISSION_REVISION_V3_CN.md](experiments/SUBMISSION_REVISION_V3_CN.md)
- [TASK_CONSTRUCTION_AUDIT_CN.md](experiments/TASK_CONSTRUCTION_AUDIT_CN.md)

### 人工评估

- [HUMAN_VALIDATION_HANDOFF_CN.md](human_evaluation/HUMAN_VALIDATION_HANDOFF_CN.md)

### 论文与投稿

- [REFERENCE_LINKS_CN.md](../paper/docs/REFERENCE_LINKS_CN.md)
- [SUBMISSION_CHECKLIST.md](../paper/docs/SUBMISSION_CHECKLIST.md)
- [PAPER_BUILD_CHECK.md](../paper/docs/PAPER_BUILD_CHECK.md)
- [PAPER_CONSISTENCY_CHECK.md](../paper/docs/PAPER_CONSISTENCY_CHECK.md)
- [APPENDIX_REORGANIZATION_CN.md](../paper/docs/APPENDIX_REORGANIZATION_CN.md)（原位于 `docs/APPENDIX_REORGANIZATION_CN.md`）

### 历史记录

- [CASE_STUDIES.md](archive/CASE_STUDIES.md)
- [GUARDED_CASE_STUDIES.md](archive/GUARDED_CASE_STUDIES.md)
- [EXPERIMENT_RESULTS.md](archive/EXPERIMENT_RESULTS.md)
- [FULL_EXPERIMENT_ROADMAP.md](archive/FULL_EXPERIMENT_ROADMAP.md)
- [NEXT_EXPERIMENT_PLAN.md](archive/NEXT_EXPERIMENT_PLAN.md)
- [PILOT_RESULTS.md](archive/PILOT_RESULTS.md)
- [PROGRESS_REPORT.md](archive/PROGRESS_REPORT.md)
- [ICLR2027_SMOKE_RESULTS.md](archive/ICLR2027_SMOKE_RESULTS.md)

## 其他材料的边界

- `paper/archive/appendix_archive_20260918/`：旧附录源稿，内容未改，不参与当前编译。
- `docs/HUMAN_ANNOTATION_SOURCE_20260920.json`：人工材料来源记录，未改动。
- `paper/archive/template_copies/`：原根目录的两份模板副本；当前编译使用 `paper/iclr2027/` 中的官方文件。
- `output/` 与 `toxictool_bench/` 下的冻结任务、人工标注和轨迹均保持原位置、原内容。历史轨迹中出现旧文档路径属于原始证据，不追改。
- `paper/exports/ARXIV_OVERLEAF_20260925/`：本地独立 arXiv 编译包；已填写作者，保持预印本设置，不覆盖匿名主稿。该生成快照及 ZIP 不提交 Git。
- `paper/previews/figure2_redesign_20260926/` 和 `paper/previews/figure2_polish_20260926/`：本地候选图预览，尚未替换正文；对应生成脚本位于 `toxictool_bench/preview_figure2_*.py`。
- `paper/archive/local_build_archive_20260928/`：旧编译中间文件和 `pandasai.log`，仅本地保留，不删除、不提交 Git。

## 编译与检查

在仓库根目录执行：

```bash
python3 toxictool_bench/check_paper_static.py --main paper/main.tex
python3 -m pytest toxictool_bench/tests -q
cd paper
mkdir -p build
tectonic -Z search-path=iclr2027 main.tex --outdir build --keep-logs --keep-intermediates
```

打开 `paper/build/main.pdf` 查看该次构建结果。`paper/main.pdf` 保留为单独更新的本地预览；整篇论文的编译 PDF 和导出 ZIP 不提交 Git，`paper/figures/` 中排版所需的 PDF 图片继续跟踪。`api` 与环境变量配置继续被忽略，不在本次归档或提交范围内。论文依赖三个 `output/` 中的实验表格，详见 [论文编译说明](../paper/README.md)。
