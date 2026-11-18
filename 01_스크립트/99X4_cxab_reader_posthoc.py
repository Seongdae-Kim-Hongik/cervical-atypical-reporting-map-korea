#!/usr/bin/env python3
# 99X4 — CXAB 사후 분석(2026-11-13, 결과 본 뒤): 판독 신호 대 HPV 신호 구분.
#  (1) 시군구 비정형:고등급 비(ASC/HG, 2018-24 합산, 세포병리 정도관리 지표 ASC/SIL 비의 대리)의 분포·Moran's I·CXAB SIR과의 순위 상관
#  (2) DMKID·STRS 공간 효과(S3_spatial_OR)와 CXAB 원자료 SIR의 순위 상관(서울 서북·경기 북부 공통 고점 점검)
#  (3) 구성 결과별(비정형·고등급) SIR과 공변량(조이혼율·외국인·수검률·의원 비율) 순위 상관
#  산출: 04_분석/CXAB/results_std3/S49R_reader_posthoc.csv, S49R_district_ratio.csv
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd
from scipy.stats import spearmanr
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); AN = os.path.join(ROOT, "04_분석"); OUT = os.path.join(AN, "CXAB", "results_std3")
SHP = os.environ.get("ST_SHP", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "boundary", "final.shp"))
P = pd.read_csv(os.path.join(ROOT, "02_패널", "CXAB_Estd3.csv"), encoding="utf-8-sig"); P["fbd_region"] = P.fbd_region.map(NFC)
Q = P[P.year >= 2018].groupby("fbd_region")[["cases", "cases_ASC", "cases_HG", "E_std", "E_std_ASC", "E_std_HG", "examinees"]].sum()
Q["asc_hg_ratio"] = Q.cases_ASC / Q.cases_HG; Q["sir"] = Q.cases / Q.E_std; Q["sir_asc"] = Q.cases_ASC / Q.E_std_ASC; Q["sir_hg"] = Q.cases_HG / Q.E_std_HG
A = P.groupby("fbd_region")[["cases", "E_std"]].sum(); Q["sir_all"] = A.cases / A.E_std
# Moran's I (593 그래프)
G = gpd.read_file(SHP); G["region"] = G.region.map(NFC)
gl = open(os.path.join(AN, "CXAB", "graph_593.graph")).read().split("\n"); n = int(gl[0]); nb = {}
for ln in gl[1:]:
    t = ln.split()
    if t: nb[int(t[0]) - 1] = [int(x) - 1 for x in t[2:]]
def moran(x):
    z = x - x.mean(); num = sum(z[i] * z[j] for i in nb for j in nb[i]); W = sum(len(v) for v in nb.values())
    return n / W * num / (z ** 2).sum()
def moran_perm(x, k=999, seed=1):
    rng = np.random.default_rng(seed); I = moran(x); r = np.array([moran(rng.permutation(x)) for _ in range(k)]); return I, (1 + (r >= I).sum()) / (k + 1)
order = G.region.tolist(); assert len(order) == n
rows = []
for col, lab in [("asc_hg_ratio", "log ASC/HG ratio 2018-24"), ("sir_asc", "log SIR ASC 2018-24"), ("sir_hg", "log SIR HG 2018-24")]:
    x = np.log(Q.loc[order, col].values); I, p = moran_perm(x, 499); rows.append(dict(quantity=lab, stat="moran_I", value=round(I, 3), p=round(p, 4)))
for a, b in [("asc_hg_ratio", "sir"), ("asc_hg_ratio", "sir_asc"), ("asc_hg_ratio", "sir_hg"), ("sir_asc", "sir_hg")]:
    r, p = spearmanr(Q[a], Q[b]); rows.append(dict(quantity=f"{a} vs {b} (2018-24)", stat="spearman", value=round(r, 3), p=round(p, 4)))
for tag in ["DMKID", "STRS"]:
    f = os.path.join(AN, tag, "results_std3", "S3_spatial_OR.csv")
    if os.path.exists(f):
        S = pd.read_csv(f); S["fbd_region"] = S.fbd_region.map(NFC); j = S.set_index("fbd_region").join(Q[["sir_all", "sir_asc", "sir_hg"]], how="inner")
        for c in ["sir_all", "sir_asc", "sir_hg"]:
            r, p = spearmanr(j.OR, j[c]); rows.append(dict(quantity=f"{tag} spatial OR vs CXAB {c}", stat="spearman", value=round(r, 3), p=round(p, 4)))
X = pd.read_csv(os.path.join(AN, "CXAB", "panel_CXAB_std3.csv")); X["fbd_region"] = X.fbd_region.map(NFC)
cm = X[X.year >= 2018].groupby("fbd_region")[["crude_divorce_rate_raw", "foreign_residents_per_1000_raw", "cervical_screening_uptake_raw", "screening_clinic_share_raw", "moderate_pa_rate_raw"]].mean()
j = cm.join(Q)
for v in cm.columns:
    for c in ["sir_asc", "sir_hg", "asc_hg_ratio"]:
        r, p = spearmanr(j[v], j[c]); rows.append(dict(quantity=f"{v} vs {c} (2018-24 means)", stat="spearman", value=round(r, 3), p=round(p, 4)))
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "S49R_reader_posthoc.csv"), index=False, encoding="utf-8-sig"); print(R.to_string())
Q.reset_index().to_csv(os.path.join(OUT, "S49R_district_ratio.csv"), index=False, encoding="utf-8-sig")
print(Q.asc_hg_ratio.describe().round(2).to_dict()); print(Q.sort_values("asc_hg_ratio").tail(8)[["asc_hg_ratio", "sir_asc", "sir_hg"]].round(2))
