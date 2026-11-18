#!/usr/bin/env python3
# 99c — CXAB(자궁경부암 검진 세포 이상 판정) 가설 풀 추가 열(2026-11-13, 99c_undx 복제·출력 파일만 분리, 원본 수정 없음). 결합은 코드표(이름 결합 금지, 군위 37310 별칭).
#  정본 통합자료(통합자료_261030/01_공변량_229x2011_2024.csv)
#   basic_livelihood_rate   = 수급자 비율(%) — 2021-23 일반구 시 30칸 + 창원 3칸 정정(15·19 맨 위 절, 33칸)
#   tertiary_educated_share = 대졸 이상 비율(%)
#   foreign_residents_per1000 = 인구 천명당 외국인 주민 — HPV 유병률이 다른 출신 지역 여성(혼인 이주) 구성의 대리
#   genhosp_per100k         = 종합병원 수 ÷ 인구 × 10만 — 병리과 자체 판독 기관 접근
#  KOSIS 암검진(DT_35007_N009, 99R_next5d 수집) — (C1, C1_NM) 쌍 결합
#   cx_screening_uptake     = 자궁경부암 검진 수검인원 ÷ 대상인원 × 100 — 검진 선택 축
#  MASTER
#   screening_clinic_share  = 검진기관 중 의원 비율(chk__요양기관_의원 ÷ (종합병원+병원+의원)) × 100 — 판독 기관 축(의원 검진 = 외부 수탁 세포병리 판독)
#  산출: 02_패널/EXT_canonical_pool_CXAB_261113.csv
import os, sqlite3, unicodedata
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, "..")); PAN = os.path.join(ROOT, "02_패널"); SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
ZD = os.environ.get("ST_CANON", os.path.join(os.path.expandvars("$ST_DATA_ROOT"), "기타/R_Studio/FBD_DATA_ZIP/통합자료_261030"))
C = pd.read_csv(os.path.join(ZD, "01_공변량_229x2011_2024.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str})
K = pd.read_csv(os.path.join(ZD, "00_시군구_229_대응표.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); assert K.sigungu_cd.is_unique and len(K) == 229
K.loc[K.sigungu_cd == "37310", "region"] = "대구시군위군"
C = C.drop(columns=["region"]).merge(K[["sigungu_cd", "region"]], on="sigungu_cd", how="left", validate="many_to_one"); assert C.region.notna().all()
fr = "foreign_residents_per_1000_pop" if C["foreign_residents_per_1000_pop"].notna().sum() >= C["foreign_residents_per_1000"].notna().sum() else "foreign_residents_per_1000"
out = pd.DataFrame({"year": C.year, "fbd_region": C.region.map(NFC), "sigungu_cd": C.sigungu_cd,
                    "basic_livelihood_rate": C.basic_livelihood_recipient_rate.astype(float),
                    "tertiary_educated_share": C.tertiary_educated_share.astype(float),
                    "foreign_residents_per1000": C[fr].astype(float),
                    "genhosp_per100k": C.general_hospitals.astype(float) / C["pop"].astype(float) * 1e5})
print("[99c-cxab] 외국인 열", fr)
out = out[(out.year >= 2011) & (out.year <= 2024)].sort_values(["fbd_region", "year"]).copy()
ref = out[out.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean()
yy = out.year.isin([2021, 2022, 2023])
bad = yy & ((out.basic_livelihood_rate < 0.2 * out.fbd_region.map(ref)) | (out.basic_livelihood_rate > 5 * out.fbd_region.map(ref)) | (out.fbd_region == NFC("경상남도창원시")))
print("[99c-cxab] 수급률 결함 칸", int(bad.sum()), sorted(out.loc[bad, "fbd_region"].unique()))
assert bad.sum() == 33 and out.loc[bad, "fbd_region"].nunique() == 11
out.loc[bad, "basic_livelihood_rate"] = np.nan
# KOSIS N009 자궁경부암 수검률 — (C1, C1_NM) 쌍 결합
L = pd.read_csv(os.path.join(SRC, "DT_35007_N009_sgg_long.csv"), dtype=str); L["DT"] = pd.to_numeric(L.DT, errors="coerce"); L["year"] = L.PRD_DE.astype(int)
for c in ("C1_NM", "C2_NM", "C3_NM"): L[c] = L[c].map(lambda v: NFC(v).strip() if isinstance(v, str) else v)
cx = pd.read_csv(os.path.join(PAN, "next5d_cancerscreen_C1_crosswalk.csv"), dtype=str); cx["C1_NM"] = cx.C1_NM.map(lambda v: NFC(v).strip())
L = L[(L.C2_NM == "합계") & (L.C3_NM == "자궁경부암")].merge(cx.drop_duplicates(["C1", "C1_NM"]), on=["C1", "C1_NM"], how="left", validate="many_to_one")
L = L[L.sigungu_cd.notna()]
U = L.pivot_table(index=["year", "sigungu_cd"], columns="ITM_NM", values="DT", aggfunc="sum")
U = (100 * U["수검인원"] / U["대상인원"]).rename("cx_screening_uptake").reset_index()
out = out.merge(U, on=["year", "sigungu_cd"], how="left", validate="one_to_one")
print("[99c-cxab] 수검률 결측", int(out.cx_screening_uptake.isna().sum()), "세종 연수", out[(out.fbd_region == NFC("세종시세종시")) & out.cx_screening_uptake.notna()].year.nunique())
# MASTER 검진기관 의원 비율
M = pd.read_parquet(os.path.join(PAN, "MASTER_시군구_연도_wide.parquet"), columns=["year", "fbd_region", "chk__요양기관_종합병원", "chk__요양기관_병원", "chk__요양기관_의원"])
M["fbd_region"] = M.fbd_region.map(NFC); tot = M[["chk__요양기관_종합병원", "chk__요양기관_병원", "chk__요양기관_의원"]].sum(1, min_count=3)
M["screening_clinic_share"] = 100 * M["chk__요양기관_의원"] / tot.where(tot > 0)
out = out.merge(M[["year", "fbd_region", "screening_clinic_share"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
V = ["basic_livelihood_rate", "tertiary_educated_share", "foreign_residents_per1000", "genhosp_per100k", "cx_screening_uptake", "screening_clinic_share"]
for c in V:
    n0 = int(out[c].isna().sum())
    out[c] = out.groupby("fbd_region")[c].transform(lambda s: s.interpolate(method="linear", limit_direction="both"))
    out[c] = out[c].fillna(out.groupby("year")[c].transform("mean"))
    nb = out.groupby("fbd_region")[c].transform(lambda s: (s.shift(1) + s.shift(-1)) / 2)
    print(f"[99c-cxab] 게이트 {c}: 채운 칸 {n0}, 이웃 평균 20% 미만 {int((out[c] < 0.2 * nb).sum())}칸, 5배 초과 {int((out[c] > 5 * nb).sum())}칸, 0값 {int((out[c] == 0).sum())}칸")
assert out.groupby("fbd_region").year.nunique().eq(14).all() and out.fbd_region.nunique() == 229 and not out.duplicated(["year", "fbd_region"]).any()
assert out[V].notna().all().all()
fp = os.path.join(PAN, "EXT_canonical_pool_CXAB_261113.csv"); out.drop(columns="sigungu_cd").to_csv(fp, index=False, encoding="utf-8-sig")
print(f"[99c-cxab] 저장 {fp} {out.shape}"); print(out[V].describe().T[["min", "50%", "max"]].round(2))
