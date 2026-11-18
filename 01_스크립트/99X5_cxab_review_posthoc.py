#!/usr/bin/env python3
# 99X5 — CXAB 심사 대응 사후 분석(2026-11-14, review 지적): (1) 고등급·비정형 SIR과 침윤암 발생률 상관의 차이(부트스트랩 2,000회, 95% CI)
#  (2) 시군구 비정형 비중(비정형 ÷ (비정형+고등급), 2018-24)의 이질성: 이항 기대 대비 과산포(카이제곱, 분산비) (3) 비정형:고등급 비 P10/P90 배수
#  산출: 04_분석/CXAB/results_std3/S49X_review_posthoc.csv
import os, unicodedata, numpy as np, pandas as pd
from scipy.stats import spearmanr, chi2
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "04_분석", "CXAB", "results_std3")
P = pd.read_csv(os.path.join(ROOT, "02_패널", "CXAB_Estd3.csv")); P["fbd_region"] = P.fbd_region.map(NFC)
M = pd.read_parquet(os.path.join(ROOT, "02_패널", "MASTER_시군구_연도_wide.parquet"), columns=["year", "fbd_region", "canc__암_자궁경부__연령표준화발생률"]); M["fbd_region"] = M.fbd_region.map(NFC)
rows = []; rng = np.random.default_rng(20261114)
for yc in (2013, 2018):
    c = M[M.year == yc].dropna().set_index("fbd_region").iloc[:, -1]
    g = P.groupby("fbd_region")[["cases_ASC", "E_std_ASC", "cases_HG", "E_std_HG"]].sum(); j = pd.concat([g, c.rename("asr")], axis=1).dropna()
    a = (j.cases_ASC / j.E_std_ASC).values; h = (j.cases_HG / j.E_std_HG).values; y = j.asr.values; n = len(j)
    d0 = spearmanr(h, y)[0] - spearmanr(a, y)[0]; bs = []
    for _ in range(2000):
        i = rng.integers(0, n, n); bs.append(spearmanr(h[i], y[i])[0] - spearmanr(a[i], y[i])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5]); rows.append(dict(analysis=f"rho_HG_minus_rho_ASC_vs_cancer_{yc}", value=round(d0, 3), lo=round(lo, 3), hi=round(hi, 3), n=n))
Q = P[P.year >= 2018].groupby("fbd_region")[["cases_ASC", "cases_HG"]].sum(); Q["n"] = Q.cases_ASC + Q.cases_HG; p0 = Q.cases_ASC.sum() / Q.n.sum()
X2 = (((Q.cases_ASC - Q.n * p0) ** 2) / (Q.n * p0 * (1 - p0))).sum(); df = len(Q) - 1
rows.append(dict(analysis="asc_share_heterogeneity_chi2", value=round(X2, 1), lo=df, hi=float(chi2.sf(X2, df)), n=len(Q)))
rows.append(dict(analysis="asc_share_dispersion_ratio", value=round(X2 / df, 2), lo=np.nan, hi=np.nan, n=len(Q)))
r = Q.cases_ASC / Q.cases_HG; rows.append(dict(analysis="ratio_p90_over_p10", value=round(r.quantile(.9) / r.quantile(.1), 2), lo=round(r.quantile(.1), 2), hi=round(r.quantile(.9), 2), n=len(Q)))
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "S49X_review_posthoc.csv"), index=False, encoding="utf-8-sig"); print(R.to_string())
