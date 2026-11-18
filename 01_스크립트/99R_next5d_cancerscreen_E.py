#!/usr/bin/env python3
# 99R_next5d — 4차 후보: 국가암검진(유방·자궁경부·간) 수검·판정 시군구 분자와 E(2026-11-13).
#  원천: 00_원천/C_NHIS_검진보험/DT_35007_N009·N017·N019_sgg_long.csv (99R_next5d_fetch_cancerscreen.py). 위·대장은 교수 과제와 겹쳐 제외.
#  결합: KOSIS 분류 코드(C1) → 기준 SQLite sigungu_cd 대응표를 명시적으로 만들어 저장(02_패널/next5d_cancerscreen_C1_crosswalk.csv)하고 코드로만 합산.
#   - 시도 머리행(코드 12자리)은 버리되 세종(Q1, 2012~)은 시도 머리행이 곧 시군구이므로 직접 포함. 2011 세종 = 연기군(K110).
#   - 일반구(수원시장안구 등)·청원군 → 상위 시, 군위군(경북 N112·대구 C109) → 대구시군위군, 여주군·당진군 → 시.
#  E(연령 아닌 대상·수검 기준 간접표준화):
#   BRSU·CXSU·LVSU 수검: E = 시군구 대상인원 × 전국 수검률(연도별). 대상 정의(연령·성)가 전국 공통이라 대상 수가 연령 구성을 대신한다.
#   BRSP(유방암 의심)·BRRC(유방 판정유보)·CXAB(자궁경부 세포 이상 = 비정형 세포 이상 + 전구단계 의심 + 암 의심): E = 시군구 수검인원 × 전국 판정률(연도별).
#  연도별 ΣE = Σcases. 산출: 02_패널/<TAG>_Estd3r.csv
import os, sqlite3, unicodedata, re
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PAN = os.path.join(ROOT, "02_패널"); SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
NFC = lambda s: unicodedata.normalize("NFC", str(s))
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
base = pd.read_sql("select year, fbd_region, sido_std, sigungu, sigungu_cd, population from disease_panel where tag='PERIO'", con)
for c in ("fbd_region", "sido_std", "sigungu"): base[c] = base[c].map(NFC)
REF = base.drop_duplicates("sigungu_cd").set_index(["sido_std", "sigungu"]).sigungu_cd.to_dict()
LET = dict(A="서울시", B="부산시", C="대구시", D="인천시", E="광주시", F="대전시", G="울산시", H="경기도", I="강원도", J="충청북도", K="충청남도", L="전라북도", M="전라남도", N="경상북도", O="경상남도", P="제주도", Q="세종시")
SPECIAL = {"15350AC400Q1": "29010", "15350AC400K110": "29010"}  # 세종(머리행)·연기군
def load(T):
    L = pd.read_csv(os.path.join(SRC, f"{T}_sgg_long.csv"), dtype=str); L["DT"] = pd.to_numeric(L.DT, errors="coerce"); L["year"] = L.PRD_DE.astype(int)
    for c in ("C1_NM", "C2_NM", "C3_NM"):
        if c in L: L[c] = L[c].map(lambda v: NFC(v).strip() if isinstance(v, str) else v)
    return L
def code_of(c1, nm):
    if c1 in SPECIAL: return SPECIAL[c1]
    if len(c1) <= 12: return None  # 시도·전국 머리행
    sido = LET[c1[10]]; n = re.sub(r"\s+", "", nm)
    m = re.match(r"^(.+?시)(.+구)$", n)
    if m and sido not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): n = m.group(1)
    n = {"청원군": "청주시", "여주군": "여주시", "당진군": "당진시"}.get(n, n)
    if n == "군위군": return REF[("대구시", "군위군")]
    return REF.get((sido, n))
