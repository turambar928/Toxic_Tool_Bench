# Public V4 evidence-control data

Retrieved 2026-09-16 without transformations from UCI's hosted CSV exports:

- `public_auto_mpg_v4.csv`: R. Quinlan, Auto MPG, UCI id 9,
  DOI https://doi.org/10.24432/C5859H,
  https://archive.ics.uci.edu/static/public/9/data.csv.
- `public_bike_v4.csv`: Hadi Fanaee-T, Bike Sharing, UCI id 275,
  DOI https://doi.org/10.24432/C5W894,
  https://archive.ics.uci.edu/static/public/275/data.csv.
  Fanaee-T and Gama, *Event labeling combining ensemble detectors and
  background knowledge*, DOI https://doi.org/10.1007/s13748-013-0040-3.

Both dataset landing pages explicitly specify Creative Commons Attribution
4.0 International: https://creativecommons.org/licenses/by/4.0/legalcode.
Attribution and source links are retained here. No endorsement is implied.
Auto MPG's export contains 398 records; Bike Sharing's hourly export contains
17,379 records (use the file count, not the inconsistent API metadata count).
Hashes and actual row counts are frozen in the V4 protocol.

The third source is the already archived `public_penguins_v3.csv` (344 rows,
CC0); see its existing license and provenance files. All three are familiar
public datasets, not claimed unseen in training. Missing numeric entries are
excluded from mean/sum; count with a null column counts all matching rows.
Task queries, filters and multiplicative corruptions are new synthetic
interventions over real observations, not naturally occurring corruptions.
