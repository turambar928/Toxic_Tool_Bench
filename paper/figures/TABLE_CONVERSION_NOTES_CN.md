# 表格转图集成与手动同步说明

已集成确认的第六版设计，并完成 9 月 22 日的标签排版调整。原 Table 3 对应 Figure 4（正文第 8 页）；原 Table 9 对应 Figure 5（附录第 16 页）；原 Table 26 的汇总对照对应 Figure 8（附录第 26 页）。页码对应当前编译，图号由 LaTeX 自动更新。

## Overleaf 本次只需同步这六个文件

替换章节文件：

- `sections/05_experiments.tex`
- `sections/09_revision_validation.tex`
- `sections/11_matched_evidence_controls.tex`

上传新增 PDF 到 `figures/`：

- `figures/fig_defense_comparison.pdf`
- `figures/fig_human_method_comparison.pdf`
- `figures/fig_evidence_control.pdf`

本次无需更改 `main.tex`、模板或参考文献。原 `output/evidence_controls_v4/results.tex` 仍保留，不要删除：汇总热力图未包含逐数据集和首轮计数，因此继续保留该明细表。旧 Overleaf 文件夹和 ZIP 不再更新。

此前的 Future Work 与 AI 声明分别在 `sections/07_discussion_limitations.tex`、`sections/12_ai_use_statement.tex`；如尚未同步，可单独同步，注意保留作者在 Overleaf 的后续编辑。

## 排版与信息保留

三张图保持已确认的布局和配色。为适应正文宽度，正式 PDF 放大了字体，把重复说明放入图注；Figure 4 的小概率数值标注已恢复正向横排，通过中间面板宽度和柱间距调整避免挤压。`Verify-only` 为 Verification-only 的图内缩写。所有 28 个率与 4 个暴露数量均保留，零值明确显示。

原算子热力图缩为正文宽度的 88%，图注略作压缩，数值及统计口径不变。正文含 Conclusion/Future Work/Limitations 仍在第 9 页结束；全文 27 页。正文格式仍由官方 ICLR 2027 模板控制，未修改样式参数。

静态引用检查通过；三张 PDF 均为矢量内容，嵌入 Times New Roman。主编译与 `output/scorer_revision_v2/pdf/` 的编译产物均已更新。

## 维护与复现（无需上传 Overleaf）

- `defense_comparison_data.tex`：保留原 Table 3 的精确显示值，作为图的数值源，不参与论文编译。
- `table_conversion_data.json`：三图数据及源文件哈希。
- `fig_*.svg`：相应矢量编辑源文件。
- `toxictool_bench/plot_table_conversion_previews.py --paper`：导出正式三图。无参数时生成预览。
- `toxictool_bench/sync_defense_paper.py`：已将原主表的同步目标改为独立数据源；之后用上述 `--paper` 命令更新图片。
- `toxictool_bench/tests/test_table_conversion_figures.py`：验证完整数值、暴露分母、24 个自动/人工计数及图表集成。

未调用任何模型 API，未修改评分器、原始轨迹或人工标签。
