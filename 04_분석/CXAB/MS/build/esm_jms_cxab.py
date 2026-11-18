# esm_jms_cxab.py — CXAB Journal of Medical Screening Supplementary material(Supporting Methods·Table S1-S4) + STROBE 체크리스트 단독 파일(2026-11-18).
#  수치는 결과 CSV에서만. 미국 철자, 표 제목 쌍점 금지, 사후 분석은 post hoc 표기.
import os, re, subprocess, pandas as pd
import content_cxab as C
from ms_base_cxab import LABEL, GROUPS, TX, foot_row
from build_jms_cxab import TITLE as DTITLE
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out_jms"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
N = C.N
st = lambda t: f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})" + ("" if t[3] else "")
J = TX(cite="bracket")
def TF(title, header, rows, foot="", fs=8, land=False, port=False):
    J.new_page("landscape") if land else (J.new_page("portrait") if port else J.page_break()); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplementary material</b>"); J.para(f"Supplementary material for the manuscript entitled \"{DTITLE}\"")
J.para("Contents. Supporting Methods; Table S1 (district characteristics); Table S2 (likelihood comparison); Table S3 (rate ratios across alternative specifications); Table S4 (national screening results by category and year).")
J.head("Supporting Methods", 1)
SM = [
 ("Joining districts across tables", "District screening results (Korean Statistical Information Service table DT_35007_N019) were joined to the district frame through a crosswalk from the table's district classification codes to administrative codes. In the published results tables (DT_35007_N017 and DT_35007_N019) the codes for 2 districts in Busan (Gangseo-gu and Yeonje-gu) carry each other's names relative to the coverage table (DT_35007_N009), while the values follow the names. Joining by code and name together assigned all 28 district-years correctly; joining by code alone would have swapped them. General-ward rows of cities with wards were summed to the city, Sejong (published only as a province header row) was included in all 14 years, with Yeongi-gun as Sejong in 2011, and Gunwi-gun was assigned to Daegu. District totals equaled the national totals in every year. Cells published as '-' (suspected cancer and known cancer in small districts) were zero, which the equality of district and national totals confirmed."),
 ("Expected counts", f"National abnormal rates by year and 14 age groups came from DT_35007_N020. District results are not published by age, so the age structure of each district's screened women was estimated as the resident female population by 5-year age group multiplied by the national screening coverage for that age group and year (national examinees by age divided by the national female population by age), rescaled so that the estimated total equaled the observed number of women screened in the district. The rescaling factor ranged from 0.47 to 1.29. Women aged 20-29 years entered the program in 2016, so their coverage was zero before then. Expected counts were rescaled within each year so that their national sum equaled the observed sum. A crude expected count (examinees multiplied by the national abnormal rate) and a female-population expected count were used as sensitivity analyses."),
 ("Category change in 2018", f"In 2018 the program introduced the category 'suspected precancerous lesion'; in the same year the 'other' category fell from {N['other_2017_2018'][0]:,} to {N['other_2017_2018'][1]:,} women while atypical-cell results changed little. Because expected counts use the national rate for each year, a level shift common to all districts is absorbed by the expected counts. Analyses were repeated for 2011-2017 and 2018-2024 separately and for 2011-2023, and the higher-grade component was analyzed for 2018-2024 only."),
 ("District characteristics", "Covariates came from the series district panel (Statistics Korea, Korea Community Health Survey age-standardized rates and administrative statistics). The basic livelihood security recipient rate had implausible values for 2021-2023 in 11 cities with general wards (33 district-years), which were set to missing and interpolated within district. The single-person household share is published from 2015; earlier years took the district mean. Remaining gaps were filled by within-district linear interpolation, then the district mean, then the national year mean (Table S1)."),
 ("Model specification", "log(μ_it) = log(E_it) + α + Σ_k β_k x_kit + b_i + γ_t + δ_t, with y_it ~ negative binomial(μ_it, size θ). The district effect b_i followed the Besag-York-Mollié 2 model on the 593-edge contact graph of the 229 districts (islands linked to the nearest mainland district), with a penalized-complexity prior on its precision (P[σ > 0.5] = 0.01) and on the mixing parameter φ (P[φ < 0.5] = 2/3); γ_t was a scaled first-order random walk and δ_t an independent year effect, both with penalized-complexity precision priors (P[σ > 0.5] = 0.01). Coefficients β_k for standardized characteristics had normal priors with mean 0 and precision 4; the intercept had precision 0.001. Models were fitted with INLA 25.10.19 in R 4.6.0 with 1 thread. The 200 random-subset models each included every characteristic independently with probability 0.5 (seed 20261019), with the 5 forced controls always included. Between-district and within-district components were the district mean of each standardized characteristic and the yearly deviation from it. In the between-within model the 3 activity measures were kept undecomposed."),
 ("Post hoc analyses", "These analyses were added after the principal results were seen. (1) Spearman correlations between district SIRs (all years, and the 5 years around each registry release) and the age-standardized incidence of invasive cervical cancer published by the national cancer registry in its 2013 and 2018 district releases. (2) The district ratio of atypical-cell results to suspected precancer or cancer results summed over 2018-2024, its Moran I (593-edge contact graph, 499 permutations) and its Spearman correlations with SIRs and district characteristics. (3) For moderate-or-higher physical activity, which was associated opposite to the expected direction, negative binomial models with the same random effects including physical activity alone with the forced controls, and all characteristics except the other 2 activity measures."),
]
for h, t in SM: J.head(h, 2); J.para(t)
M = pd.read_csv(os.path.join(B, "panel_META_CXAB_std3.csv"), encoding="utf-8-sig").set_index("variable")
SRC = {"crude_divorce_rate": "Statistics Korea, vital statistics", "single_person_household_share": "Statistics Korea, census-based household statistics", "foreign_residents_per_1000": "Ministry of the Interior and Safety, local foreign residents",
       "current_smoking_rate": "Korea Community Health Survey (age-standardized)", "cervical_screening_uptake": "National Health Insurance Service, cancer screening (DT_35007_N009)", "screening_clinic_share": "National Health Insurance Service, screening institutions",
       "genhosp_per100k": "Health Insurance Review and Assessment Service, institutions", "basic_livelihood_rate": "Ministry of Health and Welfare", "tertiary_educated_share": "Statistics Korea, census",
       "walking_practice_rate": "Korea Community Health Survey (age-standardized)", "moderate_pa_rate": "Korea Community Health Survey (age-standardized)", "public_sports_facilities_per_100k": "Ministry of Culture, Sports and Tourism",
       "urban_population_share": "Ministry of Land, urban planning statistics", "physicians_per_1000": "Statistics Korea, regional indicators", "sex_ratio": "Resident registration", "fiscal_independence": "Ministry of the Interior and Safety, local finance", "pop80_share": "Resident registration",
       "hit_and_run_rate": "Korean National Police Agency", "traffic_culture_index": "Korea Transportation Safety Authority", "fires_per_10000": "National Fire Agency"}
