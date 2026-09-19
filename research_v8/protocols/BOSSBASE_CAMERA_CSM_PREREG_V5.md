# BOSSBase V5 — Camera-aware cover-source mismatch preregistration

Status: FROZEN BEFORE V5 CAMERA-SPECIFIC ANALYSIS.
Date: 2026-09-10.

## Purpose
V5 tests cover-source mismatch across acquisition sources after V4A found positive but sub-threshold within-source dispersion. V4A keeps its original outcome.

## Frozen partition and camera groups
Reuse the V4 split: 3,500 fit, 1,500 calibration, 5,000 holdout. Camera groups are fixed before pixel analysis: Canon-10MP (EOS 40D+400D), Canon EOS 7D, Canon Rebel XSi, Pentax K20D, Nikon D70 and Leica M9.

## Retained embedding/source objects
Carrier lattice, predictor, eligibility rule, eight context strata, exact discrete Cachin orientation D(P_C||P_S), and ternary +/-1 embedding family remain fixed.

## Fit-only camera tangent
For each source, estimate the 8-vector of log-scale shifts relative to the global fit source. Fisher-whitened weighted PCA is performed about the frozen global-source origin. Choose the smallest K explaining >=90% weighted between-source variance with 2<=K<=4. The mapped basis is orthonormal in the frozen Fisher metric.

## Calibration-only radius
Within each camera group, form consecutive 50-image calibration blocks by frozen rank. Project each block into the fit-derived nuisance basis. Set r_cam to the empirical 95th percentile of Fisher norms. Nuisance adequacy requires median normalized orthogonal residual <=0.35 and Q90<=0.60.

## Robust risk and certification
Use deterministic scrambled Sobol directions on the K-dimensional Fisher sphere: 4,096 primary, 32,768 independent certification directions, escalating to 131,072 if relative discrepancy exceeds 5e-4.

## Iso-Cachin sample and decision
For each epsilon in {2e-4,8e-4}, generate 128 new positive eight-dimensional directions with frozen independent seeds and project to exact nominal KL. At r_cam define J=R_robust/epsilon and D80=Q90(J)-Q10(J). Materiality requires positive D80 for both budgets and D80>=0.05 for at least one. Design consequence compares nominal exact optimization, uniform safety shrinkage and K-mode robust optimization. Robust designs must be independently certified and non-scalar (relative residual >1e-3).

PASS TO HOLDOUT requires nuisance adequacy, materiality, certified feasibility and non-scalar allocations for both budgets.
