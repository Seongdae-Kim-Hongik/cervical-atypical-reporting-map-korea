# -*- coding: utf-8 -*-
# figs_jlgtd_cxab.py — CXAB JLGTD 그림(2026-11-18, 패널 문자 대문자 1A·1B 규정, 선화 1200 dpi). 원본 figs_cxab(2026-11-14, figs_sknd 이식). 컬러, 패널 문자 = fig.text 상수 PANEL_LABEL_PT(모든 패널 같은 크기·굵기; 저널 지침 '(a), (b), (c)'에 따라 소문자),
#  방위표 3배(동해 중간), 그림 안 설명문 없음, 결합은 시군구 코드로만. TIFF: 지도 600 dpi, 선화 1200 dpi.
#  Fig 1 (a) 연도별 판정률(비정형·고등급) (b) 연령별 판정률 · Fig 2 지도 (a) 14년 SIR (b) 잔차 공간 RR (c) 핫·콜드스팟 (d) 비정형:고등급 비 2018-24 · Fig 3 3변수 모형별 RR
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_cxab import load, DESC, RS, B, DIV, FOR, MPA
SHP = os.path.expandvars("$ST_DATA_ROOT") + "/기타/R_Studio/FBD_DATA_ZIP/final.shp"
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figs_jlgtd"); OUTF = os.path.join(os.path.dirname(HERE), "out_jlgtd", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 170 * MM; DPI = 600; LW = 0.3
PANEL_LABEL_PT = 54   # 15 런북 11/10·37호: 48–64 pt, fig.text 상수 하나
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "legend.fontsize": 8, "legend.title_fontsize": 8.5, "axes.linewidth": 0.6, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["region"] = G.region.map(NFC); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
assert G.region.is_unique and len(G) == 229
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
def label(fig, ax, ch, dx=-0.02, dy=0.01):   # 축 왼쪽 위 바깥, 그림 좌표
    bb = ax.get_position(); fig.text(bb.x0 + dx, bb.y1 + dy, ch.upper(), fontsize=PANEL_LABEL_PT, fontweight="bold", va="bottom", ha="left")
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#303030", linewidth=0.5); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by, bh = x0 + 0.55 * W_, y0 + 0.03 * H_, 0.012 * H_
    ax.add_patch(Rectangle((bx, by), 50000, bh, facecolor="black", edgecolor="black", lw=0.5)); ax.add_patch(Rectangle((bx + 50000, by), 50000, bh, facecolor="white", edgecolor="black", lw=0.5))
    for k, t in ((0, "0"), (50000, "50"), (100000, "100")): ax.text(bx + k, by + bh + 0.01 * H_, t, ha="center", va="bottom", fontsize=6.5)
    ax.text(bx + 100000 + 0.015 * W_, by + bh / 2, "km", ha="left", va="center", fontsize=6.5)
    nx, ny, nw, nh = x0 + 0.93 * W_, y0 + 0.40 * H_, 0.06 * W_, 0.20 * H_
    ax.add_patch(Polygon([[nx - nw / 2, ny], [nx, ny + nh], [nx + nw / 2, ny], [nx, ny + 0.25 * nh]], closed=True, facecolor="black", edgecolor="black", lw=0.4))
    ax.text(nx, ny + nh + 0.012 * H_, "N", ha="center", va="bottom", fontsize=22, fontweight="bold")
