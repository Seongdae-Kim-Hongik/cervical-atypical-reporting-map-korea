#  규정(Author Guidelines, onlinelibrary.wiley.com/page/journal/13652303/homepage/forauthors.html, 11/20 확인):
#   원저 ≤3,000단어, 구조 초록 ≤250(Objective/Methods/Results/Conclusions), 키워드 2-6(MeSH), 제목 약어 금지, running title <70자,
#   제목면(제목·running·단어/표/그림 수·저자·소속·교신·감사·초록·키워드 + 윤리·자료·연구비·COI·동의·재사용 허가·임상시험 진술),
#   본문(제목·저자·감사·초록·키워드·Practitioner Points ≤3·서론~결론·참고문헌·표·그림 범례 목록), 표·그림 별도 파일, 단일 익명,
#   AMA 위첨자 번호, 그래픽 초록 필수(저자 제작), 'Inside this month' 2-3문장(약어 금지), 컬러 온라인 무료.
import os, re, subprocess, shutil
import content_cxab as C
import ms_base_cxab as B0
import ms_layout_cxab as JL
from ms_base_cxab import TX, table1, table2, put_table, docx_text, ORCID, ADDRESS, PHONE
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N
JL.DRAFT = os.path.join(MS, "draft", "manuscript.md")
_r = lambda f, d: open(os.path.join(OUT, f)).read().strip() if os.path.exists(os.path.join(OUT, f)) else d
ZENODO = _r("zenodo_doi.txt", "[ZENODO DOI]"); GITHUB = _r("github_url.txt", "[GITHUB URL]")
TITLE = "Reading or risk? Atypical-cell reports shape the district map of abnormal cervical cytology across South Korea"
RUNNING = "Atypical-cell reports and district maps of cervical cytology"
KEYWORDS = "Papanicolaou test; atypical squamous cells of the cervix; uterine cervical neoplasms; early detection of cancer; quality control; spatial analysis"
assert len(RUNNING) < 70 and 2 <= len(KEYWORDS.split(";")) <= 6 and ":" not in TITLE and not re.search(r"\b[A-Z]{2,}\b", TITLE)
AUTHOR = "Seongdae Kim, PhD"; AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ETHICS = JL.ETHICS_TP
ETHICS_M = ("The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012), before the analysis began, "
            "approved its continuing review on November 3, 2026 (7002340-202611-HR-040) and waived informed consent.")
FUNDING = "The author received no specific funding for this work."
COI = "The author has no conflicts of interest to declare."
CONSENT = "Not applicable; only published aggregate statistics were analyzed and no individual participant data or images are included."
PERMIT = "No material reproduced from other sources."
TRIAL = "Not applicable (observational ecological study)."
AICONT = "Seongdae Kim conceived the study, curated the data, conducted the analysis, prepared the figures and wrote and revised the manuscript."
def data_statement(): return (f"All source data are publicly available aggregate statistics (National Health Insurance Service, resident registration, Korea Community Health Survey and national cancer registry, via the Korean Statistical Information Service). "
                             f"The analysis code is openly available on GitHub ({GITHUB}) and archived on Zenodo (https://doi.org/{ZENODO}).")

def fix(t):
    t = t.replace(JL.IRB_NEW, ETHICS_M)
    t = t.replace("Supplemental Digital Content", "Supporting Information")
    return t
def cites(t): return JL.cites(fix(t))

def statements(J, lvl=1):
    for h, v in (("Author Contributions", AICONT), ("Acknowledgements", "None."), ("Funding", FUNDING), ("Conflict of Interest", COI),
                 ("Ethics Approval Statement", ETHICS), ("Patient Consent Statement", CONSENT), ("Permission to Reproduce Material from Other Sources", PERMIT),
                 ("Clinical Trial Registration", TRIAL), ("Data Availability Statement", data_statement())):
        J.head(h, lvl); J.para(v)

