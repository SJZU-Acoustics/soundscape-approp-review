#!/usr/bin/env python3
"""load_data.py -- read the Mendeley Data workbook placed in data/ and write each
data sheet to intermediate/ as a CSV, ready for the analysis and figure modules.

Usage:  python load_data.py        (run from the repository root)
"""
import pandas as pd, pathlib, glob, sys

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT  = ROOT / "intermediate"
OUT.mkdir(exist_ok=True)

xlsx = sorted(glob.glob(str(DATA / "*.xlsx")))
if not xlsx:
    sys.exit("No workbook found. Download the Mendeley Data .xlsx and place it in data/ "
             "(see data/README.md).")
src = xlsx[0]

xl = pd.ExcelFile(src)
skip = {"README", "Sheet_summary", "variable_dictionary"}
sheets = [s for s in xl.sheet_names if s not in skip]
for s in sheets:
    # read as text so the round-trip is loss-free; each module re-infers types it needs
    xl.parse(s, dtype=str).to_csv(OUT / f"{s}.csv", index=False)
    print(f"  intermediate/{s}.csv")
print(f"Loaded {len(sheets)} data sheets from {pathlib.Path(src).name}")
