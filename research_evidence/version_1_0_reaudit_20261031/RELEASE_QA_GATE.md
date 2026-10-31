# DSP-D-26-02810 — Version 1.0 — Corrected source-data reconciliation (31 October 2026)

**Pre-submission research audit:** Four P0 numerical/documentary issues were corrected in the supplied Version 1.0 LaTeX/PDF release. The corrective ZIP files are the authoritative deliverables for this iteration. **Important sync warning:** the current GitHub `Version_1.0/*.tex` paths still contain the older 4-priorities manuscript (no S6 section); their byte-for-byte synchronization with the corrected 31/8/1-page release is NOT yet confirmed. Do not treat the older GitHub manuscript source as the latest submission version until that sync is resolved.

## P0 correction matrix — independently verified
1. **S2 statistical dispersion:** 50 raw Euclidean iteration counts; mean **586.3**, population standard deviation **41.63376033941685**, published as **41.6** rather than erroneous 0.0. NG iteration count remains 1 for all 50 cases.
2. **S1 RK4:** `data/s1_geodesic_data.csv` has `rk4_error_bound=inf` for each of four tests. A finite a priori RK4 error bound was not established. The submission table removes that column and reports **observed endpoint shooting residuals** only (maximum **4.96e-13**); the numerical residual is not a global RK4 truncation-error certificate.
3. **S5 source provenance:** Archive-level older `data/s5_vae_results.csv` and `data/s5_vae_summary.json` are incompatible with current S5 and were segregated into a distinct INTERNAL_ONLY forensic archive. Editorial S5 evidence is exclusively `Version_1.0/results/benchmark_s5/full_benchmark.json` (Euclidean path energy **7777.395**, Fisher-preconditioned path energy **8077.127**, a **3.85%** increase in that protocol). Earlier numbers are not used as manuscript evidence.
4. **S2-EXT convergence censoring:** at final KL < 1e-5, Euclidean **19/30** successes, natural-gradient **28/30**; capped at 200 steps **11/30** and **2/30**; Euclidean final KL >1 in **9/30** trials and NG in **0/30**. The paired mean **2.0871** is a ratio of recorded, **censored** iteration counts, not a measured success-conditioned convergence-time speedup. The S2-EXT vector figure was redrawn from all 30 raw paired trials and marks censored trials separately.

## Additional scientific consistency
- Curvature Jacobi remainder relaxed to **O(t^4)** for variable curvature; the Stein exponent uses `log beta_n=-n D_KL+o(n)` at a fixed distribution pair before a local Fisher expansion, not a finite-n performance bound.
- S6 includes a supplementary table of probability-domain MSE and recorded optimizer time per codeword, checked against `pareto_algorithm2_summary_earlystop.csv`.
- The three corrected deliverable PDFs have **31 pages (article), 8 (reviewer response), 1 (cover)** and identify **Version 1.0**. Bibliography: 52 cited entries, no dangling LaTeX labels or unresolved citations.
- **42 machine checks passed, 0 failed**; 7 targeted S4/S6 scientific tests passed. The full model-training and steganalysis campaigns were NOT freshly regenerated in this release.
- The published external anonymized data URL could not be verified reachable; the corrected article references only the reproducibility data delivered as editorial supplements.
- The LaTeX build still emits 11 overfull warnings, including those associated with the CAS title, even though a visual check found no obvious text clipping.

## Version 1.0 artifact hashes — current corrected authoritative local ZIP
- Editorial three-document source+PDF ZIP: SHA-256 `493c919fff2cb603d49567e343720dbd1923f631aeaacc6f822e17fc66226e8a`.
- Complete submission/reproducibility ZIP: SHA-256 `83ebe802ce30ce467fcf52d26ba0b6116e3607f2edb51ad2715efa2ef46e7dde`.
- Internal deep-audit PDF: SHA-256 `fd98219d99b4d2d96f2bc5768b285a75af56c01f4645141cca2eaf951a59c46a`.
- Corrected local article LaTeX: SHA-256 `ca033d56965be41e9023a976534c4f3b207e2fb8c791c18cc3f7905bb80a157e`.
- Corrected local reviewer-response LaTeX: SHA-256 `1c780cb49db26d4be942524c7a50a6cf5e1f418b5e72312fc9501b9f04c43096`.
- Corrected local cover-letter LaTeX: SHA-256 `2452e60ad94dbb5c46057cfb4effd6600d7fe59e0c1b2ff0d891eeba10c27b63`.

## Pre-submission gate
The four P0 issues are closed **in the corrected release**. Remaining checks: verify journal-specific title-page/anonymization workflow, editorial platform supplements, and reconcile the public GitHub manuscript files with the authoritative ZIP. Do not claim universal security superiority or that all 52 external reference metadata have been independently validated.
