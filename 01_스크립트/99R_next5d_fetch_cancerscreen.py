#!/usr/bin/env python3
# 99R_next5d — 4차 후보: 시군구 국가암검진 수검·판정(KOSIS DT_35007_N009·N017·N019) 연도별 수집(2026-11-13, 99R_next5b_fetch_N139.py 복제·표만 교체).
#  위암(N011)·대장암(N013)은 교수 위장관 암 과제와 겹쳐 받지 않는다.
#  키: ~/.kosis_key(내용 출력 금지). 산출: 00_원천/C_NHIS_검진보험/<TBL>_sgg/<연도>.json, <TBL>_sgg_long.csv
import os, sys, json, time, urllib.request, urllib.parse
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
KEY = open(os.path.expanduser("~/.kosis_key")).read().strip()
URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do?"
TBLS = sys.argv[1:] or ["DT_35007_N009", "DT_35007_N017", "DT_35007_N019"]
for T in TBLS:
    OUT = os.path.join(SRC, f"{T}_sgg"); os.makedirs(OUT, exist_ok=True); rows = []
    for y in range(2011, 2025):
        f = os.path.join(OUT, f"{y}.json")
        if not os.path.exists(f):
            for nl in (4, 3, 2, 1):  # 표의 분류 수를 모르므로 objL 개수를 줄여 가며 시도
                q = dict(method="getList", apiKey=KEY, itmId="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y), orgId="350", tblId=T,
                         **{f"objL{i}": "ALL" for i in range(1, nl + 1)})
                for k in range(3):
                    try: d = json.loads(urllib.request.urlopen(URL + urllib.parse.urlencode(q), timeout=300).read().decode("utf-8")); break
                    except Exception as e: time.sleep(5 * (k + 1)); d = {"err": str(type(e).__name__)}
                if not (isinstance(d, dict) and d.get("err") == "21"): break
            if isinstance(d, dict): print(f"[99R5d-f] {T} {y} 오류 응답: {d}"); continue
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False); time.sleep(1)
        d = json.load(open(f, encoding="utf-8"))
        for r in d:
            rows.append({k: r.get(k) for k in ("PRD_DE", "C1", "C1_NM", "C2", "C2_NM", "C3", "C3_NM", "C4", "C4_NM", "ITM_ID", "ITM_NM", "UNIT_NM", "DT")})
        print(f"[99R5d-f] {T} {y}: {len(d):,}행", flush=True)
    L = pd.DataFrame(rows); L.to_csv(os.path.join(SRC, f"{T}_sgg_long.csv"), index=False, encoding="utf-8-sig")
    for c in ("C1_NM", "C2_NM", "C3_NM", "C4_NM", "ITM_NM"):
        if c in L and L[c].notna().any(): print(T, c, L[c].nunique(), list(L[c].dropna().unique()[:14]))
