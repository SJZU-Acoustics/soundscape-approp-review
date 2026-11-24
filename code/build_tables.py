#!/usr/bin/env python3
"""build_tables.py -- regenerate the four main-text LaTeX tables (1-4) from the
deposited data in intermediate/ (written by load_data.py). Table 3 reads the
pooled estimates recomputed by meta_analysis.R, so the table reflects the re-run
meta-analysis. Outputs -> output/tables/.
"""
import pandas as pd, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
INT  = ROOT / "intermediate"
OUT  = ROOT / "output" / "tables"
OUT.mkdir(parents=True, exist_ok=True)


def lz(x, nd=2):
    """Format with a leading zero and a proper LaTeX minus (house rule)."""
    if pd.isna(x):
        return "--"
    return f"{x:.{nd}f}".replace("-", "$-$")


def num(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# ---------------------------------------------------------------- Table 1
st = pd.read_csv(INT / "report_characteristics.csv")
st["country"] = st["country"].replace({"Türkiye": "Turkey"})
st = num(st, ["year", "reporting_quality_score", "n_participants"])
N = len(st)


def block(title, series, order=None, top=None, label_map=None):
    vc = series.value_counts()
    items = [(k, int(vc.get(k, 0))) for k in order] if order else list(vc.items())[:top]
    rows = [f"\\multicolumn{{2}}{{@{{}}l}}{{\\textit{{{title}}}}} \\\\"]
    for k, v in items:
        name = (label_map or {}).get(k, k)
        rows.append(f"\\quad {name} & {v} ({100*v/N:.0f}\\%) \\\\")
    return "\n".join(rows)


periods = pd.cut(st.year, [2012, 2017, 2020, 2023, 2026],
                 labels=["2013--2017", "2018--2020", "2021--2023", "2024--2026"],
                 include_lowest=True)

t1 = r"""\begin{table}[!tb]
\centering
\caption{Characteristics of the 67 empirical reports (describing 53 independent studies) of soundscape
appropriateness. Percentages are of the 67 reports. The full report-level table is in Supplementary
Table~S3.}
\label{tab:characteristics}
\footnotesize
\begin{tabular}{@{}lr@{}}
\toprule
Characteristic & Reports \\
\midrule
""" + "\n".join([
    block("Publication period", periods,
          order=["2013--2017", "2018--2020", "2021--2023", "2024--2026"]),
    r"\addlinespace",
    block("Setting", st.setting_indoor_outdoor,
          order=["outdoor", "indoor", "both"],
          label_map={"outdoor": "Outdoor", "indoor": "Indoor", "both": "Both"}),
    r"\addlinespace",
    block("Space function", st.space_function,
          order=["park", "residential", "healthcare", "educational", "square",
                 "office", "heritage", "street", "other"],
          label_map={k: k.capitalize() for k in
                     ["park", "residential", "healthcare", "educational", "square",
                      "office", "heritage", "street", "other"]}),
    r"\addlinespace",
    block("Data-collection method", st.method,
          order=["in-situ-survey", "soundwalk", "ex-situ-lab", "VR-immersive", "online-survey"],
          label_map={"in-situ-survey": "In-situ survey", "soundwalk": "Soundwalk",
                     "ex-situ-lab": "Ex-situ laboratory", "VR-immersive": "VR / immersive",
                     "online-survey": "Online survey"}),
    r"\addlinespace",
    block("Study design", st.study_design,
          order=["cross-sectional", "experimental", "mixed"],
          label_map={"cross-sectional": "Cross-sectional", "experimental": "Experimental",
                     "mixed": "Mixed"}),
    r"\addlinespace",
    block("Appropriateness instrument", st.SA_construct_status,
          order=["single-ISO-item", "per-source-appropriateness", "multi-item-scale"],
          label_map={"single-ISO-item": "Single ISO/TS 12913 item",
                     "per-source-appropriateness": "Per-source item",
                     "multi-item-scale": "Multi-item scale"}),
    r"\addlinespace",
    block("Overall risk of bias", st.RoB_overall,
          order=["high", "some-concerns", "low"],
          label_map={"high": "High", "some-concerns": "Some concerns", "low": "Low"}),
    r"\addlinespace",
    block("Most frequent countries", st.country, top=6),
]) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
(OUT / "table1_characteristics.tex").write_text(t1)


# ---------------------------------------------------------------- Table 2
ins = num(pd.read_csv(INT / "rq1_instrument_summary.csv"),
          ["n_studies", "alpha_reported_n", "mean_reporting_quality"])
name_map = {
    "single ISO/TS 12913 appropriateness item": "Single ISO/TS 12913 item",
    "per-source appropriateness item": "Per-source appropriateness item",
    "multi-item appropriateness/place-fit scale": "Multi-item appropriateness scale",
}
resp_map = {
    "VAS; numeric; Likert-verbal": "Verbal Likert, numeric, VAS",
    "numeric; Likert-verbal": "Verbal Likert, numeric",
    "Likert-verbal": "Verbal Likert",
}
_cls = {"single ISO/TS 12913 appropriateness item": "single-ISO-item",
        "per-source appropriateness item": "per-source-appropriateness",
        "multi-item appropriateness/place-fit scale": "multi-item-scale"}
questionnaire_alpha = pd.read_csv(ROOT / "code/questionnaire_alpha.csv").set_index("study_id").alpha
rows2 = []
for _, r in ins.iterrows():
    key = _cls.get(r.instrument_class)
    sub = st[st.SA_construct_status == key] if key else st.iloc[0:0]
    n_cls = len(sub) if key else int(r.n_studies)
    rq_cls = sub.reporting_quality_score.mean() if len(sub) else r.mean_reporting_quality
    rows2.append(" & ".join([
        name_map.get(r.instrument_class, r.instrument_class),
        str(int(n_cls)),
        str(r.years).replace("-", "--"),
        resp_map.get(r.response_types, r.response_types),
        str(int(sub.study_id.map(questionnaire_alpha).count())),
        f"{rq_cls:.0f}",
    ]) + r" \\")
t2 = r"""\begin{table}[!tb]
\centering
\caption{How soundscape appropriateness is operationalised across the 67 empirical reports (RQ1).
Counts in the $\alpha$ column refer to reports giving Cronbach's $\alpha$ for a broader questionnaire or battery. VAS, visual analogue scale.}
\label{tab:instruments}
\footnotesize
\resizebox{\textwidth}{!}{%
\setlength{\tabcolsep}{5pt}
\begin{tabular}{@{}lccp{3.7cm}cc@{}}
\toprule
Instrument class & Reports & Years & Response formats & $\alpha$ reported & Reporting quality (\%) \\
\midrule
""" + "\n".join(rows2) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
(OUT / "table2_instruments.tex").write_text(t2)


# ---------------------------------------------------------------- Table 3
reml = num(pd.read_csv(INT / "pooled_estimates.csv"),
           ["k", "estimate_r", "ci_low_r", "ci_high_r", "pi_low_r", "pi_high_r", "I2"])
reml = reml.set_index("pool_label")
order3 = [
    ("Determinants of appropriateness", None),
    ("\\quad Natural sounds", "source_natural"),
    ("\\quad Human or social sounds", "source_human_social"),
    ("\\quad Loudness", "index_loudness"),
    ("\\quad Sound level", "index_sound_level"),
    ("Associations with other appraisals", None),
    ("\\quad Pleasantness", "SA_pleasantness"),
    ("\\quad Acoustic comfort or soundscape quality", "SA_comfort_quality"),
]
inf_map = {"supported_positive": "Supported (+)", "supported_negative": "Supported ($-$)",
           "not_supported": "Not supported"}
rows3 = []
for label, key in order3:
    if key is None:
        rows3.append(f"\\multicolumn{{7}}{{@{{}}l}}{{\\textit{{{label}}}}} \\\\")
        continue
    r = reml.loc[key]
    rows3.append(" & ".join([
        label, str(int(r.k)), lz(r.estimate_r),
        f"{lz(r.ci_low_r)}, {lz(r.ci_high_r)}",
        f"{lz(r.pi_low_r)}, {lz(r.pi_high_r)}",
        f"{r.I2:.0f}", inf_map[r.inference],
    ]) + r" \\")
t3 = r"""\begin{table}[!tb]
\centering
\caption{Random-effects pooled correlations for the six association families that met the
five-study threshold (RQ2 and RQ3). Estimates are back-transformed from Fisher-$z$; positive correlations indicate that the two variables increase together. CI, 95\% confidence interval; PI, 95\% prediction interval;
$k$, number of independent studies. The sign in the inference column gives the direction when the 95\% CI excludes zero.
Benjamini--Hochberg adjusted $p$-values ($q$) were below 0.05 except for human or social sounds ($q=0.61$).}
\label{tab:pooled}
\footnotesize
\resizebox{\textwidth}{!}{%
\setlength{\tabcolsep}{5pt}
\begin{tabular}{@{}lcccccl@{}}
\toprule
Association with appropriateness & $k$ & $r$ & CI & PI & $I^2$ (\%) & Inference \\
\midrule
""" + "\n".join(rows3) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
(OUT / "table3_pooled.tex").write_text(t3)


# ---------------------------------------------------------------- Table 4
g = num(pd.read_csv(INT / "grade_certainty.csv"),
        ["k_studies", "estimate_r", "ci_low_r", "ci_high_r"])
g = g.set_index("pool_label")
reasons = {
    "source_natural": "Serious risk of bias, inconsistency, indirectness, imprecision",
    "source_human_social": "Very serious inconsistency and imprecision; serious risk of bias and indirectness",
    "index_loudness": "Serious risk of bias, inconsistency, imprecision (CI hugs zero)",
    "index_sound_level": "Serious risk of bias, inconsistency, imprecision",
    "SA_pleasantness": "Serious risk of bias and heterogeneity; large, precise, stable effect",
    "SA_comfort_quality": "Serious risk of bias and inconsistency; large, stable effect",
}
order4 = ["source_natural", "source_human_social", "index_loudness", "index_sound_level",
          "SA_pleasantness", "SA_comfort_quality"]
cert_map = {"low": "Low", "very-low": "Very low"}
rows4 = []
for key in order4:
    r = g.loc[key]
    rows4.append(" & ".join([
        r.pool_name, str(int(r.k_studies)),
        f"{lz(r.estimate_r)} ({lz(r.ci_low_r)}, {lz(r.ci_high_r)})",
        cert_map[r.final_certainty_after_13_4], reasons[key],
    ]) + r" \\")
t4 = r"""\begin{table}[!tb]
\centering
\caption{Certainty of the pooled evidence, rated with a GRADE approach adapted for observational
association evidence for RQ2 and RQ3. SA, soundscape appropriateness. No pooled family contained a low-risk-of-bias
study, which drives the universal risk-of-bias downgrade.}
\label{tab:grade}
\footnotesize
\resizebox{\textwidth}{!}{%
\setlength{\tabcolsep}{5pt}
\begin{tabular}{@{}lccp{1.7cm}p{5.4cm}@{}}
\toprule
Association & $k$ & $r$ (95\% CI) & Certainty & Main reasons \\
\midrule
""" + "\n".join(rows4) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
(OUT / "table4_grade.tex").write_text(t4)

print("Wrote 4 table fragments to", OUT)
