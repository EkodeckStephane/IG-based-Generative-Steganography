# Iso-Cachin Frontier Confirmatory Study — preregistration V3

Status: FROZEN BEFORE V3 EXECUTION.
Date: 2026-09-10.
Purpose: independently confirm that embedding designs with the same exact nominal Cachin security budget can have materially different robustness to bounded cover-source mismatch under the Fisher–Rao nuisance geometry.

## 1. Fixed source profiles
Use exactly the four 8-stratum profiles frozen in CONTROLLED_GRID_PREREG_V1.md: P1 balanced-moderate, P2 smooth-heavy, P3 texture-heavy, P4 bimodal. The discrete Gaussian PMF model and discrete source Fisher metric from CONTROLLED_GRID_DISCRETE_PREREG_V2.md are mandatory.

## 2. Nominal Cachin budgets
Primary budgets: epsilon in {2e-4, 8e-4} nat/residual.

## 3. Source-mismatch radii
Evaluate r in {0.04, 0.08, 0.12} under the same 2D nuisance model and Fisher metric as V2.

## 4. Independent frontier designs
For each (profile, epsilon), generate N=128 designs using NumPy PCG64 seed 20260910 plus a deterministic profile/budget offset. Each raw direction has eight positive components sampled as exp(N(0,0.9^2)), normalized by its maximum. For each direction d, solve a scalar lambda so beta=lambda*d satisfies exact discrete nominal Cachin risk C(beta)=epsilon, with beta_g <=0.2. Rejection depends only on nominal feasibility.

## 5. Robust evaluation
For each accepted design and radius, compute worst-case exact discrete Cachin risk over the Fisher–Rao nuisance set. Primary numerical grid: 720 boundary directions plus nominal center. Certification recomputes every 10th design and Q10/median/Q90/min/max neighborhood designs using 2880 boundary directions and radial levels {0,0.25,0.5,0.75,1}. Any 720-vs-2880 relative discrepancy >5e-4 triggers full affected-cell recomputation.

Define inflation J_r(beta)=R_r(beta)/epsilon.

## 6. Primary confirmatory estimands
For each (profile,epsilon,r): Q10, median, Q90 of J_r and D80=Q90-Q10. At r=0.12 also report S80=Q90/Q10. Bootstrap uncertainty: 10,000 nonparametric resamples of the 128 designs within each cell.

## 7. Predeclared decision rules
Validity:
V1. |C(beta)-epsilon| <= max(1e-10,1e-6*epsilon).
V2. Certified robust risk never falls below nominal risk beyond 1e-8 tolerance.
V3. Angular certification follows the rule above.

Confirmation:
H1. At r=0.12, D80>=0.08 in at least 6/8 profile-budget cells.
H2. At r=0.12, S80>=1.05 in at least 6/8 cells.
H3. Across-cell median D80 at r=0.12 >=0.10.
H4. In at least 6/8 cells, bootstrap 95% CI lower bound for D80 >0.05.
H5. For every profile-budget cell, median J_r is nondecreasing over r={0.04,0.08,0.12}.

Decision: CONFIRMED if V1-V3 and H1-H5 all pass; PARTIALLY CONFIRMED if V1-V3 pass and at least three H-criteria pass; otherwise NOT CONFIRMED.

## 8. Interpretation boundary
The confirmatory target is the distinction between nominal Cachin security and bounded source robustness inside the declared model. Cross-corpus and detector-facing validation are handled in later frozen stages.
