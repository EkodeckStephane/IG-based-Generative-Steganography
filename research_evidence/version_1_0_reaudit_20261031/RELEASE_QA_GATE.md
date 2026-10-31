# DSP-D-26-02810 — Version 1.0 — independent re-audit gate (2026-10-31)

**Status: corrective work required before resubmission.** This file records verifiable manuscript/supplement consistency findings. It is not a new experimental result; the three submission documents remain unchanged by this audit.

## Confirmed checks

- Independently recompiled the three latest LaTeX sources twice: article 30 pages, reviewer response 8, cover letter 1. The extracted text of all three recompilations matches their delivered PDFs.
- Verified that Version 1.0 is indicated, that 155 TeX labels have no duplicates or dangling references, that 52 bibliography entries are cited, and that four embedded figure files exist.
- Confirmed S4 Gaussian exact-path convergence (L=1024 geometric relative error 0.0403053%), S5 current benchmark energy (Euclidean 7777.395, Fisher-preconditioned 8077.127), S6a 251/300 public decodes and 233/300 packing certificates, and S6b/S6c aggregate counts against CSV/JSON sources.
- Re-ran 7 existing S6 invariant tests successfully, plus S4's standalone randomized 200-path numerical test. These checks are not a fresh end-to-end rerun of all S6 training/detection runs.

## P0 items directly evidenced by bundled CSV files

1. **S2 standard deviation:** Manuscript `tab:s2` gives Euclidean iteration standard deviation 0.0. Source `data/s2_gradient_data.csv` has 50 Euclidean counts with mean 586.3 and population SD **41.6337603** (sample SD 42.0564489). Correct the table.
2. **S1 RK4 bound:** Manuscript `tab:s1` lists finite RK4 a-priori error bounds (1e-9 to 1e-8), but all four `rk4_error_bound` values in `data/s1_geodesic_data.csv` are **inf**. Recompute provable constants or present the *observed endpoint errors only*.
3. **S5 historical data ambiguity:** Bundled `data/s5_vae_results.csv` / `data/s5_vae_summary.json` report a 99.98%-style Fisher energy reduction (mean E_E=3071.9569, E_NG=1.1711), whereas the current manuscript and `results/benchmark_s5/full_benchmark.json` report energy E_E=7777.395, E_NG=8077.127 (Fisher energy 3.9% higher). These are potentially *distinct experiments*, but legacy files must be identified as such or excluded from submission supplements.
4. **S2-EXT capped convergence:** `data/s2_nondiagonal_data.csv`: successful final KL<1e-5 in **19/30 Euclidean** vs **28/30 natural-gradient** runs; **9/30 Euclidean** end with KL>1, up to 3.5e127. The table's mean capped iteration ratio is not a success-conditioned convergence speed. Report reliability and censoring.

## P1 manuscript/release issues

- Variable sectional-curvature Jacobi expansion in `thm:curvature_instability`: the remainder is normally **O(t^4)** when the curvature derivative along the path may be nonzero; O(t^5) needs further assumptions.
- Chernoff–Stein `eq:beta_exponent`: clarify the asymptotic o(n) term and do not imply an unproved finite-n bound.
- The S6 multiobjective table omits reported probability MSE and wall/CPU-time dimensions, even though these are present in `pareto_algorithm2_summary_earlystop.csv`. The supplementary S6 security–decoder figure is packaged but not included in the paper.
- The 17-entry submission archive omits the S6 checkpoint and data and includes an internal audit PDF. A 286-entry full archive carries S6 evidence; prepare a dedicated, clean supplementary submission package.
- The S6 README inside the project still states that results are *not incorporated into the three submission documents*, contrary to the current article's S6 section.
- Manuscript data-availability link `anonymous.4open.science/r/IG-based-Generative-Steganography-D255` could not be confirmed reachable by the auditor; check independently. Verify whether the journal requires a separate title page (not present in the short archive).
- 11 LaTeX overfull-box warnings remain, maximal logged 123.627pt at CAS maketitle, but visual inspection did not identify obvious text clipping. Metadata for all 52 bibliography records was not externally audited.

## Scope of review responses

The manuscript and the response/cover letter are materially aligned on core S4–S6 figures and state the conditional character of the R2.1/R2.2 guarantees and R2.3/R2.7 operational results. Neither the audit nor this note certifies editorial acceptance or full satisfaction of the initial reviewer requests.

**Reconciliation order:** S2 table → S1 RK4 claim → S5 supplement provenance → S2-EXT reliability/censoring → Jacobi/Stein mathematical wording → S6 cost/distortion and submission-supplement completeness → recompile and re-audit all three documents. 
