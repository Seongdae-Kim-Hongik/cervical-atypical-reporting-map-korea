#!/usr/bin/env python3
# 99X — CXAB(자궁경부암 검진 세포 이상 판정) 전국 연령별 표를 KOSIS에서 받는다(2026-11-13, 99U_fetch·99R_next5d_fetch 방식 복제, 원본 수정 없음).
#  ① DT_35007_N020 연령별 자궁경부암 검진 결과 판정 현황(분자·분모 연령별)
#  ② DT_35007_N010 연령별 성별 암검진 대상 및 수검인원 현황(수검자 연령 구조 근사용 전국 연령별 수검률)
#  키: ~/.kosis_key(내용 출력 금지). 산출: 00_원천/C_NHIS_검진보험/<TBL>_national/<연도>.json, <TBL>_national_long.csv
import os, sys, json, time, urllib.request, urllib.parse
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
KEY = open(os.path.expanduser("~/.kosis_key")).read().strip()
URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do?"
for T in (sys.argv[1:] or ["DT_35007_N020", "DT_35007_N010"]):
    OUT = os.path.join(SRC, f"{T}_national"); os.makedirs(OUT, exist_ok=True); rows = []
    for y in range(2011, 2025):
        f = os.path.join(OUT, f"{y}.json")
        if not os.path.exists(f):
            for nl in (4, 3, 2, 1):
                q = dict(method="getList", apiKey=KEY, itmId="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y), orgId="350", tblId=T,
                         **{f"objL{i}": "ALL" for i in range(1, nl + 1)})
                for k in range(3):
                    try: d = json.loads(urllib.request.urlopen(URL + urllib.parse.urlencode(q), timeout=300).read().decode("utf-8")); break
                    except Exception as e: time.sleep(5 * (k + 1)); d = {"err": str(type(e).__name__)}
                if not (isinstance(d, dict) and d.get("err") == "21"): break
            if isinstance(d, dict): print(f"[99X-f] {T} {y} 오류 응답: {d}"); continue
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False); time.sleep(1)
        d = json.load(open(f, encoding="utf-8"))
        for r in d: rows.append({k: r.get(k) for k in ("PRD_DE", "C1", "C1_NM", "C2", "C2_NM", "C3", "C3_NM", "C4", "C4_NM", "ITM_ID", "ITM_NM", "UNIT_NM", "DT")})
        print(f"[99X-f] {T} {y}: {len(d):,}행", flush=True)
    L = pd.DataFrame(rows); L.to_csv(os.path.join(SRC, f"{T}_national_long.csv"), index=False, encoding="utf-8-sig")
    for c in ("C1_NM", "C2_NM", "C3_NM", "C4_NM", "ITM_NM"):
        if c in L and L[c].notna().any(): print(T, c, L[c].nunique(), list(L[c].dropna().unique()[:25]))
