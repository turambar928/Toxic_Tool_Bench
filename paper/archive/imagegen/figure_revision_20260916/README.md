# Revised Figure 1 and Figure 2

Final outputs:

- `figures/figure1_revised.png` — 6336 × 2688 pixels.
- `figures/figure2_revised.png` — 5504 × 3072 pixels.

Original `figures/figure1.png` and `figures/figure2.png` are preserved. The paper
now references the revised siblings. No numerical result plots were changed.

The built-in image-generation service was attempted first; Figure 1 had minor
text defects and subsequent edits repeatedly failed with network errors. The
user explicitly authorized local programmatic edits. Both final images were
therefore produced deterministically with Pillow from the original PNGs, using
`edit_original_figures.py`; they are not the generated draft. `prompts.md`
records the initial requested changes and generation prompts for provenance.

Figure 1 keeps the original source table, agent illustration and clean/poison
branch layout. It locates poisoning at the returned observation and removes
claims that tool logic is replaced or errors are undetectable.

Figure 2 retains the four-section layout and color roles. It distinguishes
task suites, adds PAR/VPA and the completed human audit, and shows the four
verification protocols as parallel comparisons. Unsupported mitigation and
independent-source claims are removed.

Rebuild from the repository root (Pillow and macOS Arial fonts required):

```sh
python3 output/imagegen/figure_revision_20260916/edit_original_figures.py
```

## Figure 2 correction: preserve the original four-step artwork

The user rejected the first revision because it changed too much of the
original layout. The current paper references `figures/figure2_revised_v2.png`
(5504 × 3072), edited directly from the original `figures/figure2.png`.
It preserves the task/operator illustrations, six metric cards, and the
four-step Generic Guard sequence. Only local text regions and inaccurate
status labels are replaced. The previous Figure 2 remains for provenance and
is no longer referenced by the paper. Figure 1 is unchanged by this correction.

Rebuild the current Figure 2 alone:

```sh
python3 output/imagegen/figure_revision_20260916/edit_figure2_minimal.py
```