def build_ms():
    D = JL.read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para(AUTHOR, before=6); J.para(AFFIL)
    J.para(f"<b>Correspondence:</b> Seongdae Kim, PhD, {ADDRESS}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para("<b>Acknowledgements:</b> None.", before=6)
    J.head("Abstract", 1)
    for p in D["Abstract"]:
        m = re.match(r"^(Objective|Methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}:</b> {m.group(2)}")
    J.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    J.head("Practitioner Points", 1)
    for p in D["Practitioner Points"]: J.para("• " + p)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(cites(p), indent=True)
    J.head("Materials and Methods", 1); M, used = JL.methods()
    for h, ps in M:
        J.head(h, 2)
        for p in ps: J.para(cites(p), indent=True)
    s4 = f"the 'other' category fell from {N['other_2017_2018'][0]:,} to {N['other_2017_2018'][1]:,}"; hit = 0
    J.head("Results", 1); tu = [0] * len(JL.TRIM)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]:
            if s4 in p: p = p.replace(s4, s4 + " (national counts by category and year in Table S4)", 1); hit += 1
            J.para(cites(JL.trim(JL.JM.apply_repl(p, used), tu)), indent=True)
    assert hit == 1 and tu == [1] * len(JL.TRIM), (hit, tu)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "):
            h = p[4:].strip(); J.head(h, 1 if h == "Conclusions" else 2); continue
        J.para(cites(JL.trim(p, [0] * len(JL.TRIM))), indent=True)
    J.counting = False
    statements(J, 1)
    assert set(J.cites) <= JL.KEEP, set(J.cites) - JL.KEEP
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + JL.ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(JL.FIGCAP): J.para(f"<b>Figure {k}.</b> {fix(JL.FIGCAP[k])}", after=6)
    return J, rl, D

def sec_words(path, a, b):
    t = docx_text(path); i = t.find(f"\n{a}\n"); j = t.find(f"\n{b}\n", i + 1); assert i >= 0 and j > i, (a, b); return len(t[i:j].split()) - 1

def build_tp(c, D):
    J = TX(cite="sup"); J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {RUNNING}", before=6)
    J.para(f"<b>Word count:</b> main text {c['text']:,}; abstract {c['abstract']}. <b>Tables:</b> 2. <b>Figures:</b> 3.", before=6)
    J.para(AUTHOR, before=6); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Telephone: {PHONE}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para("<b>Acknowledgements:</b> None.", before=6)
    J.head("Abstract", 2)
    for p in D["Abstract"]:
        m = re.match(r"^(Objective|Methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}:</b> {m.group(2)}")
    J.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    J.head("Inside this issue", 2); J.para(" ".join(D["Inside"]))
    statements(J, 2)
    p = os.path.join(OUT, "Title_page.docx"); J.doc_title = "Title page"; J.save(p); return p

def build_tables():
    J = TX(cite="sup"); put_table(J, JL.tbl(table1()))
    p1 = os.path.join(OUT, "Table1.docx"); J.doc_title = "Table 1"; J.save(p1)
    J = TX(cite="sup"); s0 = J.doc.sections[0]; from docx.enum.section import WD_ORIENT; from docx.shared import Cm as _Cm
    s0.orientation = WD_ORIENT.LANDSCAPE; s0.page_width, s0.page_height = _Cm(29.7), _Cm(21.0); put_table(J, JL.tbl(table2()), fs=8)
    p2 = os.path.join(OUT, "Table2.docx"); J.doc_title = "Table 2"; J.save(p2)
    return p1, p2

def topdf(p):
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_cxab_ms", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx")
    J, rl, D = build_ms(); J.doc_title = "Manuscript"; J.save(p)
    aw = sum(len(re.sub(r"^(Objective|Methods|Results|Conclusions):\s*", "", x).split()) for x in D["Abstract"])
    text = sec_words(p, "Introduction", "Author Contributions")
    ins = " ".join(D["Inside"]); pp = D["Practitioner Points"]
    assert text <= 3000 and aw <= 250 and len(pp) <= 3 and 2 <= len(re.findall(r"[.!?](\s|$)", ins)) <= 3 and not re.search(r"\b[A-Z]{2,}\b", ins), (text, aw)
    c = dict(abstract=aw, text=text)
    os.makedirs(os.path.join(OUT, "Figures"), exist_ok=True)
    for k in (1, 2, 3): shutil.copyfile(os.path.join(MS, "out_base", "Figures", f"Figure{k}.tif"), os.path.join(OUT, "Figures", f"Figure{k}.tif"))
    for f in (p, build_tp(c, D), *build_tables()): topdf(f)
    txt = docx_text(p)
    assert "Hongik University" in txt and "November 4, 2025" in txt and "Supplemental Digital Content" not in txt and "précis" not in txt.lower()
    assert not re.search(r"\b(we|our|us|I)\b", re.sub(r"Moran I\b|\(I+\)", "", txt.split("\nReferences\n")[0])), "1인칭"
    assert "—" not in txt
    open(os.path.join(OUT, "reference_list.txt"), "w", encoding="utf-8").write("\n".join(rl))
    open(os.path.join(OUT, "wordcount.txt"), "w").write("\n".join(f"{k}={v}" for k, v in c.items()) + f"\nrefs={len(rl)}\n")
    print(f"[build] text {text} (≤3000) · abstract {aw} (≤250) · refs {len(rl)} · practitioner points {len(pp)}")
