# 论文文件

这里是论文的唯一源稿入口。仓库根目录不再保留 `main.tex`、Bib 文件、章节、图片或模板副本。本次仅整理路径，没有修改论文内容、数据或图形设计。

## 目录

- `main.tex`、`references.bib`：当前匿名 ICLR 主稿与参考文献。
- `sections/`、`figures/`：章节与正文采用的图片；图像原件和矢量版均保留。
- `iclr2027/`：当前使用的官方模板，模板文件内容未改。
- `docs/`：参考文献核查、投稿检查和排版记录；旧记录中的结论对应其记录日期。
- `archive/`：旧附录、模板副本、历史修订与参考文献审计，以及旧 PDF，不参与当前编译。
- `build/`、`main.pdf`：本地编译产物与更新后的预览，不提交 Git。
- `exports/`：本地独立 Overleaf/arXiv 编译包及补充材料发布包，不提交 Git。
- `previews/`：本地候选图预览，不提交 Git，不代表已替换正文。

原 `docs/paper/` 已移至 `paper/docs/`。原 `output/paper_revision/`、`output/reference_audit_20260922/` 和 `output/pdf/` 已移至 `paper/archive/`；旧记录保留当时的内容与路径描述。

旧绘图记录 `output/imagegen/` 和转换脚本 `tmp/pdfs/` 分别归入 `paper/archive/imagegen/` 与 `paper/archive/flowchart_scripts/`。这些历史脚本未重新生成图片。

## 本地编译

从仓库根目录执行：

```bash
python3 toxictool_bench/check_paper_static.py --main paper/main.tex
cd paper
mkdir -p build
tectonic -Z search-path=iclr2027 main.tex --outdir build --keep-logs --keep-intermediates
```

本次构建结果为仓库中的 `paper/build/main.pdf`。如需同步预览，在 `paper/` 内执行 `cp build/main.pdf main.pdf`。使用传统 TeX 工具链时，也在 `paper/` 内执行 `TEXINPUTS=./iclr2027//: latexmk -pdf main.tex`。

论文直接读取以下三个实验生成的 TeX 表格，保持单一数据来源；它们仍在仓库的 `output/` 中，章节通过 `../output/` 引入：

- `output/human_validation_20260920/scorer_metrics.tex`
- `output/submission_revision_v3/fresh_results.tex`
- `output/evidence_controls_v4/results.tex`

因此，单独下载此文件夹并不等于自包含 Overleaf 包。需要独立上传时使用已有导出包；或者一并带上上述三个文件并调整输入路径。实验代码、原始数据和人工标注未移动。

## arXiv 与候选图

已填写作者的独立 arXiv 包现位于 `paper/exports/ARXIV_OVERLEAF_20260925/`，同名 ZIP 也保留在 `paper/exports/`。它内部仍以 `main.tex` 编译，保留作者、Preprint 页眉及预印本设置，不覆盖匿名主稿。导出快照不会随主稿自动更新。

arXiv 作者信息的 Git 跟踪源文件为 [arxiv/authors.tex](arxiv/authors.tex)，Overleaf 修改方式见 [arxiv/README.md](arxiv/README.md)。2026-09-29 更新：两位作者单位均为 Tongji University；第一条星号脚注说明研究始于一作的同济本科期间，第二条剑号脚注标注导师为通讯作者。

最近的 Figure 2 微调候选在 `paper/previews/figure2_polish_20260926/`，生成脚本仍是 `toxictool_bench/preview_figure2_polish.py`；此次没有将它替换进正文。

代码、实验与复现入口见 [项目说明](../README.md) 和 [文档导航](../docs/README.md)。
