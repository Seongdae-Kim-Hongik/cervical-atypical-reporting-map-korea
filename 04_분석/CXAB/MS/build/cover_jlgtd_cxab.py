# cover_jlgtd_cxab.py — CXAB JLGTD 커버레터(2026-11-18). 규정 항목: 전체 제목, 미출판·타지 미심사 진술, 중요성·독자 관련성, IRB 승인(방법 절과 일치). 1쪽, 비인칭, 수신 Editor-in-Chief(현 편집장 확인 불가 → 직함만).
#  자료 중복 고지 금지(저자 결정), 제외 심사자는 포털 칸에만. IRB 번호 포함. Zenodo 공개 DOI만. --draft면 DOI 자리표시자 허용.
import os, re, sys, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_cxab as C
from build_jlgtd_cxab import TITLE as DTITLE, ZENODO, GITHUB, ADDRESS
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out_jlgtd"); DRAFT = "--draft" in sys.argv
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount.txt")).read().split())
if not DRAFT: assert ZENODO.startswith("10.5281/zenodo."), "공개 DOI 없음(투고 전 게이트)"
RQ = N["ratio_q"]; T1 = N["T1"]
_d = datetime.date.today(); cl = [f"{_d:%B} {_d.day}, {_d.year}", "The Editor-in-Chief", "Journal of Lower Genital Tract Disease", "",
      "Dear Editor-in-Chief,",
      f"Please find enclosed the manuscript entitled \"{DTITLE}\" by Seongdae Kim, for consideration as Original Research in the Journal of Lower Genital Tract Disease. The manuscript has not been published and is not under consideration for publication in any other journal.",
      f"The proportion of screened women with an abnormal cervical cytology result is often read as a marker of underlying risk, yet it also reflects how smears are reported. This study examines how far each explanation is compatible with the geography of abnormal results across a whole national program, covering all {N['exam_total']:,} screening examinations and {N['cases_total']:,} abnormal results of the Korean National Cancer Screening Program in the {N['n_districts']} districts of the Republic of Korea over 2011–2024. "
      f"Abnormal results followed a stable map dominated by atypical-cell results, and district characteristics, including proxies of human papillomavirus exposure, accounted for little of it. In post hoc analyses, the variance of the district atypical share was {N['rev']['asc_share_dispersion_ratio']['value']:.1f} times that expected by chance, and the ratio of atypical results to suspected precancer or cancer clustered in space and was not correlated with the exposure proxies.",
      "The work speaks to the journal's mission of improving the prevention of HPV-related disease. For colposcopists, cytopathologists and screening program managers among its readers, it shows that the composition of abnormal results, not only their rate, varies geographically within a single program, and it indicates what linking results to reading laboratories would allow programs to monitor. "
      "The study used only published aggregate statistics; the Institutional Review Board of Hongik University approved it (7002340-202511-HR-012) and its continuing review (7002340-202611-HR-040) and waived informed consent. The approval notices, with an English translation, are uploaded as a separate file.",
      f"The text contains {int(W['text']):,} words (limit 3,000), with a précis of {W['precis']} words, a structured abstract of {W['abstract']} words, 2 tables, 3 color figures and {W['refs']} references. Supplemental Digital Content and the completed STROBE checklist are provided. The analysis code is openly available on GitHub ({GITHUB}) and archived on Zenodo (https://doi.org/{ZENODO}).",
      "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript, reviewed and edited all output, and takes full responsibility for the content. No third-party writing assistance was received.",
      "Thank you for considering this manuscript.", "", "Sincerely,", "",
      "Seongdae Kim, PhD (corresponding author)", ADDRESS, "Email: kimsd@hongik.ac.kr"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
gap = False
for t in cl:
    if t == "": gap = True; continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_letter.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_cxab_cl_jlgtd", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and re.search(r"7002340-?\s*202611-?\s*HR-040", txt) and not re.search(r"(?i)funding|competing|overlap|previously submitted|token|private link", txt), "문체·IRB·금지 항목"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages, "draft" if DRAFT else "")
