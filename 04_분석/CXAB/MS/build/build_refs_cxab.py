#  주제 문헌 = refs/cxab_refs_verified.csv(PubMed efetch 검증, 문헌 에이전트) + refs/raw/esummary.json 저자 목록. 방법 문헌 = SKND 캐시(PubMed·Crossref 검증)에서 복사.
import os, json, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); AN = os.path.dirname(os.path.dirname(MS))
CSV = pd.read_csv(os.path.join(MS, "refs", "cxab_refs_verified.csv"), dtype=str).fillna("")
ES = json.load(open(os.path.join(MS, "refs", "raw", "esummary.json"), encoding="utf-8")); ES = ES.get("result", ES)
OUT = {}
for r in CSV.itertuples():
    e = ES.get(r.pmid) or {}
    au = [a["name"] for a in e.get("authors", []) if a.get("authtype", "Author") == "Author"] or [r.first_author]
    jr = e.get("source") or r.journal
    OUT[r.key] = dict(type="journal", authors=au, title=r.title.rstrip("."), journal=jr, year=int(r.year), vol=r.volume, issue=e.get("issue", ""), pages=r.pages, doi=r.doi, pmid=r.pmid, verified="PubMed efetch/esummary 2026-11-13")
SK = json.load(open(os.path.join(AN, "SKND", "MS", "build", "refs_sknd.json"), encoding="utf-8"))
for k in ["besag1991bayesian", "rue2009approximate", "simpson2017penalising", "vonelm2007strengthening", "inskip1983methods", "web:rcore2026", "bell2015explaining", "dupont2022spatial",
          "vanderweele2017sensitivity", "moran1950notes", "gelman2014understanding", "lipsitch2010negative", "kang2015korea"]:
    OUT[k] = SK[k]
OUT["web:kosis2026screening"] = dict(type="web", authors="National Health Insurance Service", title="National cancer screening statistics: cervical cancer screening results by district (DT_35007_N019) and by age (DT_35007_N020), and cancer screening target and examinee counts (DT_35007_N009, DT_35007_N010), 2011–2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="13 November 2026")
OUT["web:mois2026population"] = SK.get("web:mois2026population") or dict(type="web", authors="Ministry of the Interior and Safety", title="Resident registration population by administrative district, sex and 5-year age group, 2011–2024", url="https://jumin.mois.go.kr", year=2026, accessed="13 November 2026")
json.dump(OUT, open(os.path.join(HERE, "refs_cxab.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(OUT), "refs;", sum(1 for v in OUT.values() if v["type"] == "journal" and len(v["authors"]) == 1), "single-author entries")
# (11/14 review 반영) AMA 전체 쪽수, 이중 하이픈 정리, 쪽수 없는 전자 논문은 esummary elocationid의 논문 번호, 암등록 자료 웹 인용
def _full(p):
    if not p or "-" not in p: return p
    a, b = p.split("-", 1)
    if a.isdigit() and b.isdigit() and len(b) < len(a): b = a[:len(a) - len(b)] + b
    return f"{a}-{b}"
for k, r in OUT.items():
    if r.get("type") != "journal": continue
    r["pages"] = _full(r.get("pages", "")); r["title"] = r["title"].replace("--", "-")
    if not r.get("pages") and r.get("pmid") in ES:
        art = [x for x in ES[r["pmid"]].get("elocationid", "").split() if not x.startswith("10.") and x not in ("doi:", "pii:")]
        if art: r["pages"] = art[-1].rstrip(".")
OUT["web:kccr2026incidence"] = dict(type="web", authors="Korea Central Cancer Registry, National Cancer Center", title="Age-standardized incidence of cervical cancer by district, district releases for 2013 and 2018. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="13 November 2026")
json.dump(OUT, open(os.path.join(HERE, "refs_cxab.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
