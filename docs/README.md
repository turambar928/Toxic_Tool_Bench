# 项目文档导航

整理日期：2026-09-28。根目录只保留项目入口 `README.md` 与数据许可证 `DATA_LICENSE.md`；论文、代码、数据和冻结人工材料仍在原位置。

## 从哪里开始

- [项目概览](../README.md)
- [实验状态（最后实验更新：2026-09-21）](experiments/CURRENT_STATUS.md)
- [已完成的人工评估报告](../output/human_validation_20260920/README_CN.md)
- [逐任务可执行验收结果](../output/task_acceptance_v1/README_CN.md)
- [参考文献核查清单](paper/REFERENCE_LINKS_CN.md)
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

- [REFERENCE_LINKS_CN.md](paper/REFERENCE_LINKS_CN.md)
- [SUBMISSION_CHECKLIST.md](paper/SUBMISSION_CHECKLIST.md)
- [PAPER_BUILD_CHECK.md](paper/PAPER_BUILD_CHECK.md)
- [PAPER_CONSISTENCY_CHECK.md](paper/PAPER_CONSISTENCY_CHECK.md)
- [APPENDIX_REORGANIZATION_CN.md](paper/APPENDIX_REORGANIZATION_CN.md)（原位于 `docs/APPENDIX_REORGANIZATION_CN.md`）

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

- `docs/appendix_archive_20260918/`：旧附录源稿，未改动，不参与当前编译。
- `docs/HUMAN_ANNOTATION_SOURCE_20260920.json`：人工材料来源记录，未改动。
- `docs/archive/template_copies/`：原根目录的两份模板副本；当前编译使用 `iclr2027/` 中的官方文件。
- `output/` 与 `toxictool_bench/` 下的冻结任务、人工标注和轨迹均保持原位置、原内容。历史轨迹中出现旧文档路径属于原始证据，不追改。
- `output/ARXIV_OVERLEAF_20260925/`：本地独立 arXiv 编译包；已填写作者，保持预印本设置，不覆盖匿名主稿。该生成快照及 ZIP 不提交 Git。
- `output/figure2_redesign_20260926/` 和 `output/figure2_polish_20260926/`：本地候选图预览，尚未替换正文；对应生成脚本位于 `toxictool_bench/preview_figure2_*.py`。
- `output/local_build_archive_20260928/`：从根目录移入的旧编译中间文件和 `pandasai.log`，仅本地保留，不删除、不提交 Git。

## 编译与检查

在仓库根目录执行：

```bash
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
mkdir -p output/paper_build
tectonic -Z search-path=iclr2027 main.tex --outdir output/paper_build --keep-logs --keep-intermediates
```

打开 `output/paper_build/main.pdf` 查看该次构建结果。根目录 `main.pdf` 保留为单独更新的本地预览；整篇论文的编译 PDF 和导出 ZIP 不提交 Git，`figures/` 中排版所需的 PDF 图片继续跟踪。`api` 与环境变量配置继续被忽略，不在本次归档或提交范围内。