def save(fig, k, dpi=DPI):
    p = os.path.join(FIG, f"Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi)); im.save(os.path.join(OUTF, f"Figure{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw"); return im.size


# Fig 1 전국 추이·연령
Y = pd.read_csv(os.path.join(DESC, "S49D_national_year.csv")); A = pd.read_csv(os.path.join(DESC, "S49D_national_age.csv")); yrs = list(range(2011, 2025))
fig = plt.figure(figsize=(W, 3.9)); axs = [fig.add_axes([0.09, 0.27, 0.38, 0.52]), fig.add_axes([0.60, 0.27, 0.38, 0.52])]
a = axs[0]; asc = 100 * Y.asc / Y.examinees; hg = 100 * (Y.precancer + Y.cancer_susp) / Y.examinees
a.bar(yrs, asc, color="#92C5DE", width=0.75, label="Atypical cells"); a.bar(yrs, hg, bottom=asc, color="#B2182B", width=0.75, label="Suspected precancer or cancer")
a.axvline(2017.5, color="#404040", lw=0.6, ls="--"); assert (asc + hg).max() < 3.0; a.set_ylim(0, 3.0); a.set_ylabel("Women with an abnormal result (%)"); a.set_xticks([2011, 2014, 2018, 2021, 2024])
a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, fontsize=7.5)
a = axs[1]; g = A[A.year >= 2016].groupby("C1_NM")[["abnormal", "examinees"]].sum(); g["r"] = 100 * g.abnormal / g.examinees
lab = [s.replace(" ~ ", "–").replace("세", "").replace("85이상", "≥ 85").replace("85 이상", "≥ 85") for s in g.index]; g.index = lab
order = [f"{lo}–{lo+4}" for lo in range(20, 85, 5)] + ["≥ 85"]; g = g.reindex(order); assert g.r.notna().all()
a.bar(range(len(g)), g.r, color="#4393C3", width=0.7); a.set_xticks(range(len(g))); a.set_xticklabels(g.index, rotation=60, fontsize=7); assert g.r.max() < 5.5; a.set_ylim(0, 5.5)
a.set_ylabel("Women with an abnormal result,\n2016–2024 (%)"); a.set_xlabel("Age group, years", fontsize=8)
for a in axs: a.spines[["top", "right"]].set_visible(False); a.tick_params(labelsize=8)
for a, ch in zip(axs, "ab"): label(fig, a, ch, dx=-0.08, dy=0.02)
s1 = save(fig, 1, dpi=1200)

# Fig 2 지도 2×2 — 결합은 시군구 코드
CW = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(B)), "02_패널", "next5d_cancerscreen_C1_crosswalk.csv"), dtype=str)
import sqlite3
DBP = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
con = sqlite3.connect(f"file:{DBP}?mode=ro", uri=True)
R = pd.read_sql("select distinct sigungu_cd, fbd_region from disease_panel where tag='PERIO'", con); R["fbd_region"] = R.fbd_region.map(NFC); R2C = dict(zip(R.fbd_region, R.sigungu_cd.astype(str))); assert len(R2C) == 229 and set(R2C.values()) == set(G.cd)
P = pd.read_csv(os.path.join(B, "panel_CXAB_std3.csv")); P["cd"] = P.fbd_region.map(NFC).map(R2C); assert P.cd.notna().all()
sm = P.groupby("cd").agg(c=("cases", "sum"), e=("E", "sum")); SIR = sm.c / sm.e
S6 = N["s6"].copy(); S6["cd"] = S6.fbd_region.map(NFC).map(R2C); assert S6.cd.nunique() == 229; d = S6.set_index("cd"); d["SIR"] = SIR
Q = pd.read_csv(os.path.join(RS, "S49R_district_ratio.csv")); Q["cd"] = Q.fbd_region.map(NFC).map(R2C); assert Q.cd.nunique() == 229; d["RAT"] = Q.set_index("cd").asc_hg_ratio
BR = [0, 0.67, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 99]; LB = ["< 0.67", "0.67–0.79", "0.80–0.89", "0.90–0.99", "1.00–1.09", "1.10–1.24", "1.25–1.49", "≥ 1.50"]
PAL = ["#053061", "#2166AC", "#67A9CF", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
for c in ("SIR", "RR"): assert d[c].min() >= BR[0] and d[c].max() < BR[-1]
fig = plt.figure(figsize=(W, 9.6)); pos = [[0.02, 0.60, 0.46, 0.34], [0.52, 0.60, 0.46, 0.34], [0.02, 0.10, 0.46, 0.34], [0.52, 0.10, 0.46, 0.34]]
for (col, ch), p in zip((("SIR", "a"), ("RR", "b")), pos[:2]):
    ax = fig.add_axes(p); gg = G.copy(); gg["v"] = gg.cd.map(d[col]); assert gg.v.notna().all()
    gg.plot(ax=ax, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, ch, dx=0.0, dy=-0.01)
fig.legend(handles=[Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)], title="Ratio (a, observed/expected; b, residual spatial)", loc="upper center", bbox_to_anchor=(0.5, 0.595), ncol=4, frameon=False, columnspacing=0.9, handlelength=1.2, fontsize=7)
ax = fig.add_axes(pos[2]); gg = G.copy(); gg["k"] = gg.cd.map(d["class"]); assert gg.k.notna().all()
CK = {"hotspot": "#B2182B", "coldspot": "#2166AC", "neutral": "#EFEFEF"}; gg.plot(ax=ax, color=gg.k.map(CK), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, "c", dx=0.0, dy=-0.01)
fig.legend(handles=[Patch(facecolor=CK[k], edgecolor="#777777", linewidth=LW, label=l) for k, l in (("hotspot", f"Hot spot ({N['n_hot']})"), ("coldspot", f"Cold spot ({N['n_cold']})"), ("neutral", "Neither"))],
           loc="upper center", bbox_to_anchor=(0.25, 0.095), ncol=3, frameon=False, fontsize=7.5, handlelength=1.2)