rows = []
for g, vs in GROUPS + [("Negative control exposures", ["hit_and_run_rate", "traffic_culture_index", "fires_per_10000"])]:
    rows.append(["__H__", g])
    for v in vs:
        m = M.loc[v]; imp = int(m.n_imputed_interp + m.n_imputed_sgg_mean + m.n_imputed_year_mean)
        if v == "basic_livelihood_rate": imp += 33   # 99c 단계에서 결측 처리·보간한 2021-23 일반구 시 33칸(Supporting Methods)
        rows.append([f"  {LABEL.get(v, m.label_en)}", SRC[v], f"{int(m.obs_year_min)}–{int(m.obs_year_max)}", str(imp), f"{m.vif_final:.1f}" if pd.notna(m.vif_final) else "—"])
TF("Table S1. District Characteristics, Sources, Observed Years, Imputed District-Years and Variance Inflation Factors", ["Characteristic (expected direction)", "Source", "Observed years", "Imputed district-years", "VIF"], rows, land=True, fs=7, foot=
   ("VIF, variance inflation factor in the principal model. Expected directions were stated before fitting the full model. All characteristics were standardized to mean 0 and SD 1."))
L = pd.read_csv(os.path.join(RS, "S49K_likelihood.csv"))
NM = {"poisson": "Poisson", "nbinomial": "Negative binomial", "binomial": "Binomial (trials = women screened)", "betabinomial": "Beta-binomial", "poisson+obs_iid": "Poisson with observation-level effect"}
TF("Table S2. Likelihood Comparison With the Forced Controls and the Same Random Effects", ["Likelihood", "WAIC", "DIC", "−Σ log CPO", "CPO failures"],
   [[NM[r.likelihood], f"{r.WAIC:,.1f}", f"{r.DIC:,.1f}", f"{r.neg_logscore:,.1f}", str(int(r.cpo_fail))] for r in L.itertuples()],
   "CPO, conditional predictive ordinate; DIC, deviance information criterion; WAIC, widely applicable information criterion. No district-year had zero abnormal results, so zero-inflated likelihoods were not fitted; binomial likelihoods used the logit of the age-standardized expected proportion as an offset. The principal model used the negative binomial likelihood by the prespecified rule (lower WAIC than Poisson).", port=True)
ROB = [C.DIV, C.FOR, C.MPA]
ANA = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"], N["main"][v]["cred"]))]
for a, lab in [("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"), ("iid_only", "Independent district effect only"), ("no_spatial", "No district effect")]:
    ANA.append((lab, (lambda a: lambda v: N["s43"].get((a, v)))(a)))
for a in N["alt"]:
    ANA.append((a.replace("_", " "), (lambda a: lambda v: N["s41"].get((a, v)))(a)))
for s, lab in [("t23", "2011–2023 only"), ("s8", "Crude expected counts"), ("E_pop", "Female-population expected counts"), ("s2", "Share aged ≥80 y omitted"), ("s577", "Queen adjacency graph (577 edges)"), ("CXASC", "Atypical cells only"), ("CXHG", "Suspected precancer or cancer, 2018–2024")]:
    ANA.append((lab, (lambda s: lambda v: N["sens"][s].get(v))(s)))
