#   AI 사용은 방법 절에 공개, 참고문헌 AMA(6명 이하 전원·7명 이상 3명 + et al, 호수 생략), 다중 패널 1A·1B, 컬러 무료, 범례 ≤125단어.
import os, re, subprocess
import content_cxab as C
import ms_base_cxab as B0
import ms_text_cxab as JM
from ms_base_cxab import TX, table1, table2, put_table, docx_text, ORCID, ADDRESS, PHONE, REFS
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out_base"); os.makedirs(OUT, exist_ok=True)
N = C.N
DRAFT = os.path.join(MS, "draft", "manuscript_base.md")
_r = lambda f, d: open(os.path.join(OUT, f)).read().strip() if os.path.exists(os.path.join(OUT, f)) else d
ZENODO = _r("zenodo_doi.txt", "[ZENODO DOI]"); GITHUB = _r("github_url.txt", "[GITHUB URL]")
TITLE = JM.TITLE; RUNNING = "Atypical-cell results and screening maps"
KEYWORDS = "Papanicolaou test; atypical squamous cells of the cervix; uterine cervical neoplasms; early detection of cancer; quality control; spatial analysis; Republic of Korea"
assert len(TITLE) <= 120 and len(RUNNING) <= 40 and 6 <= len(KEYWORDS.split(";")) <= 10
KEEP = {"walboomers1999human", "arbyn2020estimates", "park2024cancer", "lee2025current", "shin2022trends", "shin2003prevalence", "burchell2006chapter", "plummer2003smoking",
        "stoler2001interobserver", "davey1994atypical", "wright2014interlaboratory", "renshaw2009asc", "choi2020continuous", "trott2024geographic",
        "vonelm2007strengthening", "web:kosis2026screening", "web:mois2026population", "inskip1983methods", "spix2016correction", "besag1991bayesian", "rue2009approximate",
        "knorrheld2000bayesian", "steegen2016increasing", "lipsitch2010negative", "vanderweele2017sensitivity", "web:kccr2026incidence", "greenland2001ecologic", "branca2015recommendations"}
assert len(KEEP) <= 30 and KEEP <= set(REFS)
ETHICS_TP = ("The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012), before the analysis began, and approved its continuing review on November 3, 2026 (7002340-202611-HR-040); "
             "informed consent was waived because only published aggregate statistics were used.")   # 11/19 반려: IRB 승인 날짜(승인서 원문 2025-11-04·2026-11-03)
assert B0.ETHICS.startswith("The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040)")
FUNDING = "None. The author received no financial support for the research, authorship, and/or publication of this article."
COI = "The author has no conflicts of interest to disclose."
def data_statement(): return (f"All source data are publicly available aggregate statistics (National Health Insurance Service, resident registration, Korea Community Health Survey and national cancer registry, via the Korean Statistical Information Service). "
                             f"The analysis code is openly available on GitHub ({GITHUB}) and archived on Zenodo (https://doi.org/{ZENODO}).")

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
TRIM = [   # 본문 3,000단어 여유(2026-11-18): 결과 절 세부를 보충 표로 넘김, 각각 정확히 1회
 (r"In a separate comparison with the forced controls, the beta-binomial \([\d,.]+\) and observation-level \([\d,.]+\) likelihoods had lower WAIC than the negative binomial \([\d,.]+\); with all characteristics, the observation-level model gave the same credible associations \(Table S2; Table S3\)\. ",
  "Two alternative likelihoods fitted better than the negative binomial, and the observation-level model gave the same credible associations (Table S2; Table S3). "),
 (r"; hit-and-run collisions \(RR[^)]*\) and fires \(RR[^)]*\) were not credible\.", "; hit-and-run collisions and fires were not credible."),
 (r"; its raw correlation with the district SIR was negative, it reversed without a district effect \(RR[^)]*\), it remained with type I and type III interactions and it was not credible with a 1-year lag \(RR[^)]*\)\.",
  "; its raw correlation with the district SIR was negative, and it reversed without a district effect and was not credible with a 1-year lag (Table S3)."),
]
def trim(p, used):
    for i, (a, b) in enumerate(TRIM):
        p, n = re.subn(a, b, p); used[i] += n
    return re.sub(r"Figure (\d)\[([a-d])\]", lambda m: f"Figure {m.group(1)}{m.group(2).upper()}", p)

