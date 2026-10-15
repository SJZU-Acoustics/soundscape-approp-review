# data/

Place the Mendeley Data workbook here before running the pipeline:

    Soundscape_appropriateness_evidence_2013-2026.xlsx

Download the current version from Mendeley Data: <https://doi.org/10.17632/zt84bkww95> (CC BY 4.0). The data
are **not** committed to this repository — the code and the data are released
separately (code = MIT here; data = CC BY 4.0 on Mendeley Data). Use the current version of the record. It counts the Granada soundwalk once.

`load_data.py` reads the first `.xlsx` it finds in this folder and writes one
CSV per data sheet into `../intermediate/`.