for w, lab in [("W1_2011-17", "2011–2017"), ("W2_2018-24", "2018–2024")]:
    ANA.append((lab, (lambda w: lambda v: N["win"].get((v, w)))(w)))
for comp, lab in [("__between", "Between-district component"), ("__within", "Within-district component")]:
    ANA.append((lab, (lambda comp: lambda v: N["bw"].get(v + comp) or N["bw"].get(v))(comp)))
for o, lab in [("TRANS", "Transport-injury deaths (comparison outcome)"), ("GCA", "Gastric cancer patients (comparison outcome)")]:
    ANA.append((lab, (lambda o: lambda v: N["nco"].get((o, v)))(o)))
rows = []
for lab, f in ANA:
    vals = [f(v) for v in ROB]
    if all(x is None for x in vals): continue
    rows.append([lab] + [st(x) + ("ᵃ" if x[3] else "") if x is not None else "—" for x in vals])
TF("Table S3. Rate Ratios per 1 SD for the 3 Robust Characteristics Across Alternative Specifications", ["Specification", "Crude divorce rate", "Foreign residents", "Moderate-or-higher physical activity"], rows,
   "Values are rate ratios (95% credible intervals). ᵃCredible interval excludes 1. Alternative fits (codes): B, smoothing of forced controls; C1, Poisson-lognormal; C2, second-order random walk for year; C3, first-order autoregressive year effect; C4, province-by-year random effect; D1, Spatial+-type adjustment for spatial confounding; E0, start year shifted; E1-E2, covariates lagged 1-2 years; F3, extreme values winsorized; G1, 3-year moving averages of survey covariates; H4, even or odd years only.", fs=7, land=True)
Y = pd.read_csv(os.path.join(B, "results_desc", "S49D_national_year.csv"), encoding="utf-8-sig")
rows4 = [[str(int(r.year)), f"{int(r.examinees):,}", f"{int(r.asc):,}", f"{int(r.precancer):,}" if r.year >= 2018 else "—", f"{int(r.cancer_susp):,}", f"{int(r.abnormal):,} ({r.rate_pct:.2f})", f"{r.asc_share_pct:.1f}", f"{int(r.other):,}"] for r in Y.itertuples()]
assert int(Y.abnormal.sum()) == N["cases_total"] and int(Y.examinees.sum()) == N["exam_total"]
TF("Table S4. National Cervical Screening Results by Category and Year, 2011–2024", ["Year", "Examinations", "Atypical cells", "Suspected precancerous lesion", "Suspected cancer", "Abnormal, No. (%)", "Atypical share of abnormal, %", "Other"], rows4, land=True, fs=8, foot=
   ("Abnormal = atypical cells + suspected precancerous lesion + suspected cancer, the study outcome; national totals equal the sums of the district counts. The suspected precancerous lesion category was introduced in 2018 (— before 2018), when the 'other' category fell. Counts of negative and reactive or infectious results are not shown."))
ps = os.path.join(OUT, "Supplementary_material.docx"); J.doc_title = "Supplementary material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_cxab_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps), len(rows), "spec rows")
MH = [x[0] for x in C.METHODS]; RH = [x[0] for x in C.RESULTS]
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"),
      ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}"), ("Participants", "6", f"Methods, {MH[0]}; {MH[1]} (all women screened; ecological)"),
      ("Variables", "7", f"Methods, {MH[1]}; {MH[2]}; Table S1"), ("Data sources/measurement", "8", "Methods; Supporting Methods"),
      ("Bias", "9", f"Methods, {MH[3]}; Table S3"), ("Study size", "10", f"Methods, {MH[0]} (all 229 districts)"), ("Quantitative variables", "11", f"Methods, {MH[2]}"),
      ("Statistical methods", "12", f"Methods, {MH[3]}; Supporting Methods; Table S2"), ("Participants (flow)", "13", "Not applicable (aggregate district data; no exclusions)"),
      ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]}; Table 1; Figure 1"),
      ("Main results", "16", f"Results, {RH[1]}; {RH[2]}; Table 2; Figures 2–3"), ("Other analyses", "17", f"Results, {RH[3]}; {RH[4]}; Tables S2–S4"),
      ("Key results", "18", "Discussion, first paragraph"), ("Limitations", "19", "Discussion, Limitations"), ("Interpretation", "20", "Discussion"), ("Generalizability", "21", "Discussion; Conclusions"),
      ("Other information (funding, code)", "22", "Statements and Declarations (Funding; Data availability)")]
K = TX(cite="bracket"); K.para("<b>STROBE checklist</b>"); K.para(f"Manuscript \"{DTITLE}\"")
K.table_fit("STROBE Checklist for This Ecological Study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9, title_bold=True)
foot_row(K, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology. Section names refer to the main manuscript and the Supplementary material.", 8, 12)
pk = os.path.join(OUT, "STROBE_checklist.docx"); K.doc_title = "STROBE checklist"; K.save(pk)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_cxab_esm", "--convert-to", "pdf", "--outdir", OUT, pk], check=True, capture_output=True)
print("saved", os.path.basename(pk))
