# Paper Build Check

Last checked: 2026-07-23 Asia/Shanghai.

Commands:

```bash
python3 -m pytest toxictool_bench/tests -q
python3 -m compileall -q toxictool_bench
python3 toxictool_bench/check_paper_static.py --main main.tex
/tmp/tectonic-musl/tectonic --outdir /tmp/toxicbench_pdf_build main.tex
pdfinfo /tmp/toxicbench_pdf_build/main.pdf
pdftotext /tmp/toxicbench_pdf_build/main.pdf /tmp/toxicbench_pdf_build/main.txt
```

Results:

- Unit tests: 23 passed.
- Python compile check: passed.
- Static paper check: passed; 11 TeX files, 22 labels, 15 refs, 27 citations, 27 BibTeX keys.
- PDF compile: passed with Tectonic 0.16.9.
- Output PDF: `/tmp/toxicbench_pdf_build/main.pdf`.
- PDF pages: 22.
- Remaining TeX warning: one minor overfull hbox in the appendix artifact list, 4.98 pt too wide. No missing citation, missing reference, or missing input errors were reported.

