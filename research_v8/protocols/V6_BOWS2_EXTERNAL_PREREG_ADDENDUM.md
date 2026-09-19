# V6 BOWS2 External Confirmation — Locked Addendum

**Status: FROZEN BEFORE ANY BOWS2 PIXEL IS AVAILABLE TO THIS RUNTIME.**
Date: 2026-09-10.

This addendum operationalizes the external-validation paragraph already frozen in `BOSSBASE_V6_PMF_GEOMETRY_PREREG.md`. It does not change any V6 fit, calibration, design, security budget, smoothing rule, nuisance basis, radius, allocation seed, or certified candidate.

## Frozen V6 objects
Use without refitting:
- 8 BOSSBase-fit context strata and their integer `cut_vnum` thresholds;
- center lattice and 4-neighbor predictor used in V4–V6;
- residual support {-255,...,255};
- Jeffreys alpha = 0.5;
- frozen BOSSBase PMFs `p0`, stratum weights `w0`, Fisher basis `V/H`, K=3;
- `r_shape = 0.2375032471006036`;
- epsilons `{2e-4, 8e-4}`;
- the already-frozen 128 iso-Cachin design vectors per epsilon;
- final 131072-certified uniform-shrink and V6-robust beta vectors.

## Corpus integrity
Primary target is the original public BOWS2 grayscale PGM corpus: exactly 10,000 decodable 512x512 8-bit grayscale images. Files are sorted deterministically by numeric filename stem when possible, otherwise lexicographically. No image may be excluded for its V6 statistics. Decode failures, duplicate byte hashes, dimensions, and header/format anomalies must be reported.

## Frozen feature extraction
No resizing or enhancement is allowed for the original 512x512 PGM corpus. Use the same non-overlapping 3x3 center lattice, eligibility rule `0 < center < 255`, context statistic, frozen 8-stratum assignment, four-neighbor rounded predictor, and integer residual used in BOSSBase V4–V6.

## External empirical distribution
For each stratum g, accumulate residual counts n_gk. Define the external PMF using the same Jeffreys smoothing:
`p_ext,g(k) = (n_gk + 0.5)/(n_g + 0.5*511)`.
Also define the actual external stratum mass `w_ext,g = n_g / sum_h n_h`.

Direct external Cachin risk is the joint-distribution risk
`C_ext(beta) = sum_g w_ext,g D_KL(p_ext,g || q_ext,g,beta_g)`.
This intentionally uses `w_ext`, because a true external-source test must not silently replace BOWS2 stratum frequencies by BOSSBase frequencies. For comparability, the frozen-w0 risk may be reported secondarily, clearly labeled.

## Frozen V6 geometry transfer diagnostic
Construct the centered log-ratio shape score relative to frozen BOSSBase `p0`, whiten with frozen `sqrt(w0 p0)`, and project on frozen V6 basis V:
- `delta_ext = V^T z_ext`;
- projected norm `||delta_ext||`;
- full whitened score norm `||z_ext||`;
- normalized orthogonal residual `||z_ext - V delta_ext|| / ||z_ext||`.
Report whether `||delta_ext|| <= r_shape`.
The calibration adequacy threshold 0.60 for normalized orthogonal residual is reused only as a diagnostic; it is not relaxed after BOWS2 is read.
Also report `0.5 * ||w_ext-w0||_1` as stratum-mass TV mismatch, which is outside the current shape-only nuisance manifold.

## Frozen candidates
For each epsilon and for each final 131072-certified candidate (`uniform_shrink`, `robust`), report:
- beta vector;
- frozen BOSSBase ideal rate;
- BOWS2 realized ideal rate using `w_ext`;
- direct empirical `C_ext(beta)` and ratio to epsilon;
- secondary empirical risk using frozen `w0`.
No BOWS2-driven rescaling or reoptimization is allowed.

## Frozen iso-Cachin external heterogeneity
For each of the already-frozen 128 V6 nominal iso-Cachin designs at each epsilon, evaluate direct BOWS2 `C_ext`. Let `J_i=C_ext(beta_i)/epsilon`; report min, Q10, median, Q90, max, and `D80=Q90-Q10`. The materiality threshold remains `D80 >= 0.05` for at least one epsilon, with positive D80 for both.

## Decision vocabulary
- **IN-MANIFOLD EXTERNAL PASS**: projected norm <= r_shape, normalized orthogonal residual <= 0.60, robust direct empirical risk <= epsilon for both budgets, and external D80 criterion passes.
- **OUT-OF-MANIFOLD / PHENOMENON CONFIRMED**: geometry transfer is outside the declared shape manifold, but the external D80 criterion passes. Candidate risks are descriptive and cannot be interpreted as violations of an in-manifold theorem.
- **IN-MANIFOLD SECURITY NOT CONFIRMED**: geometry transfer is in-manifold but one or both fixed robust candidates exceed epsilon. No repair/retest on BOWS2 is permitted.
- **EXTERNAL PHENOMENON NOT CONFIRMED**: D80 criterion fails.

## Prohibited post-hoc actions
No adjustment of alpha, support, strata, predictor, V/H, K, r_shape, epsilon, beta vectors, design vectors, risk orientation, weighting rule, or success thresholds after any BOWS2 pixel is read.