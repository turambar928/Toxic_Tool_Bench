# arXiv author information

`authors.tex` is the version-controlled preprint author block. The anonymous ICLR entry point `paper/main.tex` does not load it.

For the standalone arXiv/Overleaf project, replace its `authors.tex` with this file, keep `\input{authors}` in the preamble, and put the research-origin note immediately after the title:

```tex
\maketitle
\researchoriginfootnote
```

- Zifu Tao: Tongji University; zifutao@nyu.edu.
- Changqing Yin: Tongji University; yinchangqing@tongji.edu.cn.
- First title footnote (`*`): Corresponding author, attached to Changqing Yin.
- Second title footnote (dagger): “This work was initiated while Zifu Tao was an undergraduate student at Tongji University.”

The local export at `paper/exports/ARXIV_OVERLEAF_20260925/` is updated separately. Export PDFs and ZIPs remain Git-ignored; this small author source is tracked so the affiliation change is available on GitHub.
