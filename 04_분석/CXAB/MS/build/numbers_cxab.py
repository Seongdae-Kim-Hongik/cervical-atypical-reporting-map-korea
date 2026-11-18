# numbers_cxab.py — CXAB(자궁경부암 검진 세포 이상 판정) 원고의 모든 수치를 결과 CSV에서 읽는다(2026-11-14, numbers_sknd.py 구조 이식). 손입력 금지, assert로 정합 확인.
import os, glob, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3"); DESC = os.path.join(B, "results_desc")
AN = os.path.dirname(B); ROOT = os.path.dirname(AN); PAN = os.path.join(ROOT, "02_패널")
rd = lambda f, d=RS, **k: pd.read_csv(os.path.join(d, f), encoding="utf-8-sig", **k)
DIV, SPH, FOR, SMK, UPT, CLI, GH, BLS, TE, WALK, MPA, FAC = ("crude_divorce_rate", "single_person_household_share", "foreign_residents_per_1000", "current_smoking_rate", "cervical_screening_uptake",
    "screening_clinic_share", "genhosp_per100k", "basic_livelihood_rate", "tertiary_educated_share", "walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k")
HYP = [DIV, SPH, FOR, SMK, UPT, CLI, GH, BLS, TE, WALK, MPA, FAC]; ROB = [DIV, FOR, MPA]; REV = [MPA]; PA = [WALK, MPA, FAC]
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
WIN = [("W1_2011-17", 2011, 2017), ("W2_2018-24", 2018, 2024)]
LOG1P = {FOR, GH}
def t4(r): return (float(r.IRR), float(r.lo), float(r.hi), bool(r.cred))
def load():
    N = {}
    P = pd.read_csv(os.path.join(B, "panel_CXAB_std3.csv")); N["n_rows"], N["n_districts"] = len(P), P.fbd_region.nunique(); assert (N["n_rows"], N["n_districts"]) == (3206, 229)
    N["cases_total"] = int(P.cases.sum()); N["exam_total"] = int(P.offset.sum()); assert N["cases_total"] == 1559162 and N["exam_total"] == 65685771
    N["zeros"] = int((P.cases == 0).sum()); assert N["zeros"] == 0
    Y = rd("S49D_national_year.csv", DESC).set_index("year"); N["nat"] = Y.to_dict("index")
    N["rate_range"] = (Y.rate_pct.min(), Y.rate_pct.max()); N["rate_peak_y"] = int(Y.rate_pct.idxmax())
    N["asc_share_pre"] = (Y.loc[2011:2017, "asc_share_pct"].min(), Y.loc[2011:2017, "asc_share_pct"].max()); N["asc_share_post"] = (Y.loc[2018:2024, "asc_share_pct"].min(), Y.loc[2018:2024, "asc_share_pct"].max())
    N["prec_n"] = (int(Y.loc[2018:, "precancer"].min()), int(Y.loc[2018:, "precancer"].max())); N["other_2017_2018"] = (int(Y.loc[2017, "other"]), int(Y.loc[2018, "other"]))
    A = rd("S49D_national_age.csv", DESC); g = A.groupby("C1_NM")[["abnormal", "examinees"]].sum(); g["r"] = 100 * g.abnormal / g.examinees; N["age_rate"] = g.r.to_dict()
    N["young_from"] = int(A[A.C1_NM.str.startswith("20")].year.min()); assert N["young_from"] == 2016
    E = pd.read_csv(os.path.join(PAN, "CXAB_Estd3.csv")); r = E.E_std / E.E_crude; N["e_ratio"] = (r.min(), r.max())
    N["rho_std_crude"] = float(E.SIR_std.corr(E.SIR_crude, method="spearman"))
    T1 = {}
    for wn, a, b in WIN + [("ALL", 2011, 2024)]:
        q = P[P.year.between(a, b)]; s = q.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        def raw(v):   # log1p 변환 변수는 원단위로 되돌려 기술(심사 지적: Table 1 단위)
            x = q[f"{v}_raw"]; return np.expm1(x) if v in LOG1P else x
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), exam=int(q.offset.sum()), rate=100 * q.cases.sum() / q.offset.sum(), p10=s.quantile(.1), med=s.median(), p90=s.quantile(.9),
                      cov={v: (raw(v).mean(), raw(v).std()) for v in HYP + FORCED})
    N["T1"] = T1
    L = rd("S49K_likelihood.csv").set_index("likelihood"); N["lik"] = L.to_dict("index")
    lk = rd("S1_likelihood.csv"); lk = lk[lk.set == "REF_forced_only"].set_index("family").WAIC; N["waic_pois"], N["waic_nb"] = lk["poisson"], lk["nbinomial"]
    s6m = rd("S6_moran_year.csv"); N["moran_year"] = (s6m.moran_I.min(), s6m.moran_I.max())
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]; N["moran_resid"], N["moran_resid_p"] = r8.loc["pearson_residual_area_mean", "moran_I"], r8.loc["pearson_residual_area_mean", "p_perm"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); N["s6"] = s6; N["rr_min"], N["rr_max"] = s6.RR.min(), s6.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum()); assert (N["n_hot"], N["n_cold"]) == (81, 74)
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict(); N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall"] = pe.kendall_W.to_dict()
    vp = rd("S42_variance_partition.csv").set_index("component"); N["vp"] = vp.share_of_linear_predictor_var.to_dict()
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role"]].to_dict("index")
    assert set(m3.index[m3.role == "hypothesis"]) == set(HYP); N["cred_hyp"] = sorted(v for v in HYP if N["main"][v]["cred"]); assert set(N["cred_hyp"]) == set(ROB)
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index"); assert set(s7.index[s7.robust]) == set(ROB); N["mv_total"] = int(s7.n_specs_total.iloc[0])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = {v: t4(r) for v, r in nc.iterrows()}; N["negctl_cred"] = sorted(v for v, t in N["negctl"].items() if t[3]); assert N["negctl_cred"] == ["traffic_culture_index"]
    wi = rd("S4_window_IRR.csv"); N["win"] = {(r.cov, r.window): t4(r) for r in wi.itertuples()}
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv"))]); N["s43"] = {(r.analysis, r.cov): t4(r) for r in S43.itertuples()}; N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): t4(r) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): t4(r) for r in S41.itertuples()}
    ALT = sorted({a for a in S41.analysis.unique() if not a.startswith(("F1_", "F2_", "G2_", "H1_", "bw_"))}); N["alt"] = ALT
    N["ret"] = {v: (sum(1 for a in ALT if N["s41"].get((a, v), (1, 1, 1, False))[3] and (N["s41"][(a, v)][0] > 1) == (N["main"][v]["IRR"] > 1)), sum(1 for a in ALT if (a, v) in N["s41"])) for v in ROB}
    N["bw"] = {r.cov: t4(r) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): t4(r) for r in S41[S41.analysis.str.startswith("H1_nco_")].itertuples()}
    N["drop_sido"] = {v: (sum(1 for a in S41.analysis.unique() if a.startswith("F1_") and N["s41"].get((a, v), (1, 1, 1, False))[3]), sum(1 for a in S41.analysis.unique() if a.startswith("F1_"))) for v in ROB}
    N["drop_year"] = {v: (sum(1 for a in S41.analysis.unique() if a.startswith("F2_") and N["s41"].get((a, v), (1, 1, 1, False))[3]), sum(1 for a in S41.analysis.unique() if a.startswith("F2_"))) for v in ROB}
    ev = lambda rr: rr + np.sqrt(rr * (rr - 1)) if rr >= 1 else 1 / rr + np.sqrt(1 / rr * (1 / rr - 1))
    N["evalue"] = {v: (ev(N["main"][v]["IRR"]), ev(N["main"][v]["lo"]) if N["main"][v]["lo"] > 1 else 1.0) for v in ROB}
    N["sens"] = {}
    for v in ("s577", "s2", "s8", "t23"):
        m = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")).set_index("cov"); N["sens"][v] = {c: t4(m.loc[c]) for c in m.index}
    for T in ("CXASC", "CXHG"):
        m = pd.read_csv(os.path.join(AN, T, "results_std3", "S3_main_IRR.csv")).set_index("cov"); N["sens"][T] = {c: t4(m.loc[c]) for c in m.index}
    o = rd("S10_offset_sensitivity_IRR.csv").set_index("cov"); N["sens"]["E_pop"] = {c: t4(o.loc[c]) for c in o.index}
    p = rd("S49P_pa_reverse.csv"); N["pa_alone"] = {(r.model, r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in p.itertuples()}
    v = rd("S49V_validity_cancer_incidence.csv"); N["valid"] = {(r.cancer_period_value, r.outcome, r.sir_years): (r.spearman, r.p) for r in v.itertuples()}
    q = rd("S49R_reader_posthoc.csv"); N["reader"] = {r.quantity: (r.value, r.p) for r in q.itertuples()}
    d = rd("S49R_district_ratio.csv"); N["ratio_q"] = (d.asc_hg_ratio.min(), d.asc_hg_ratio.quantile(.1), d.asc_hg_ratio.median(), d.asc_hg_ratio.quantile(.9), d.asc_hg_ratio.max())
    cv = rd("S5_covid.csv"); N["covid_main"] = t4(cv[cv.term == "post_main"].iloc[0])
    eb = rd("S12c_yearly_EB_SIR.csv"); g = eb.groupby("year").ebSIR; gap = pd.DataFrame({"p10": g.quantile(.1), "p90": g.quantile(.9)}); gap["ratio"] = gap.p90 / gap.p10; N["gap"] = gap.to_dict("index")
    x = rd("S49X_review_posthoc.csv").set_index("analysis"); N["rev"] = x.to_dict("index")
    N["e_lo"] = {v: N["evalue"][v][1] for v in ROB}
    return N
if __name__ == "__main__":
    N = load()
    for k in ("rate_range", "asc_share_pre", "asc_share_post", "prec_n", "other_2017_2018", "e_ratio", "phi", "moran_year", "ratio_q", "covid_main"): print(k, N[k])
    print("hot", N["hot_by_sido"]); print("cold", N["cold_by_sido"]); print("kendall", N["kendall"]); print("ret", N["ret"], len(N["alt"])); print("ev", N["evalue"])
    print("drop", N["drop_sido"], N["drop_year"]); print("age", {k: round(v, 2) for k, v in N["age_rate"].items()}); print("vp", N["vp"]); print({k: N["s43_waic"][k] for k in sorted(N["s43_waic"]) if k.startswith("KH")})
    print("Epop", {c: N["sens"]["E_pop"][c] for c in ROB}); print(N["moran_pooled"], N["moran_resid"], N["waic_nb"], N["waic_pois"])
