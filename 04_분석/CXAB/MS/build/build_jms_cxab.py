#   (Objectives/Setting/Methods/Results/Conclusions), 키워드 ≥4, 본문 Introduction/Methods/Results/Discussion/Conclusions,
#   표지 = 제목·저자·소속·교신 연락처·선언 목록, 본문 끝 Acknowledgements → Author contributions → Statements and Declarations(6항),
#   Sage Vancouver(번호 위첨자는 구두점 뒤, 저자 3명까지·4명 이상은 3명 + et al, 학술지 약어), 그림 300 dpi, 단일 익명, 추천 심사자 받지 않음, 게재료 없음.
import os, re, json, subprocess
from docx.shared import Pt
import content_cxab as C
import ms_base_cxab as B0
from ms_base_cxab import TX, table1, table2, put_table, docx_text, ORCID, AFFIL, ADDRESS, PHONE, ETHICS, REFS
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out_jms"); os.makedirs(OUT, exist_ok=True)
N = C.N
DRAFT = os.path.join(MS, "draft", "02_manuscript_jms.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
_gf = os.path.join(OUT, "github_url.txt"); GITHUB = open(_gf).read().strip() if os.path.exists(_gf) else "[GITHUB URL]"
TITLE = "Atypical-cell results dominate the district map of abnormal cervical screening results in Korea"
KEYWORDS = "Papanicolaou test; atypical squamous cells of the cervix; uterine cervical neoplasms; early detection of cancer; quality control; spatial analysis; Republic of Korea"
assert ":" not in TITLE and "HPV" not in TITLE and "Pap " not in TITLE and TITLE != C.TITLE
AI_USE = ("The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. "
          "The author reviewed and edited all output and takes full responsibility for the content of this publication.")
CREDIT = "Seongdae Kim: conceptualization, data curation, formal analysis, methodology, software, visualization, writing – original draft, and writing – review and editing."
CONSENT_P = "Not applicable. Only published aggregate statistics were used, and the Institutional Review Board waived informed consent."
CONSENT_PUB = "Not applicable."
COI = "The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article."
FUNDING = "The author received no financial support for the research, authorship, and/or publication of this article."
def data_statement(): return (f"All source data are publicly available aggregate statistics from the National Health Insurance Service, resident registration, the Korea Community Health Survey and the national cancer registry, accessed through the Korean Statistical Information Service. "
                             f"The analysis code that generates every number, table and figure is openly available on GitHub ({GITHUB}) and archived on Zenodo (https://doi.org/{ZENODO}). The processed district-year data are available from the author on reasonable request.")

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t):   # Sage Vancouver STM: 위첨자 번호는 구두점 뒤
    t = re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
    return re.sub(r"(\{\{[^}]+\}\})([.,;:])", r"\2\1", t)

def ref(k):   # Sage Vancouver: 저자 3명까지(마지막 앞 and), 4명 이상 = 3명 + et al. / 'J Abbr Year; Vol: pages.'
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}, {r['url']} ({r['year']}, accessed {r['accessed']})."
    au = r["authors"]; a = (au[0] if len(au) == 1 else ", ".join(au[:-1]) + " and " + au[-1]) if len(au) <= 3 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} {r['journal']} {r['year']}"
    if r.get("vol"): s += f"; {r['vol']}"
    if r.get("pages"): s += f": {r['pages'].replace('-', '–')}"
    s += "."
    if r.get("doi"): s += f" DOI: {r['doi']}."
    return s

def declarations(J, lvl=2):
    for h, t in [("Ethical considerations", ETHICS), ("Consent to participate", CONSENT_P), ("Consent for publication", CONSENT_PUB),
                 ("Declaration of conflicting interest", COI), ("Funding", FUNDING), ("Data availability", data_statement())]:
        J.head(h, lvl); J.para(t)

