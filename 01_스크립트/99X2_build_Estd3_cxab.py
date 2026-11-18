#!/usr/bin/env python3
# 99X2 — CXAB(자궁경부암 검진 세포 이상 판정) 연령 간접표준화 E (2026-11-13; 99U2_build_Estd3_undx.py 복제·수정, 원본 수정 없음).
#  cases  = 시군구 '비정형 세포 이상'+'자궁경부암 전구단계 의심'(2018~)+'자궁경부암 의심' 인원(KOSIS DT_35007_N019, KOSIS '-' = 0: 시군구 합 = 전국 계 검산)
#  구성 결과: cases_ASC(비정형 세포 이상만), cases_HG(전구단계 의심+암 의심; 2018 이전에는 암 의심만)
#  offset = 시군구 자궁경부암 검진 판정 수검자(N019 '계'), 여성만.
#  전국 연령(14구간 20-24 … 80-84, 85+; 20-29세는 2016 대상 확대 이후만): 분자·분모 DT_35007_N020(99X_cxab_fetch_national.py).
#  시군구 수검자 연령 구조: KOSIS에 시군구×연령 판정 표가 없다 → 99U2와 같은 근사(주민등록 여자 5세 인구 × 전국 연령별 수검률, (d,y) 실측 수검자로 재척도).
#  E_std[d,y] = Σ_a exam_hat × 전국 판정률[y,a], 연도별 ΣE=Σcases 재척도. E_crude(수검자 × 전국 판정률, 선별 단계 E)·E_pop(여자 인구 분모, 수검 선택 민감도).
#  산출: 02_패널/CXAB_Estd3.csv
#  사용: ST_FBDZIP=<창원 2023 교정 인구 폴더> python3 01_스크립트/99X2_build_Estd3_cxab.py
import os, importlib.util, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석"); PAN = os.path.join(ROOT, "02_패널")
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m38 = _load("m38", "38_build_Estd_all.py"); cw = _load("cw", "40_region_crosswalk.py")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
TAG = "CXAB"; YEARS = list(range(2011, 2025))
BANDS = [f"{lo}-{lo+4}" for lo in range(20, 85, 5)] + ["85+"]
CAT = {"": ["비정형 세포 이상", "자궁경부암 전구단계 의심", "자궁경부암 의심"], "_ASC": ["비정형 세포 이상"], "_HG": ["자궁경부암 전구단계 의심", "자궁경부암 의심"]}
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"
def band(a):
    a = NFC(a).replace(" ", "")
    if a == "85세이상": return "85+"
    if a.endswith("세") and "~" in a: lo, hi = a[:-1].split("~"); return f"{lo}-{hi}"
    return None
