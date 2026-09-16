# Public-data transfer fixture

This file is the unmodified `penguins.csv` from **palmerpenguins** by Allison
Horst, Alison Hill, and Kristen Gorman. Observations were collected by Kristen
Gorman and the Palmer Station Long Term Ecological Research program.

- Source: https://github.com/allisonhorst/palmerpenguins
- Source revision observed on retrieval: `8957207b78d6ccd1b4654a9dd9c9041b657478ab`
- File: `inst/extdata/penguins.csv`, retrieved 2026-09-16.
- Dataset license: CC0, as stated in the source package DESCRIPTION.
- Unmodified license text: `public_penguins_v3.LICENSE.md`.
- CSV SHA-256: `f204db2c753b0937caac3cb35258562c14f073e4bbc76be24b4c51ce22767a93`.

The fixture has 344 rows and eight columns. Missing values remain `NA`.
The six new tasks explicitly define filters, units, and missing-value handling;
their references are computed from the downloaded file before any model runs.
Tasks and source hashes are frozen in `output/submission_revision_v3/protocol.json`.
The source CSV is never poisoned; only eligible returned observations are edited.

This is a small public-data transfer check, not six independent datasets, not
an unseen-data claim, and not evidence of production-scale generalization.
The common public dataset may have appeared in model training.
