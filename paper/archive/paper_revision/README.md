# ToxicBench text and reference revision

The current source restores task construction, verification protocols, and result interpretation; reduces repeated disclaimers; simplifies prose; and corrects the bibliography. Experimental table values and the scorer were not changed in this editing pass.

- `FIGURE_REVISION_GUIDE.md`: concrete Figure 1 and Figure 2 editing instructions, English labels, and captions.
- `reference_audit.md`: source links and findings for all 42 references.
- `reference_changes.json`: corrected reference fields.
- `revision_checks.json`: validation results and source hashes.
- `../pdf/toxicbench_text_revision_preview.pdf`: compiled preview. Figures 1 and 2 retain their old artwork pending the author's edits.

The repository now includes the official ICLR 2027 style and bibliography files from https://github.com/ICLR/Master-Template/tree/master/iclr2027. The abstract is enclosed in the template's abstract environment. References start on a new page. Font sizes and page margins follow the template. Explicit T1 font encoding keeps the Times family active in both the local XeTeX-based build and pdfLaTeX.

Compile `main.tex` using the included style files. This preview was built with Tectonic 0.17.0. Replacing Figure 1 or 2 can change pagination; preserve their aspect ratios and LaTeX display widths, then compile again.