# ── 전국 연령별(N020) ──
N = pd.read_csv(os.path.join(SRC, "DT_35007_N020_national_long.csv"), dtype=str); N["DT"] = pd.to_numeric(N.DT, errors="coerce").fillna(0); N["year"] = N.PRD_DE.astype(int)
N["C1_NM"] = N.C1_NM.map(NFC); N["C2_NM"] = N.C2_NM.map(NFC); N["band"] = N.C1_NM.map(band)
EX = N[(N.C2_NM == "계") & N.band.notna()].pivot_table(index="year", columns="band", values="DT", aggfunc="sum").reindex(columns=BANDS).fillna(0)
EXT = N[(N.C2_NM == "계") & (N.C1_NM == "계")].set_index("year").DT
assert (abs(EX.sum(1) - EXT) <= 2).all(), (EX.sum(1) - EXT)
NUM = {s: N[N.C2_NM.isin(c) & N.band.notna()].pivot_table(index="year", columns="band", values="DT", aggfunc="sum").reindex(index=YEARS, columns=BANDS).fillna(0) for s, c in CAT.items()}
RATE = {s: (NUM[s] / EX.replace(0, np.nan)).fillna(0) for s in CAT}
print("[99X2] 전국 판정률(%):", (100 * NUM[""].sum(1) / EX.sum(1)).round(2).to_dict())
print("[99X2] 20-29세 수검(2016~ 대상 확대):", EX[["20-24", "25-29"]].sum(1).astype(int).to_dict())
# ── 시군구 여자 5세 주민등록 인구(99U2 매칭 규칙 그대로, 여자만) ──
base = pd.read_csv(os.path.join(AN, "PERIO", "panel_PERIO.csv"), encoding="utf-8-sig"); base["fbd_region"] = base.fbd_region.map(NFC); base["key"] = base.key.map(NFC)
base = base[["year", "key", "fbd_region"]].drop_duplicates()
PKEYS = set(base.key); SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]; OLD85 = ["85-89세", "90-94세", "95-99세", "100세 이상"]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시", ("충청남도", "연기군"): "세종시|세종시"}; rows = []
for y in YEARS:
    d = pd.read_csv(os.path.join(m38.FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
    d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip()
    d["여자"] = pd.to_numeric(d["여자"].str.replace(",", ""), errors="coerce")
    sido = None; city = None; blocks = (d["행정구역별"] != d["행정구역별"].shift()).cumsum()
    for _, g in d.groupby(blocks, sort=False):
        nm = g["행정구역별"].iat[0]
        if nm == "전국": continue
        if nm in SIDO_HDR:
            sido = nm; city = None
            if nm != "세종특별자치시": continue
            g = g.drop_duplicates("연령별")
        sg = nm.split("-")[-1]
        if sg.endswith("시"): city = sg
        elif sg.endswith("구") and city is not None and cw.sido_std(sido) not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): continue
        else: city = None
        key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
        if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
        a = g.set_index("연령별")["여자"]; tot = a.get("계", np.nan)
        if pd.isna(tot): continue
        f = a.reindex(FIVE); o = a.reindex(OLD85).fillna(0); assert f.notna().all(), (y, nm)
        rows.append({"year": y, "key": NFC(key), "tot": tot, **{b: f[b + "세"] for b in BANDS[:-1]}, "85+": o.sum()})
G = pd.DataFrame(rows).groupby(["year", "key"], as_index=False)[["tot"] + BANDS].sum()
NATPOP = G.groupby("year")[BANDS].sum(); UPT = EX / NATPOP
# ── 시군구 판정(N019) → 코드 결합(99R_next5d 대응표) ──
L = pd.read_csv(os.path.join(SRC, "DT_35007_N019_sgg_long.csv"), dtype=str); L["DT"] = pd.to_numeric(L.DT, errors="coerce"); L["year"] = L.PRD_DE.astype(int); L["C2_NM"] = L.C2_NM.map(NFC)
raw_dash = int(L.DT.isna().sum()); L["DT"] = L.DT.fillna(0)   # KOSIS '-' = 0 (아래 시군구 합 = 전국 검산으로 확인)
cx = pd.read_csv(os.path.join(PAN, "next5d_cancerscreen_C1_crosswalk.csv"), dtype=str)
import sqlite3
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
R = pd.read_sql("select distinct sigungu_cd, fbd_region from disease_panel where tag='PERIO'", con); R["fbd_region"] = R.fbd_region.map(NFC); R = R.drop_duplicates("sigungu_cd")
assert len(R) == 229
# ★결합 결함 정정: KOSIS N019·N017의 부산 C1 B112/B113 이름(연제구/강서구)이 N009와 서로 뒤바뀌어 있고 값은 이름을 따른다.
#  선별 단계 99R_next5d는 C1만으로 결합(N009 우선)해 N019의 연제구 값을 강서구에 넣었다 → (C1, C1_NM) 쌍으로 결합한다.
L["C1_NM"] = L.C1_NM.map(lambda v: NFC(v).strip()); cx["C1_NM"] = cx.C1_NM.map(lambda v: NFC(v).strip())
L = L.merge(cx[["C1", "C1_NM", "sigungu_cd"]].drop_duplicates(["C1", "C1_NM"]), on=["C1", "C1_NM"], how="left", validate="many_to_one")
NAT = L[L.C1 == "15350AC400Z1"]; L = L[L.sigungu_cd.notna()].merge(R, on="sigungu_cd", how="left", validate="many_to_one"); assert L.fbd_region.notna().all()
P = L[L.C2_NM == "계"].groupby(["year", "fbd_region"]).DT.sum().rename("examinees").to_frame()
for s, c in CAT.items(): P["cases" + s] = L[L.C2_NM.isin(c)].groupby(["year", "fbd_region"]).DT.sum()
P = P.reset_index().fillna({k: 0 for k in ["cases" + s for s in CAT]})
natc = NAT[NAT.C2_NM.isin(CAT[""])].groupby("year").DT.sum(); natx = NAT[NAT.C2_NM == "계"].groupby("year").DT.sum()
rr_c = P.groupby("year").cases.sum() / natc; rr_x = P.groupby("year").examinees.sum() / natx
print(f"[99X2] KOSIS '-' 칸 {raw_dash}(0으로) · 시군구 합/전국 세포 이상 {rr_c.min():.4f}~{rr_c.max():.4f} · 수검자 {rr_x.min():.4f}~{rr_x.max():.4f}")
assert ((rr_c - 1).abs() < 0.002).all() and ((rr_x - 1).abs() < 0.002).all()
assert P.groupby("year").fbd_region.nunique().eq(229).all() and P[P.fbd_region == NFC("세종시세종시")].year.nunique() == 14, "세종·229 누락"
assert (P.examinees > 0).all() and not P.duplicated(["year", "fbd_region"]).any()
# 선별 단계 E와 대조
S0 = pd.read_csv(os.path.join(PAN, "CXAB_Estd3r.csv"), encoding="utf-8-sig"); S0["fbd_region"] = S0.fbd_region.map(NFC)
cmp_ = P.merge(S0, on=["year", "fbd_region"], how="outer", validate="one_to_one", indicator=True)
assert (cmp_._merge == "both").all()
dif = cmp_[((cmp_.cases_x - cmp_.cases_y).abs() > 0.5) | ((cmp_.examinees - cmp_.offset).abs() > 0.5)]
print(f"[99X2] 선별 단계(CXAB_Estd3r)와 다른 칸 {len(dif)}: {sorted(dif.fbd_region.unique())} (B112/B113 이름 뒤바뀜 정정분만이어야 함)")
assert set(dif.fbd_region) <= {NFC("부산시강서구"), NFC("부산시연제구")}
# ── 수검자 연령 구조 근사 → E ──
P = P.merge(base, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert P.key.notna().all()
X = P[["year", "key"]].merge(G, on=["year", "key"], how="left", validate="one_to_one")
miss = X.tot.isna()
print("[99X2] 여자 5세 인구 없는 칸", int(miss.sum()), X.loc[miss, ["year", "key"]].values.tolist()[:10])
assert not miss.any()
raw = X[BANDS].values * UPT.loc[X.year.values].values
sc = P.examinees.values / raw.sum(1); exam = raw * sc[:, None]
rsc = lambda e, s: e * P.groupby("year")["cases" + s].transform("sum").values / pd.Series(e).groupby(P.year.values).transform("sum").values
for s in CAT:
    P["E_std" + s] = rsc((exam * RATE[s].loc[P.year.values].values).sum(1), s)
    P["E_pop" + s] = rsc((X[BANDS].values * (NUM[s] / NATPOP).loc[P.year.values].values).sum(1), s)
    assert np.allclose(P.groupby("year")["E_std" + s].sum(), P.groupby("year")["cases" + s].sum())
natr = P.groupby("year").cases.sum() / P.groupby("year").examinees.sum(); P["E_crude"] = P.examinees * P.year.map(natr)
P["young20_29_share_exam"] = exam[:, :2].sum(1) / exam.sum(1)
H = pd.read_csv(os.path.join(PAN, "HTND_Estd2.csv"), encoding="utf-8-sig"); H["fbd_region"] = H.fbd_region.map(NFC)
P = P.merge(H[["year", "fbd_region", "pop80_share_raw"]], on=["year", "fbd_region"], how="left", validate="one_to_one"); assert P.pop80_share_raw.notna().all()
for s in CAT: P["SIR_std" + s] = P["cases" + s] / P["E_std" + s]
P["SIR_crude"] = P.cases / P.E_crude; P["SIR_pop"] = P.cases / P.E_pop
cols = ["year", "fbd_region", "examinees", "cases", "cases_ASC", "cases_HG", "E_std", "E_std_ASC", "E_std_HG", "E_pop", "E_crude", "young20_29_share_exam", "pop80_share_raw", "SIR_std", "SIR_std_ASC", "SIR_std_HG", "SIR_crude", "SIR_pop"]
fp = os.path.join(PAN, f"{TAG}_Estd3.csv"); P[cols].to_csv(fp, index=False, encoding="utf-8-sig")
r = P.E_std / P.E_crude
print(f"[99X2] {fp}: 행 {len(P)}, 시군구 {P.fbd_region.nunique()}, 세포 이상 합 {int(P.cases.sum()):,}, 수검자 합 {int(P.examinees.sum()):,}, 0칸 {int((P.cases==0).sum())}")
print(f"[99X2] E_std/E_crude {r.min():.3f}~{r.max():.3f} (P5 {r.quantile(.05):.3f}, P95 {r.quantile(.95):.3f}) · Spearman(SIR_std,SIR_crude) {P.SIR_std.corr(P.SIR_crude, method='spearman'):.3f} · (SIR_std,SIR_pop) {P.SIR_std.corr(P.SIR_pop, method='spearman'):.3f}")
print(f"[99X2] 재척도 배수 {sc.min():.3f}~{sc.max():.3f} (P5 {np.quantile(sc,.05):.3f}, P95 {np.quantile(sc,.95):.3f}) · Spearman(SIR_ASC,SIR_HG) {P.SIR_std_ASC.corr(P.SIR_std_HG, method='spearman'):.3f}")
_o = pd.DataFrame({"year": P.year, "fbd_region": P.fbd_region, "sc": sc}).sort_values("sc")
print("[99X2] 재척도 배수 극단(하위·상위 5):", _o.head(5).round(3).values.tolist(), _o.tail(5).round(3).values.tolist())
