# 附录整理说明（2026-09-18）

这次只整理论文及其表格同步逻辑，没有重跑模型、修改评分器、覆盖人工标签或改变实验结论。使用官方 ICLR 2027 模板，保持字号、页边距和正文不变。

## 阅读结构

论文由 32 页缩至 25 页；正文仍为第 1–9 页，参考文献为第 10–13 页，附录为第 14–25 页（19 页减为 12 页）。附录从 9 个一级章节改为 5 个，保留 6 个二级小节，取消所有段落级小标题。

| 新附录 | 内容 | 源文件 |
| --- | --- | --- |
| A | Benchmark 构造、威胁模型、独立性的边界、相关工作对照 | `sections/08_appendix_guard_details.tex` |
| B | 指标判定、120/240 条人工审计、评分器修复、reference 修订、待完成人工验证 | `sections/09_revision_validation.tex` |
| C | Agent 协议、框架注入边界、多表执行和备选验证策略 | `sections/08_appendix_guard_details.tex` |
| D | 分任务族结果、暴露分母、算子/跨模型结果、配对区间、成本、重复投毒 | `sections/08_appendix_guard_details.tex` |
| E | 历史 delivery 审计、修复后的 scalar 对照、field-bound/common-parent 实验 | `sections/10_delivery_controls.tex`、`sections/11_matched_evidence_controls.tex` |

`main.tex` 仅引入 08 文件，再由其按阅读顺序引入 B 和 E，避免重复编译。同一张合并表保留原 label 别名，正文引用仍然有效。

## 合并和移出的内容

- 旧版/修复版 scorer 的 240 条人工对照合为一表；保留样本数、阳性数、precision/recall，以及“修复开发集而非独立验证”的限制。F1 的完整原值仍保存在原分析与旧附录快照。
- 120 条开发审计的 scorer 指标和标注者一致性合为一表，明确两者含义不同，不隐藏 BCR/ADR 低召回。
- 防御分任务族结果和 exposure 表合并，保留暴露分子/分母、PDR、BCR、VR、RR；非零 BCR 事件数在 caption 中明确列出。
- 重复的成本概览、边际区间表、框架覆盖表、多表任务清单移出 PDF；必要结论、精确事件上界解释、框架排除原因及任务族仍保留在正文段落。完整旧表见快照，机器可读数据没有删除。
- 重复展示正文数值的 expanded-GPT capability-gap 图和 defense-frontier 图移出 PDF，原图文件仍保留。正文算子图、跨模型图、重复投毒曲线均保留。
- 运行命令和长文件清单由仓库文档承载，不再占用论文篇幅。

本次保留了所有关键不利结果：历史 scorer 漏判、Guard 没有稳健优势、旧 sign-flip 投毒问题、部分投毒残留正确值、公共数据执行检查的局限、新受控实验的推广边界，以及尚未完成的独立人工验证。

## 完整材料入口

- [旧附录完整 TeX 快照](appendix_archive_20260918/)：四个文件逐字保留整理前版本；不参与当前论文编译，不作为当前结果的另一套来源，也不由同步脚本更新。
- [运行命令](../RUN_COMMANDS.md)：已有实验、重复投毒及防御结果重建入口。复制运行模型命令会产生 API 请求，不是本次排版整理所必需。
- `toxictool_bench/results/`：`public_cross_model_*`、`public_poison_type_summary.csv`、`iclr2027_gpt_expanded_cross_agent_*`、`leakage_free_defense_*`、`verification_stress_*`、`langgraph_multitable_extension_summary.csv`。
- `toxictool_bench/human_audit_v2/`、`human_review_v3/`、`human_holdout_v1/`：原始人工材料与分析，未修改。
- `output/scorer_revision_v2/`：冻结版本、三版本重评分、reference 审计、claim span 和 provenance。
- `output/submission_revision_v3/`、`output/evidence_controls_v4/`：新实验的冻结协议、执行记录、结果、amendments 和审计。
- [CASE_STUDIES.md](../CASE_STUDIES.md)、[GUARDED_CASE_STUDIES.md](../GUARDED_CASE_STUDIES.md)：完整案例。

`sync_defense_paper.py` 已适配合并后的表格和新的 scorer 源文件位置。完整边际区间仍输出 CSV；下次执行该脚本还会输出 `leakage_free_defense_paper_intervals.csv`，区分零 BCR 的单侧 exact 上界与普通 bootstrap 区间。本次未重跑完整重评分流水线。

## 离线检查与官方模板编译

在仓库根目录执行：

```bash
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
tectonic -Z search-path=iclr2027 main.tex --keep-logs --keep-intermediates
tectonic -Z search-path=iclr2027 main.tex --outdir output/scorer_revision_v2/pdf --keep-logs --keep-intermediates
```

保留官方模板的字体、匿名审稿页眉和行号。编译器已有 bibliography 重复遍历警告需要与真正的 undefined reference 区分；交付前检查最终 PDF 页数、引用及表格分页。
