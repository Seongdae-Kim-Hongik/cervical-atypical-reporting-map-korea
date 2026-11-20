#   본문 → References(AMA, 저자 6명 이하 전원·7명 이상 3명 + et al, 수동 번호) → 표(각 쪽) → Figure legends. 미국 철자. 단일 익명. 소속 = 홍익대 단독.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from jkms_engine import JKMS
import content_cxab as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_cxab.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
PHONE = "+82-2-320-1114"
AI_STATEMENT = ("The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. "
                "The author reviewed and edited all output and takes full responsibility for the content of this publication.")
FUNDING = "This study received no specific funding."
COI = "The author declares no conflicts of interest."
CREDIT = "Seongdae Kim: Conceptualization, data curation, formal analysis, methodology, software, visualization, writing – original draft, and writing – review and editing."
ACK = "None."
def data_statement(): return (f"All source data are publicly available aggregate statistics from the National Health Insurance Service, resident registration, the Korea Community Health Survey and the national cancer registry, accessed through the Korean Statistical Information Service. "
                             f"The analysis code that generates every number, table and figure is openly available on Zenodo (https://doi.org/{ZENODO}). The processed district-year data are available from the author on reasonable request.")
ETHICS = "The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used."

def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_cxab.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys(); assert all(k in REFS for k in KEYS), [k for k in KEYS if k not in REFS]

def ref(k):   # AMA 11판(저널 지침: 6명 이하 전원, 7명 이상 3명 + et al)
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Accessed {r['accessed']}. {r['url']}"
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} <i>{r['journal']}</i>. {r['year']}"
    if r.get("vol"): s += f";{r['vol']}"
    if r.get("issue"): s += f"({r['issue']})"
    if r.get("pages"): s += f":{r['pages']}"
    s += "."
    if r.get("doi"): s += f" doi:{r['doi']}"
    return s

class TX(JKMS):
    raw = False
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

TAB1 = [("crude_divorce_rate", "Crude divorce rate, per 1000"), ("single_person_household_share", "Single-person households, %"), ("foreign_residents_per_1000", "Foreign residents, per 1000"),
        ("current_smoking_rate", "Current smoking, %"), ("cervical_screening_uptake", "Cervical screening coverage, %"), ("screening_clinic_share", "Clinics among screening institutions, %"),
        ("genhosp_per100k", "General hospitals, per 100,000"), ("basic_livelihood_rate", "Basic livelihood recipients, %"), ("tertiary_educated_share", "Tertiary-educated adults, %"),
        ("walking_practice_rate", "Walking, %"), ("moderate_pa_rate", "Moderate-or-higher physical activity, %"), ("public_sports_facilities_per_100k", "Public sports facilities, per 100,000")]