def cites(t):   # 남길 문헌만, 위첨자는 구두점 뒤(AMA)
    def g(m):
        ks = [k.strip().lstrip("@") for k in m.group(1).split(";")]; ks = [k for k in ks if k in KEEP]
        return "{{" + ",".join(ks) + "}}" if ks else ""
    t = re.sub(r"\s*\[(@[^\]]+)\]", g, t)
    return re.sub(r"(\{\{[^}]+\}\})([.,;:])", r"\2\1", t)

DC = ("Twelve characteristics were chosen from the literature on HPV epidemiology and cervical cytology, each with a stated expected direction (Table S1, Supplemental Digital Content). "
      "Area-level proxies for HPV exposure were the crude divorce rate, the share of single-person households and foreign residents per 1000 population [@burchell2006chapter; @shin2003prevalence], with age-standardized current smoking as a cofactor [@plummer2003smoking]. "
      "Screening selection was represented by cervical screening coverage [@spix2016correction]; the reading setting by the share of clinics among screening institutions (clinic smears are read by commercial laboratories) and general hospitals per 100,000 population [@wright2014interlaboratory]; "
      "deprivation by the share of basic livelihood security recipients and the tertiary-educated share; and area health behavior by age-standardized walking, moderate-or-higher physical activity and public sports facilities per 100,000 population. "
      "Five controls were forced into every model (urban population share, physicians per 1000 population, sex ratio, fiscal autonomy and the population share aged 80 years or older), and 3 negative control exposures with no plausible link to cervical cytology (hit-and-run collisions, a traffic-culture index and fires) were fitted in a separate model [@lipsitch2010negative]. "
      "Gaps in covariates were filled by within-district interpolation, then the district mean and then the national year mean. All characteristics were standardized to mean 0 and SD 1.")
SA = [("The principal model was negative binomial, chosen before the characteristics were added by the prespecified rule of a lower widely applicable information criterion than Poisson (Table S2), "
       "with an offset of log expected counts, a Besag-York-Mollié 2 district effect and first-order random-walk and independent year effects, fitted by integrated nested Laplace approximation [@besag1991bayesian; @rue2009approximate] (priors in Supplemental Digital Content). "
       "Rate ratios (RRs) per 1 SD are reported with 95% credible intervals (CrIs); an association was called credible when its interval excluded 1, and with 12 characteristics about 0.6 credible associations would be expected by chance. "
       "Residual hot spots and cold spots were districts whose posterior probability of a residual spatial RR above 1 exceeded .95 or fell below .05; persistence of district rankings was measured by Kendall W and spatial autocorrelation by Moran I."),
      ("Robustness was assessed in 200 models with random covariate subsets (robust when credible in at least 75% of the models containing the characteristic with at least 95% sign agreement) [@steegen2016increasing], 4 Knorr-Held space-time interactions [@knorrheld2000bayesian], "
       "refits for 2011-2017, 2018-2024 and 2011-2023, a province-by-year random effect as a proxy for the catchments of reading laboratories and further specifications listed in Table S3. "
       "Transport-injury deaths and patients treated for gastric cancer were fitted with the same model as comparison outcomes, and E-values were computed for robust associations [@vanderweele2017sensitivity]. "
       "After the results were seen, 3 post hoc analyses were added: correlations of district SIRs with the incidence of invasive cervical cancer from the national cancer registry [@web:kccr2026incidence]; "
       "the district ratio of atypical to higher-grade results for 2018-2024, an area analog of the laboratory atypical-to-lesion ratio [@davey1994atypical; @renshaw2009asc], with a χ² test of heterogeneity of the atypical share; "
       "and refits of the association opposite to the expected direction with fewer activity measures. "
       "Claude (Anthropic) and ChatGPT (OpenAI) were used only for translation and English-language editing of the manuscript; the author reviewed and edited all output and takes full responsibility for the content.")]