BR2 = [0, 4, 5, 6, 7, 8, 99]; LB2 = ["< 4", "4–4.9", "5–5.9", "6–6.9", "7–7.9", "≥ 8"]; PAL2 = ["#FFFFCC", "#C7E9B4", "#7FCDBB", "#41B6C4", "#2C7FB8", "#253494"]
assert d.RAT.min() >= BR2[0] and d.RAT.max() < BR2[-1]
ax = fig.add_axes(pos[3]); gg = G.copy(); gg["v"] = gg.cd.map(d["RAT"]); assert gg.v.notna().all()
gg.plot(ax=ax, column="v", cmap=ListedColormap(PAL2), norm=BoundaryNorm(BR2, len(PAL2)), edgecolor="#b5b5b5", linewidth=0.2); mapax(ax); label(fig, ax, "d", dx=0.0, dy=-0.01)
fig.legend(handles=[Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL2, LB2)], title="Atypical to high-grade ratio, 2018–2024", loc="upper center", bbox_to_anchor=(0.75, 0.095), ncol=3, frameon=False, fontsize=7, handlelength=1.2)
s2 = save(fig, 2)

# Fig 3 포레스트(3변수 × 모형)
LAB = {DIV: "Crude divorce rate", FOR: "Foreign residents\nper 1000", MPA: "Moderate-or-higher\nphysical activity"}; ORD = [DIV, FOR, MPA]
SEN = lambda s: (lambda v: N["sens"][s][v][:3] if v in N["sens"][s] else None)
MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "o", "#000000"),
       ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)][:3], "D", "#F4A582"),
       ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3], "D", "#B2182B"),
       ("Province-by-year effect", lambda v: N["s41"][("C4_sido_year_iid", v)][:3], "v", "#8073AC"),
       ("2011–2023 only", SEN("t23"), "s", "#2D004B"),
       ("Atypical cells only", SEN("CXASC"), "s", "#E08214"),
       ("Precancer or cancer, 2018–2024", SEN("CXHG"), "^", "#1B7837"),
       ("Transport-injury deaths as outcome", lambda v: N["nco"][("TRANS", v)][:3], "^", "#2166AC")]
VALS = [t for v in ORD for _, f, _, _ in MOD if (t := f(v)) is not None]; lo_all = min(t[1] for t in VALS); hi_all = max(t[2] for t in VALS)
fig, ax = plt.subplots(figsize=(W, 4.4)); fig.subplots_adjust(left=0.22, right=0.98, top=0.97, bottom=0.30)
off = np.linspace(-0.38, 0.38, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, mk, fc), o in zip(MOD, off):
        t = f(v)
        if t is None: continue
        e, lo_, hi_ = t; ax.plot([lo_, hi_], [i + o] * 2, color=fc, lw=0.9); ax.plot(e, i + o, marker=mk, mfc=fc, mec=fc, ms=3.8, ls="none")
ax.axvline(1, color="#808080", lw=0.6); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
ax.set_xscale("log"); xt = [0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 standard deviation (95% credible interval, log scale)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=fc, marker=m, mfc=fc, mec=fc, lw=0.9, ms=3.8, label=l) for l, _, m, fc in MOD], loc="upper center", bbox_to_anchor=(0.40, -0.15), ncol=3, frameon=False, fontsize=7.5)
s3 = save(fig, 3, dpi=1200)
print("figs", s1, s2, s3)