LK = N["lik"]
REPL = [   # 교차검토(2026-11-18) 반영: 이 원고에서만 바꾸는 문장(content_cxab 원본 보존), 각각 정확히 1회 적용
 ("according to the STROBE statement [@vonelm2007strengthening] (STROBE checklist). ", "according to the STROBE statement, with the checklist provided as a supplementary file [@vonelm2007strengthening]. "),
 ("Women aged 20-29 years became eligible in 2016 and had the highest abnormal rates (Figure 1). ",
  "Women aged 20-29 years became eligible in 2016. The published tables do not define the 'other' category, which was larger than the outcome in every year before 2018 and fell sharply in 2018; it was not part of the outcome, and before 2018 the program had no separate category for suspected precancerous lesion (Table S4). "),
 ("the national abnormal rate by year and 14 age groups (20-24 to 85 years or older) was applied",
  "the national abnormal rate by year and age group (12 groups from 30-34 years in 2011-2015 and 14 groups from 20-24 years from 2016, up to 85 years or older) was applied"),
 ("(higher-grade results, 2018-2024).",
  "(higher-grade results, 2018-2024). Here higher-grade denotes the program categories suspected precancerous lesion and suspected cancer; the published tables do not map them to Bethesda low-grade or high-grade lesions, so the district ratio of atypical to higher-grade results is not directly comparable with laboratory benchmarks."),
 ("were filled by within-district interpolation, then the district mean (Table S1).", "were filled by within-district interpolation, then the district mean and then the national year mean (Table S1)."),
 (f"({N['waic_nb']:,.1f} vs {N['waic_pois']:,.1f})", f"({LK['nbinomial']['WAIC']:,.1f} vs {LK['poisson']['WAIC']:,.1f}; Table S2)"),
 ("Abnormal rates were highest at 20-24 years", "Over 2016-2024, abnormal rates were highest at 20-24 years"),
 ("For the 2013 release the correlations were ", "Both comparisons used district SIRs for 2018-2024 for higher-grade results and for 2011-2024 for atypical cells; for the 2013 release the correlations were "),
 ("; the atypical share was ", "; the variance of the district atypical share was "),
 (" times more dispersed than binomial variation (", " times that expected under binomial variation ("),
 ("For atypical cells only, all 3 remained credible;", "For atypical cells only, all 3 remained credible (physical activity with a lower limit of 1.000 after rounding);"),
]
def apply_repl(p, used):
    for i, (a, b) in enumerate(REPL):
        if a in p: p = p.replace(a, b); used[i] += 1
    return p

def tbl(t): return (re.sub(r"^TABLE (\d)\.", r"Table \1.", t[0]),) + tuple(t[1:])

def build(counts=None):
    D = read_draft(); J = TX(cite="sup"); c = counts or {}
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim, PhD", before=6); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Telephone: {PHONE}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Word count:</b> main text, {c.get('main', '[M]')} words; abstract, {c.get('abstract', '[A]')} words; tables, 2; figures, 3; references, {c.get('refs', '[R]')}; supplementary files, 2 (Supplementary material and STROBE checklist).", before=6)
    J.para("<b>Declarations</b>", before=6)
    J.para(f"<b>Ethical considerations:</b> {ETHICS}"); J.para(f"<b>Consent to participate:</b> {CONSENT_P}"); J.para(f"<b>Consent for publication:</b> {CONSENT_PUB}")
    J.para(f"<b>Declaration of conflicting interest:</b> {COI}"); J.para(f"<b>Funding:</b> {FUNDING}"); J.para(f"<b>Data availability:</b> {data_statement()}")
    J.page_break(); J.head("Abstract", 1)
    for p in D["Abstract"]:
        m = re.match(r"^(Objectives|Setting|Methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}:</b> {m.group(2)}")
    J.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    used = [0] * len(REPL)
    J.head("Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(apply_repl(p, used)), indent=True)
    J.head("Results", 1)
    s4 = f"the 'other' category fell from {N['other_2017_2018'][0]:,} to {N['other_2017_2018'][1]:,}"; hit = 0
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]:
            if s4 in p: p = p.replace(s4, s4 + " (national counts by category and year in Table S4)", 1); hit += 1
            J.para(pandoc_cites(apply_repl(p, used)), indent=True)
    assert hit == 1 and used == [1] * len(REPL), used
    J.head("Discussion", 1); lvl = 2
    for p in D["Discussion"]:
        if p.startswith("### "):
            h = p[4:].strip(); J.head(h, 1 if h == "Conclusions" else 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("Acknowledgements", 1); J.para("None.")
    J.head("Author contributions", 1); J.para(CREDIT)
    J.head("Statements and Declarations", 1); declarations(J)
    assert sorted(J.cites) == B0.KEYS, (set(J.cites) ^ set(B0.KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, tbl(table1()))
    J.new_page("landscape"); put_table(J, tbl(table2()), fs=8)
    J.new_page("portrait"); J.head("Figure legends", 1)
    for k in sorted(B0.FIGCAP): J.para(f"<b>Figure {k}.</b> {B0.FIGCAP[k]}", after=6)
    return J, rl, D

def main_words(path):
    t = docx_text(path); i = t.find("\nIntroduction\n"); j = t.find("\nAcknowledgements\n"); return len(t[i:j].split())

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx"); D = read_draft()
    aw = sum(len(re.sub(r"^(Objectives|Setting|Methods|Results|Conclusions):\s*", "", x).split()) for x in D["Abstract"])
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p)
    for _ in range(2):
        mw = main_words(p); J, rl, D = build({"main": f"{mw:,}", "abstract": aw, "refs": len(rl)}); J.doc_title = "Manuscript"; J.save(p)
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_cxab_jms", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
    npg = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", p.replace(".docx", ".pdf")], capture_output=True, text=True).stdout).group(1))
    mw = main_words(p); assert mw <= 4000 and aw <= 250
    open(os.path.join(OUT, "reference_list.txt"), "w", encoding="utf-8").write("\n".join(rl))
    print(f"[build] main text {mw} (limit 4000) · abstract {aw} (limit 250) · refs {len(rl)} · pages {npg}")
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"main={mw}\nabstract={aw}\nrefs={len(rl)}\npages={npg}\n")
