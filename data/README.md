# data/

Place the Mendeley Data workbook here before running the pipeline:

    Soundscape_appropriateness_evidence_2013-2026.xlsx

Download it from Mendeley Data: <https://doi.org/10.17632/zt84bkww95.1> (CC BY 4.0). The data
are **not** committed to this repository — the code and the data are released
separately (code = MIT here; data = CC BY 4.0 on Mendeley Data).

`load_data.py` reads the first `.xlsx` it finds in this folder and writes one
CSV per data sheet into `../intermediate/`.
