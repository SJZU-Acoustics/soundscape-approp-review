#!/usr/bin/env bash
# =============================================================================
# run_all.sh -- one-command reproduction of every pooled estimate, figure and
# table that appears in the manuscript and its Supplementary Information.
#
#   bash run_all.sh                            (run from the repository root)
#   bash run_all.sh 2>&1 | tee output/run_log.txt   (also save the numbers)
#
# Pipeline:  data/<Mendeley .xlsx>  ->  output/figures/  +  output/tables/
# The intermediate/ folder holds the per-sheet CSVs and is safe to delete.
# =============================================================================
set -e
cd "$(dirname "$0")"

echo "== 1/4  Load the Mendeley Data workbook =="
python load_data.py

echo ""
echo "== 2/4  Meta-analysis: six random-effects pooled correlations + forest plot =="
Rscript code/meta_analysis.R

echo ""
echo "== 3/4  Main-text tables (Tables 1-4) =="
python code/build_tables.py

echo ""
echo "== 4/4  Supplementary tables (Tables S1-S2) =="
python code/build_si_tables.py

echo ""
echo "== Done.  Figures -> output/figures/   Tables -> output/tables/ =="