frames = {T: load(T) for T in ("DT_35007_N009", "DT_35007_N017", "DT_35007_N019")}
cx = pd.concat([f[["C1", "C1_NM"]] for f in frames.values()]).drop_duplicates()
cx["sigungu_cd"] = [code_of(a, b) for a, b in zip(cx.C1, cx.C1_NM)]
hdr = cx.C1.str.len() <= 12; um = cx[~hdr & cx.sigungu_cd.isna()]
assert um.empty, um
cx.to_csv(os.path.join(PAN, "next5d_cancerscreen_C1_crosswalk.csv"), index=False, encoding="utf-8-sig")
print(f"[99R5d-cs] 대응표 {len(cx)}행(머리행 {int(hdr.sum())}·세종 머리행 포함), 미결합 0")
def agg(L, filt):
    d = L[filt(L)].merge(cx[["C1", "sigungu_cd"]].drop_duplicates("C1"), on="C1", how="left")
    # 검산: 시군구 합 = 전국(Z1 계) — 세종 포함
    nat = d[d.C1 == "15350AC400Z1"].groupby("year").DT.sum(); d = d[d.sigungu_cd.notna()]
    s = d.groupby("year").DT.sum(); rr = (s / nat).dropna()
    assert ((rr - 1).abs() < 0.002).all(), rr
    return d.groupby(["year", "sigungu_cd"]).DT.sum()
N9, N17, N19 = frames["DT_35007_N009"], frames["DT_35007_N017"], frames["DT_35007_N019"]
def sel9(cancer, item): return lambda L: (L.C2_NM == "합계") & (L.C3_NM == cancer) & (L.ITM_NM == item)
spec = {
    "BRSU": (agg(N9, sel9("유방암", "수검인원")), agg(N9, sel9("유방암", "대상인원")), "유방암 검진 수검(대상 대비)"),
    "CXSU": (agg(N9, sel9("자궁경부암", "수검인원")), agg(N9, sel9("자궁경부암", "대상인원")), "자궁경부암 검진 수검(대상 대비)"),
    "LVSU": (agg(N9, sel9("간암", "수검인원")), agg(N9, sel9("간암", "대상인원")), "간암 검진 수검(고위험군 대상 대비)"),
    "BRSP": (agg(N17, lambda L: L.C2_NM == "유방암 의심"), agg(N17, lambda L: L.C2_NM == "계"), "유방암 검진 '유방암 의심' 판정"),
    "BRRC": (agg(N17, lambda L: L.C2_NM == "판정유보"), agg(N17, lambda L: L.C2_NM == "계"), "유방암 검진 판정유보(재검 필요)"),
    "CXAB": (agg(N19, lambda L: L.C2_NM.isin(["비정형 세포 이상", "자궁경부암 전구단계 의심", "자궁경부암 의심"])), agg(N19, lambda L: L.C2_NM == "계"), "자궁경부 세포 이상(비정형+전구+암 의심)"),
}
for T, (num, den, lab) in spec.items():
    X = base.set_index(["year", "sigungu_cd"]).join(num.rename("cases")).join(den.rename("den")).reset_index()
    miss = X[X.cases.isna() | X.den.isna() | (X.den <= 0)]
    print(f"[99R5d-cs] {T} 빈칸 {len(miss)}", miss.groupby("year").size().to_dict() if len(miss) else "")
    X = X[X.cases.notna() & (X.den > 0)].copy()
    assert X[X.fbd_region == NFC("세종시세종시")].year.nunique() >= 13, "세종 누락"
    X["E_raw"] = X.den * X.year.map(X.groupby("year").cases.sum() / X.groupby("year").den.sum())
    X["E_std"] = X.E_raw; X["offset"] = X.den
    X["E_crude"] = X.population * X.year.map(X.groupby("year").cases.sum() / X.groupby("year").population.sum())
    assert not X.duplicated(["year", "fbd_region"]).any() and (X.E_std > 0).all()
    X[["year", "fbd_region", "offset", "cases", "E_std", "E_crude"]].to_csv(os.path.join(PAN, f"{T}_Estd3r.csv"), index=False, encoding="utf-8-sig")
    yt = X.groupby("year").cases.sum()
    print(f"[99R5d-cs] {T} {lab}: {X.year.min()}-{X.year.max()} 시군구/연 {X.groupby('year').fbd_region.nunique().min()}~{X.groupby('year').fbd_region.nunique().max()} 합 {int(X.cases.sum()):,} 연 {yt.min():,.0f}~{yt.max():,.0f} 전국율 {float((X.cases.sum()/X.den.sum())):.4f} 0칸 {int((X.cases==0).sum())} 세종 {X[X.fbd_region==NFC('세종시세종시')].year.nunique()}년")