IRB_OLD = "The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent."
IRB_NEW = "The institutional review board approved the study and waived informed consent (details on the title page)."
def methods():
    out = []; used = [0] * len(JM.REPL); irb = 0
    for x in C.METHODS:
        if x[0] == "District Characteristics": out.append((x[0], [DC])); continue
        if x[0] == "Statistical Analysis": out.append((x[0], SA)); continue
        ps = []
        for p in x[1:]:
            if IRB_OLD in p: p = p.replace(IRB_OLD, IRB_NEW); irb += 1
            p = p.replace("(Supporting Methods)", "(Supplemental Digital Content)")
            ps.append(JM.apply_repl(p, used))
        out.append((x[0], ps))
    assert irb == 1
    return out, used

def ref(k):   # AMA: 6명 이하 전원, 7명 이상 3명 + et al, 호수 생략, 학술지 약어
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Available at: {r['url']}. Accessed {r['accessed']}."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} {r['journal']} {r['year']}"
    if r.get("vol"): s += f";{r['vol']}"
    if r.get("pages"): s += f":{r['pages'].replace('-', '–')}"
    return s + "."

ABBR = [("BYM2", "Besag-York-Mollié 2"), ("CI", "confidence interval"), ("CrI", "credible interval"), ("HPV", "human papillomavirus"), ("RR", "rate ratio"), ("SD", "standard deviation"),
        ("SIR", "standardized incidence ratio"), ("STROBE", "Strengthening the Reporting of Observational Studies in Epidemiology"), ("WAIC", "widely applicable information criterion")]
FIGCAP = {k: re.sub(r"\(([a-d])\)", lambda m: f"({m.group(1).upper()})", v) for k, v in B0.FIGCAP.items()}

def build_ms():
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Précis:</b> {D['Precis'][0]}", before=6)
    J.head("Abstract", 1)
    for p in D["Abstract"]:
        m = re.match(r"^(Objectives|Methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}:</b> {m.group(2)}")
    J.para(f"<b>Key words:</b> {KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(cites(p), indent=True)
    J.head("Methods", 1); M, used = methods()
    for h, ps in M:
        J.head(h, 2)
        for p in ps: J.para(cites(p), indent=True)
    s4 = f"the 'other' category fell from {N['other_2017_2018'][0]:,} to {N['other_2017_2018'][1]:,}"; hit = 0
    J.head("Results", 1); tu = [0] * len(TRIM)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]:
            if s4 in p: p = p.replace(s4, s4 + " (national counts by category and year in Table S4)", 1); hit += 1
            J.para(cites(trim(JM.apply_repl(p, used), tu)), indent=True)
    over = " ".join(p for x in C.METHODS if x[0] in ("District Characteristics", "Statistical Analysis") for p in x[1:])
    skip = {i for i, (a, b) in enumerate(JM.REPL) if a in over}   # 새로 쓴 절에 있던 문장
    assert hit == 1 and all(u == 1 for i, u in enumerate(used) if i not in skip) and tu == [1] * len(TRIM), (used, tu)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "):
            h = p[4:].strip(); J.head(h, 1 if h == "Conclusions" else 2); continue
        J.para(cites(trim(p, [0] * len(TRIM))), indent=True)
    J.counting = False
    J.head("Abbreviations", 1); J.para("; ".join(f"{a}, {b}" for a, b in ABBR) + ".")
    assert set(J.cites) <= KEEP and len(J.cites) <= 30, (set(J.cites) - KEEP, len(J.cites))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    return J, rl, D

def sec_words(path, a, b):
    t = docx_text(path); i = t.find(f"\n{a}\n"); j = t.find(f"\n{b}\n", i + 1); return len(t[i:j].split()) - 1

