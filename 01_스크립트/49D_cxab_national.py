#!/usr/bin/env python3
# 49D — CXAB 전국 기술(2026-11-13): 연도별 수검자·세포 이상 판정률·범주 구성(비정형/전구/암 의심/기타), 연령별 판정률(DT_35007_N020).
#  산출: 04_분석/CXAB/results_desc/S49D_national_year.csv, S49D_national_age.csv
import os, unicodedata, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "04_분석", "CXAB", "results_desc"); os.makedirs(OUT, exist_ok=True)
N = pd.read_csv(os.path.join(ROOT, "00_원천", "C_NHIS_검진보험", "DT_35007_N020_national_long.csv"), dtype=str); N["DT"] = pd.to_numeric(N.DT, errors="coerce").fillna(0); N["year"] = N.PRD_DE.astype(int)
N["C1_NM"] = N.C1_NM.map(NFC); N["C2_NM"] = N.C2_NM.map(NFC)
T = N[N.C1_NM == "계"].pivot_table(index="year", columns="C2_NM", values="DT", aggfunc="sum").fillna(0)
Y = pd.DataFrame({"examinees": T["계"], "asc": T["비정형 세포 이상"], "precancer": T.get("자궁경부암 전구단계 의심", 0), "cancer_susp": T["자궁경부암 의심"], "other": T["기타"], "reactive": T["반응성 소견 및 감염성 질환"], "normal": T["이상소견 없음"]})
Y["abnormal"] = Y.asc + Y.precancer + Y.cancer_susp; Y["rate_pct"] = 100 * Y.abnormal / Y.examinees; Y["asc_share_pct"] = 100 * Y.asc / Y.abnormal; Y["asc_to_hg"] = Y.asc / (Y.precancer + Y.cancer_susp)
Y.reset_index().to_csv(os.path.join(OUT, "S49D_national_year.csv"), index=False, encoding="utf-8-sig")
ab = N[N.C2_NM.isin(["비정형 세포 이상", "자궁경부암 전구단계 의심", "자궁경부암 의심"]) & (N.C1_NM != "계")].groupby(["year", "C1_NM"]).DT.sum()
ex = N[(N.C2_NM == "계") & (N.C1_NM != "계")].groupby(["year", "C1_NM"]).DT.sum()
A = pd.DataFrame({"abnormal": ab, "examinees": ex}).reset_index(); A = A[A.examinees > 0]; A["rate_pct"] = 100 * A.abnormal / A.examinees
A.to_csv(os.path.join(OUT, "S49D_national_age.csv"), index=False, encoding="utf-8-sig")
print(Y.round(2).to_string()); print(A.groupby("C1_NM")[["abnormal", "examinees"]].sum().assign(rate=lambda d: (100 * d.abnormal / d.examinees).round(2)).to_string())
