# arXiv author information

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
