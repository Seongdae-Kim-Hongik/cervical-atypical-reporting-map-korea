# Atypical-cell reporting and the district map of abnormal cervical screening results, Republic of Korea, 2011-2024

Analysis code for the manuscript

> Kim S. *Atypical-cell results dominate the district map of abnormal cervical screening results in Korea.* Submitted to *Journal of Medical Screening*.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24332247 (v1.0.0).

## Contents

This repository contains code only. The processed district-year data (master table, analytic panel, expected counts, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/CXAB/sets_CXAB_*.json`, `config_CXAB_std3.json`, `run_std3_chain.sh` | Covariates with expected directions, forced controls, negative controls, comparison outcomes and model settings (principal model `std3`; sensitivity versions with crude expected counts, without the share aged 80 or older, with the queen contiguity graph and for 2011-2023) |
| `04_분석/CXASC/`, `04_분석/CXHG/` | Settings for the component outcomes (atypical cells only; suspected precancer or cancer, 2018-2024) |
| `04_분석/CXAB/MS/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material, including `content_cxab.py`, which generates the Methods and Results text (the draft source of the Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Cervical cancer screening results by district (KOSIS DT_35007_N019) and by age (DT_35007_N020), and cancer screening target and examinee counts (DT_35007_N009, DT_35007_N010): National Health Insurance Service, fetched by `99R_next5d_fetch_cancerscreen.py` and `99X_cxab_fetch_national.py` (require a personal KOSIS API key in `~/.kosis_key`; the key is not included). District codes were joined by code and name together because two Busan districts carry swapped names across these tables (see `99X2_build_Estd3_cxab.py`).
- Female population by 5-year age group: Ministry of the Interior and Safety, resident registration statistics.
- District covariates: a harmonised public district panel, the Community Health Survey and Korean Statistical Information Service local indicators; invasive cervical cancer incidence from the national cancer registry district releases.

## Pipeline

Run from the repository root (set `ST_DATA_ROOT`, `ST_FBDZIP_CORRECTED` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database).

| Step | Script | Output |
|---|---|---|
| 0 | `99R_next5d_fetch_cancerscreen.py`, `99X_cxab_fetch_national.py`, `99R_next5d_cancerscreen_E.py` | District and national screening tables; district code crosswalk |
| 1 | `99X2_build_Estd3_cxab.py`, `99c_extra_canonical_pool_cxab.py`, `49D_cxab_national.py` | Age-standardised expected counts; district characteristics; national descriptive tables |
| 2 | `80_build_disease_panel_v.py CXAB` (`ST_VER=std3`) | Analytic panel |
| 3 | `49K_cxab_likelihood.R` | Likelihood comparison (Poisson, negative binomial, binomial, beta-binomial, observation-level effect) |
| 4 | `81_fit_inla.R CXAB` (`ST_VER=std3`, `ST_GRAPH=04_분석/CXAB/graph_593.graph`, `ST_THREADS=1`; see `04_분석/CXAB/run_std3_chain.sh`) | Principal model, set comparison, 200-subset multiverse, window models |
| 5 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `86b_ehsa_modified_mk.py`, `87_window_grid.py` | Maps, yearly smoothed ratios, persistence |
| 6 | `88g_sens_prep.py CXAB std3 GCA,TRANS`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` with `kh_constraints.R`, `89g_sens_combine.py` | Sensitivity analyses, comparison outcomes, Knorr-Held models |
| 7 | `99X3_cxab_validity.py`, `99X4_cxab_reader_posthoc.py`, `99X5_cxab_review_posthoc.py`, `49P_cxab_pa_reverse.R` | Post hoc analyses (cancer incidence correlations, atypical-to-higher-grade ratio, association opposite to the expected direction) |
| 8 | `04_분석/CXAB/MS/build/` (`build_refs_cxab.py`, `numbers_cxab.py`, `figs_cxab.py`, `ms_base_cxab.py`, `build_jms_cxab.py`, `esm_jms_cxab.py`, `cover_jms_cxab.py`) | Manuscript, supplementary material, figures |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
