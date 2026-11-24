Code for reproducing the meta-analysis, figures and tables for the manuscript "Soundscape appropriateness as a contextual link between sound sources and perceived quality: a systematic review and selective meta-analysis".

## Requirements

- Python 3.9+ (developed on 3.11). Packages: `pandas`, `numpy`, `openpyxl`.

  ```bash
  pip install pandas numpy openpyxl
  ```

- R 4.5+ (developed on 4.5.3). CRAN packages: `metafor`, `dplyr`, `readr`, `ggplot2`.

  ```r
  install.packages(c("metafor", "dplyr", "readr", "ggplot2"))
  ```

- Typical install time: a few minutes with binary packages. No non-standard hardware is required.

## Data

The pipeline reads a single input: the Mendeley Data workbook
`Soundscape_appropriateness_evidence_2013-2026.xlsx`.

1. Download the current version from Mendeley Data: <https://doi.org/10.17632/zt84bkww95> (CC BY 4.0). The workbook describes 67 empirical reports and 53 independent studies. Two reports of the Granada soundwalks are one dataset, and only the 2021 report enters the pooled estimates.
2. Place the `.xlsx` file in the `data/` folder (see `data/README.md`).

The workbook holds the audited data tables that underlie the manuscript: the report
characteristics, the extracted effect sizes, the per-study pooling inputs (Fisher-z and
variance), and the team-computed result tables. Source-study full texts and the search
exports are not redistributed (publisher / Clarivate / Elsevier terms); their DOIs are in
the workbook's `corpus_citations.csv` and the article reference list.

## File structure

- `run_all.sh` — master script: loads the workbook, re-runs the meta-analysis, and writes the data-derived figure and tables.
- `load_data.py` — reads the data sheets from the workbook into `intermediate/`.
- `code/meta_analysis.R` — random-effects pooling (REML, Fisher-z) of the six families that met the five-study threshold, from the deposited `pool_inputs`; writes the pooled estimates and the Figure 2 forest plot (points and 95% confidence intervals).
- `code/questionnaire_alpha.csv` gives the three numeric coefficients and their source DOIs. Table 2 counts these by instrument class. Six text markers for missing values had been included in the summary count in the version 2 deposit.
- `code/build_tables.py` — main-text Tables 1–4 (characteristics, instruments, pooled estimates, GRADE certainty).
- `code/build_si_tables.py` — Supplementary Tables S3 (full report list, file `tableS1_reports.tex`) and S4 (non-pooled families, file `tableS2_nonpooled.tex`).

The conceptual framework (Figure 3) and the PRISMA flow (Figure 1) are drawn in LaTeX/TikZ in the manuscript and are not data-derived, so they are not regenerated here.

## Usage

From the repository root:

```bash
bash run_all.sh
```

The full pipeline runs in a few seconds. Outputs are written to:

- `output/figures/` — the Figure 2 forest plot (`forest.png`, 600 dpi)
- `output/tables/` — Tables 1–4 and Supplementary Tables S3–S4 (LaTeX fragments)

The console log lists every pooled estimate (r, 95% CI, 95% prediction interval, I²). To save it:

```bash
bash run_all.sh 2>&1 | tee output/run_log.txt
```

## Notes

- Random-effects pooling uses restricted maximum likelihood (REML) via `metafor`. Correlations were Fisher-z transformed for pooling and back-transformed to r; Spearman coefficients were converted with r = 2·sin(π·ρ/6) and one estimate per dataset (cluster) is used, all carried in the deposited `pool_inputs` table.
- `intermediate/` and `output/` are produced at run time and are safe to delete.

## License

Code in this repository is released under the MIT License (see `LICENSE`). The input data are archived separately under CC BY 4.0 at Mendeley Data. The review is registered on the Open Science Framework (https://osf.io/v6nfc).