WC = ["W1_2011-17", "W2_2018-24", "ALL"]; WH = ["2011–2017", "2018–2024", "2011–2024"]
def table1():
    T = N["T1"]
    rows = [["__H__", "Screening"], ["  District-years, No."] + [f"{T[c]['n']:,}" for c in WC], ["  Screening examinations, No."] + [f"{T[c]['exam']:,}" for c in WC],
            ["  Abnormal results, No. (%)"] + [f"{T[c]['cases']:,} ({T[c]['rate']:.2f})" for c in WC],
            ["  District SIR, median (P10–P90)ᵃ"] + [f"{T[c]['med']:.2f} ({T[c]['p10']:.2f}–{T[c]['p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("Abbreviations: P10–P90, 10th–90th percentile; SD, standard deviation; SIR, standardized incidence ratio. ᵃObserved over age-standardized expected counts summed over the period. "
            "Characteristics are district-year means; the 5 forced controls are in Table S1.")
    return (f"TABLE 1. Cervical Screening Results and District Characteristics, {N['n_districts']} Districts, Republic of Korea, 2011–2024", ["Characteristic"] + WH, rows, foot)

GROUPS = [("HPV exposure and cofactor", [C.DIV, C.SPH, C.FOR, C.SMK]), ("Screening selection and reading setting", [C.UPT, C.CLI, C.GH]), ("Deprivation", [C.BLS, C.TE]), ("Physical activity", [C.WALK, C.MPA, C.FAC]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {C.DIV: "Crude divorce rate (+)", C.SPH: "Single-person households (+)", C.FOR: "Foreign residents (+)", C.SMK: "Current smoking (+)", C.UPT: "Screening coverage (−)",
         C.CLI: "Clinics among screening institutions (+)", C.GH: "General hospitals (−)", C.BLS: "Basic livelihood recipients (+)", C.TE: "Tertiary-educated adults (−)",
         C.WALK: "Walking (−)", C.MPA: "Moderate-or-higher physical activity (−)", C.FAC: "Public sports facilities (−)",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged ≥80 y"}
def f3(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
def table2():
    rows = []; assert set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][("KH_typeII", v)]; asc = N["sens"]["CXASC"][v]; hg = N["sens"]["CXHG"][v]
            rows.append([f"  {LABEL[v]}", f3((m["IRR"], m["lo"], m["hi"])), f"{100*mv['cred_frac']:.0f}" if mv else "Forced", f3(k), f3(asc), f3(hg)])
    foot = (f"Abbreviations: CrI, credible interval; HPV, human papillomavirus; RR, rate ratio per 1 standard deviation; expected direction in parentheses. Principal model: negative binomial with a Besag-York-Mollié 2 district effect and random-walk and independent year effects, all characteristics and 5 forced controls (n = {N['n_rows']:,} district-years). "
            "ᵃShare of the 200 covariate-subset models containing the characteristic in which the CrI excluded 1. ᵇKnorr-Held type II space-time interaction added, the best-fitting interaction model. "
            "ᶜAtypical cells only, 2011–2024. ᵈSuspected precancerous lesion or cancer, 2018–2024.")
    return (f"TABLE 2. District Characteristics and Abnormal Cervical Cytology, {N['n_districts']} Districts, Republic of Korea, 2011–2024",
            ["Characteristic", "Principal RR (95% CrI)", "Subsets credible, %ᵃ", "Type II RR (95% CrI)ᵇ", "Atypical cells RR (95% CrI)ᶜ", "Higher grade RR (95% CrI)ᵈ"], rows, foot)

FIGCAP = {
 1: "Cervical screening results, Korean National Cancer Screening Program, 2011–2024. (a) Women with an abnormal result by year, split into atypical cells and suspected precancer or cancer; the dashed line marks the 2018 introduction of the suspected precancerous lesion category. (b) Abnormal results by age group, 2016–2024.",
 2: "District geography of abnormal cervical cytology, 229 districts, Republic of Korea. (a) Standardized incidence ratio (observed over age-standardized expected counts, 2011–2024 pooled). (b) Residual spatial rate ratio from the principal model. (c) Residual hot spots and cold spots (posterior probability of a rate ratio above 1 >.95 or <.05). (d) Ratio of atypical-cell results to suspected precancer or cancer results, 2018–2024. Thick lines are province boundaries.",
 3: "Rate ratios per 1 standard deviation with 95% credible intervals for the 3 characteristics that were credible in all random-subset models, across alternative models: principal model, Knorr-Held type II and type IV space-time models, province-by-year random effect, 2011–2023 only, atypical cells only, suspected precancer or cancer (2018–2024), and transport-injury deaths as a comparison outcome. The horizontal axis is on a log scale.",
}
def foot_row(J, text, sz=9, ls=13):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    J._emit(p, text, sz)
def table_words(t): return len(" ".join([t[0]] + t[1] + [c for r in t[2] for c in r if c != "__H__"] + [t[3]]).split())
def put_table(J, t, fs=9):
    J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8)

def build(counts=None):
    D = read_draft(); J = TX(cite="sup")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para("Seongdae Kim, PhD", before=6); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Telephone: {PHONE}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Funding:</b> {FUNDING}", before=6); J.para(f"<b>Conflict of interest disclosures:</b> {COI}")
    J.para(f"<b>Author contributions:</b> {CREDIT}"); J.para(f"<b>Acknowledgments:</b> {ACK}")
    J.para(f"<b>Data availability:</b> {data_statement()}"); J.para(f"<b>Ethics approval:</b> {ETHICS}")
    J.para(f"<b>Precis:</b> {D['Precis'][0]}", before=6)
    c = counts or {}
    J.page_break(); J.head("Abstract", 1)
    for p in D["Abstract"]:
        m = re.match(r"^(Background|Methods|Results|Conclusions):\s*(.*)$", p, re.S); J.para(f"<b>{m.group(1)}:</b> {m.group(2)}")
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.para(f"<b>Counts:</b> text pages, {c.get('pages', '[P]')} (including title page, abstract, main text, references and figure legends); tables, 2; figures, 3; supporting files, 2 (Supporting Information and STROBE checklist). Total words (title page to tables), {c.get('words', '[W]')}.", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Materials and Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    J.head("Disclosure of Artificial Intelligence Use", 1); J.para(AI_STATEMENT)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s = f"{i}. " + ref(k); rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, table1())
    J.new_page("landscape"); put_table(J, table2(), fs=8)
    J.new_page("portrait"); J.head("Figure Legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>FIGURE {k}.</b> {FIGCAP[k]}", after=6)
    return J, rl, D

def docx_text(path):
    from docx import Document
    d = Document(path); t = [p.text for p in d.paragraphs]
    for tb in d.tables:
        for r in tb.rows: t.append(" ".join(dict.fromkeys(c.text for c in r.cells)))
    return "\n".join(t)
def total_words(path):   # 저널 계산: 표지·초록·본문·참고문헌·표 포함(그림 범례 제외)
    t = docx_text(path); i = t.find("\nFigure Legends\n"); body = t[:i] if i > 0 else t
    return len(body.split())
def main_words(path):
    t = docx_text(path); i = t.find("\nIntroduction\n"); j = t.find("\nDisclosure of Artificial Intelligence Use\n"); return len(t[i:j].split())