def build_tp(c):
    J = TX(cite="sup"); J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {RUNNING}", before=6)
    J.para("Seongdae Kim, PhD", before=6); J.para("Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea")
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Telephone: {PHONE}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>IRB approval:</b> {ETHICS_TP}", before=6)
    J.para("<b>Disclosure statement:</b> " + COI + " Source of funding: none; " + FUNDING.replace("None. The author", "the author"))
    J.para(f"<b>Data availability:</b> {data_statement()}")
    J.para("<b>Author contributions:</b> Seongdae Kim conceived the study, curated the data, conducted the analysis, prepared the figures and wrote and revised the manuscript.")
    J.para("<b>Acknowledgements:</b> None.")
    J.para(f"<b>Word counts:</b> précis, {c['precis']}; abstract, {c['abstract']}; text, {c['text']:,} (introduction, {c['intro']}; discussion and conclusions, {c['disc']}).", before=6)
    J.para("<b>Counts:</b> tables, 2; figures, 3; Supplemental Digital Content files, 2 (supplementary methods and Tables S1–S4; STROBE checklist).")
    p = os.path.join(OUT, "Title_page.docx"); J.doc_title = "Title page"; J.save(p); return p

def tbl(t): return (re.sub(r"^TABLE (\d)\.", r"Table \1.", t[0]),) + tuple(t[1:])
def build_tables():   # 11/19 반려: 표마다 편집 가능한 Word 파일 하나씩(Table1.docx·Table2.docx)
    J = TX(cite="sup"); put_table(J, tbl(table1()))
    p1 = os.path.join(OUT, "Table1.docx"); J.doc_title = "Table 1"; J.save(p1)
    J = TX(cite="sup"); s0 = J.doc.sections[0]; from docx.enum.section import WD_ORIENT; from docx.shared import Cm as _Cm   # 빈 첫 쪽 없이 가로 방향
    s0.orientation = WD_ORIENT.LANDSCAPE; s0.page_width, s0.page_height = _Cm(29.7), _Cm(21.0); put_table(J, tbl(table2()), fs=8)
    p2 = os.path.join(OUT, "Table2.docx"); J.doc_title = "Table 2"; J.save(p2)
    return p1, p2
def build_legends():
    J = TX(cite="sup"); J.head("Figure Legends", 1)
    for k in sorted(FIGCAP):
        assert len(FIGCAP[k].split()) <= 125; J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}", after=6)
    p = os.path.join(OUT, "Figure_legends.docx"); J.doc_title = "Figure legends"; J.save(p); return p

def topdf(p):
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_cxab_layout", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_anonymized.docx")
    J, rl, D = build_ms(); J.doc_title = "Manuscript"; J.save(p)
    aw = sum(len(re.sub(r"^(Objectives|Methods|Results|Conclusions):\s*", "", x).split()) for x in D["Abstract"]); pw = len(D["Precis"][0].split())
    text = sec_words(p, "Introduction", "Abbreviations"); intro = sec_words(p, "Introduction", "Methods"); disc = sec_words(p, "Discussion", "Abbreviations")
    ow = len(D["Abstract"][0].replace("Objectives:", "").split())
    assert text <= 3000 and intro <= 400 and disc <= 1200 and aw <= 250 and pw <= 25 and ow <= 40, (text, intro, disc, aw, pw, ow)
    c = dict(precis=pw, abstract=aw, text=text, intro=intro, disc=disc)
    for f in (p, build_tp(c), *build_tables(), build_legends()): topdf(f)
    assert "Disclosure Statement" not in docx_text(p) and "November 4, 2025" in docx_text(os.path.join(OUT, "Title_page.docx"))
    txt = docx_text(p)
    assert not re.search(r"(?i)hongik|seongdae|kim s\b|github|zenodo|7002340", txt), "익명화 위반"
    open(os.path.join(OUT, "reference_list.txt"), "w", encoding="utf-8").write("\n".join(rl))
    open(os.path.join(OUT, "wordcount.txt"), "w").write("\n".join(f"{k}={v}" for k, v in c.items()) + f"\nrefs={len(rl)}\n")
    print(f"[build] text {text} (≤3000) · intro {intro} (≤400) · discussion+conclusions {disc} (≤1200) · abstract {aw} · objectives {ow} · précis {pw} · refs {len(rl)} (≤30)")
