# arXiv-specific source files

`authors.tex` is the version-controlled preprint author block. The anonymous ICLR entry point `paper/main.tex` does not load it.

For the standalone arXiv/Overleaf project, replace its `authors.tex` with this file and keep `\input{authors}` in the preamble. Both notes are generated automatically by:

```tex
\maketitle
```

- Zifu Tao: Tongji University; zifutao@nyu.edu.
- Changqing Yin: Tongji University; yinchangqing@tongji.edu.cn.
- First title footnote (`*`), attached to Zifu Tao: “This work was initiated while Zifu Tao was an undergraduate student at Tongji University.”
- Second title footnote (dagger), attached to Changqing Yin: Corresponding author.

The old `\researchoriginfootnote` call can be removed from `main.tex`. It remains defined as an empty compatibility command, so older Overleaf main files still compile without duplicating the note.

The local export at `paper/exports/ARXIV_OVERLEAF_20260925/` is updated separately. Export PDFs and ZIPs remain Git-ignored; this small author source is tracked so the affiliation change is available on GitHub.

## Figure 2

`figures/figure2_vector.pdf` and its editable SVG are the lightly polished September 26 version, incorporated into the arXiv export on September 29. The original layout and text are preserved; colors are slightly softened and the second-row arrows, captions, and icons are aligned. This is not the rejected full redesign.

For Overleaf, replace `figures/figure2_vector.pdf` with this file. Its filename and dimensions are unchanged, so no LaTeX edits are needed. The anonymous manuscript continues to use the original `paper/figures/figure2_vector.pdf`.

The rendering script is `toxictool_bench/preview_figure2_polish.py`; it writes candidates under `paper/previews/figure2_polish_20260926/`. Promoting a candidate into this directory and the standalone export is a separate step.
