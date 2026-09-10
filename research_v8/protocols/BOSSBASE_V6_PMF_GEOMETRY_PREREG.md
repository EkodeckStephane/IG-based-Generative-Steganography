# V6 — Empirical-PMF Fisher geometry repair preregistration

**Status: FROZEN AFTER V5 BOSSBASE HOLDOUT DIAGNOSTIC AND BEFORE ANY V6 CAMERA-PMF FIT/CALIBRATION ANALYSIS OR ANY BOWS2 PIXEL READ.**
Date: 2026-09-10.

## Why V6 exists
V5 confirmed the iso-Cachin phenomenon on untouched BOSSBase holdout but the low-budget robust design exceeded the exact empirical-PMF Cachin budget on Canon-10MP. Post-holdout diagnosis localized most excess to mid-texture strata where empirical PMF shape differs from the moment-matched discrete Gaussian. V6 is therefore a declared post-holdout model repair. The V5 holdout is contaminated for V6 and will never be reused as V6 confirmatory evidence.

## Scientific change
The embedding family, exact Cachin orientation, carrier lattice, predictor, eligibility rule and 8 frozen V4 context strata remain unchanged. Only the nuisance/source manifold changes: from eight log-scale perturbations of discrete Gaussians to a low-dimensional Fisher tangent model of the **full residual PMF shape** in each stratum.

## Data allowed for V6 construction
- BOSSBase V4 `fit` split (3500 images): learn the global empirical PMFs and inter-camera shape directions.
- BOSSBase V4 `calibration` split (1500 images): calibrate nuisance radius only.
- BOSSBase V4 `holdout`: forbidden for V6 model selection, calibration, optimization and confirmation.
- BOWS2 original 10000 grayscale 512x512 PGM images: reserved as the independent external confirmation source; no BOWS2 pixel may be read before the V6 pre-external gate passes.

## PMF definition and fixed smoothing
For each frozen stratum g and residual k in {-255,...,255}, let n_gk be the count. Use Jeffreys smoothing alpha=0.5 in every bin:
`p_g(k) = (n_gk + 0.5)/(n_g + 0.5*511)`.
No support trimming, tail deletion or adaptive bin merging is allowed after observing V6 results.

## Fisher tangent representation
Let p0_g be the globally fitted BOSSBase-fit empirical PMF and w_g its frozen stratum frequency. For a source PMF p_s,g define the centered log-ratio score
`h_s,g(k)=log(p_s,g(k)/p0_g(k)) - E_{p0_g}[log(p_s,g/p0_g)]`.
Define its Fisher-whitened coordinate
`z_s,gk = sqrt(w_g p0_g(k)) h_s,g(k)`.
Then `||z_s||_2^2` is the Fisher quadratic norm of the shape score at the global source.

Using the six V5 camera groups on the BOSSBase fit split, perform origin-centered camera-weighted SVD of z_s. Select the smallest K explaining >=90% of weighted inter-camera Fisher energy, constrained to 2 <= K <= 5. No mean subtraction is applied because every z_s is already a displacement from the frozen global source.

Let V_j be the selected orthonormal directions in whitened coordinates. Define score basis functions
`H_j,gk = V_j,gk / sqrt(w_g p0_g(k))`.
Numerically recenter each H_j within each stratum under p0_g only to remove roundoff, then re-orthonormalize once under the frozen Fisher inner product before any calibration result is inspected.

## Exponential shape manifold
For nuisance coordinate delta in R^K define
`p_g(k|delta) = p0_g(k) exp(sum_j delta_j H_j,gk) / Z_g(delta)`.
This preserves positivity and normalization. At delta=0 the Fisher metric in the orthonormal nuisance coordinates is the identity.

## Calibration radius
For each V5 camera group in the BOSSBase calibration split, order images by the frozen rank_hash and form consecutive complete 50-image blocks. Estimate each block PMF with the same alpha=0.5 smoothing, form its Fisher-whitened centered log-ratio z, project `delta=V^T z`, and compute normalized orthogonal residual.

Set `r_shape` to the empirical 95th percentile (linear interpolation) of block `||delta||_2` values. Diagnostic adequacy requires median normalized residual <=0.35 and Q90 <=0.60. Failure means V6 nuisance geometry is inadequate; do not increase K or tune smoothing after observing calibration results.

## Exact risk on the V6 manifold
For each delta, construct p(delta) exactly by the exponential tilt above. Under stratum embedding probability beta_g, construct
`q_g(k)=(1-2 beta_g)p_g(k)+beta_g p_g(k-1)+beta_g p_g(k+1)`
with zero extension beyond residual support. Compute exact `D_KL(p(delta)||q(delta,beta))`, weighted by the frozen global stratum frequencies.

## V6 pre-external tests
Epsilons remain `{2e-4,8e-4}`. Generate N=128 new positive 8-D allocation directions using PCG64 seeds 20261311 and 20261411, components `exp(N(0,0.9^2))`, max-normalized, then scalar-project each onto exact nominal `D_KL(p0||q_beta)=epsilon`, beta<=0.2.

At r_shape define J=worst_manifold_risk/epsilon and D80=Q90(J)-Q10(J). Materiality passes if D80>0 for both epsilons and D80>=0.05 for at least one. Threshold unchanged from V4/V5.

For each epsilon compare the exact nominal optimizer, uniform safety shrinkage, and V6 robust optimizer. Robust candidate must be non-scalar relative to nominal with weighted residual >1e-3 and pass independent risk certification. Primary nuisance search uses 4096 deterministic Sobol sphere directions + center. Certification uses a distinct 32768-direction Sobol sphere and escalates to 131072 if relative discrepancy exceeds 5e-4.

## Pre-external decision
- PASS TO EXTERNAL: calibration diagnostic passes + materiality passes + both robust candidates are independently certified and non-scalar.
- FAIL / MODEL REDESIGN: any of those conditions fails.

## External confirmation source and rules
Only after PASS TO EXTERNAL, acquire the original BOWS2 grayscale PGM corpus from the public reproducible-signal-processing distribution. Do not use BOWS2 for tuning. Process it with the frozen BOSS predictor, lattice, strata, p0, score basis, r_shape and candidate beta vectors.

External reporting must include direct empirical-PMF Cachin risks of the fixed candidates and iso-Cachin D80 for the already-frozen V6 designs. No BOWS2-driven reoptimization is permitted. A BOWS2 empirical risk excess must be reported as such; it cannot be repaired and retested on the same BOWS2 corpus.

No threshold, alpha, K rule, basis construction, radius quantile, epsilon, allocation seed, Sobol seed or success criterion may change after V6 fit/calibration PMF results are observed.
