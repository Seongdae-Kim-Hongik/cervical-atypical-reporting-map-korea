#!/usr/bin/env python3
# 99X3 — CXAB 사후 타당도(2026-11-13): 시군구 세포 이상 SIR(원자료 합산)과 자궁경부암 발생률(암등록 연령표준화, MASTER canc__, 2013·2018 기간 값)의 순위 상관.
#  판독과 무관한 침윤암 발생이 같은 지리를 따르면 HPV 노출 쪽 근거, 따르지 않으면 판독 쪽 근거. 구성 결과(비정형·고등급)별로도.
#  산출: 04_분석/CXAB/results_std3/S49V_validity_cancer_incidence.csv
import os, unicodedata, numpy as np, pandas as pd
from scipy.stats import spearmanr
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAN = os.path.join(ROOT, "02_패널")
P = pd.read_csv(os.path.join(PAN, "CXAB_Estd3.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)
M = pd.read_parquet(os.path.join(PAN, "MASTER_시군구_연도_wide.parquet"), columns=["year", "fbd_region", "canc__암_자궁경부__연령표준화발생률", "canc__암_자궁경부__발생자수"]); M["fbd_region"] = M.fbd_region.map(NFC)
rows = []
for yc, win in [(2013, (2011, 2015)), (2018, (2016, 2020))]:
    c = M[M.year == yc].dropna(subset=["canc__암_자궁경부__연령표준화발생률"]).set_index("fbd_region")
    for out in ["", "_ASC", "_HG"]:
        for lab, sub in [("all_years", P), (f"window_{win[0]}-{win[1]}", P[P.year.between(*win)])]:
            g = sub.groupby("fbd_region")[["cases" + out, "E_std" + out]].sum(); sir = (g["cases" + out] / g["E_std" + out]).rename("sir")
            j = pd.concat([sir, c["canc__암_자궁경부__연령표준화발생률"].rename("asr"), c["canc__암_자궁경부__발생자수"].rename("n")], axis=1).dropna()
            r, p = spearmanr(j.sir, j.asr); jw = j[j.n >= 10]; rw, pw = spearmanr(jw.sir, jw.asr)
            rows.append(dict(cancer_period_value=yc, outcome="CXAB" + out, sir_years=lab, n=len(j), spearman=round(r, 3), p=round(p, 4), n_cases10plus=len(jw), spearman_cases10plus=round(rw, 3), p_cases10plus=round(pw, 4)))
R = pd.DataFrame(rows); fp = os.path.join(ROOT, "04_분석", "CXAB", "results_std3", "S49V_validity_cancer_incidence.csv"); R.to_csv(fp, index=False, encoding="utf-8-sig"); print(R.to_string())
