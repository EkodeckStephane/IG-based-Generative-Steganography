# BOSSBase Natural-Image Witness — preregistration V4

Status: FROZEN BEFORE HOLDOUT PIXEL ANALYSIS.
Date: 2026-09-10.

## Goal
Test whether the iso-Cachin robustness heterogeneity confirmed in controlled/discrete families remains present when source parameters and embedding strata are estimated from natural BOSSBase 1.01 images, without holdout use for model construction, uncertainty calibration or tuning.

## Frozen data split and carrier
The validated 10,000-image 512x512 8-bit PGM corpus is split from filenames using SHA-256 ranking: 3,500 fit, 1,500 calibration, 5,000 final holdout. Carrier centers use a stride-3 lattice with one-pixel margin; 0/255 centers are excluded. The residual is center minus the rounded arithmetic mean of N/S/W/E neighbors, which are never carrier centers. A +/-1 center change therefore translates the residual exactly by +/-1.

## Frozen 8-stratum source model
Context scale is computed from the eight surrounding pixels independently of the center value. Seven octile cutpoints are learned on fit only and then frozen. Each stratum uses an exact discrete residual model; empirical fit diagnostics are reported before progression.

## Nuisance calibration
The two nuisance coordinates are global log-scale shift and texture-dependent log-scale shift. Calibration images form deterministic blocks; projected Fisher norms set the empirical 95th-percentile radius r*. Holdout cannot alter the radius.

## Primary budgets/designs
epsilon in {2e-4,8e-4}. For each budget, 128 independent positive allocation directions are projected onto exact nominal Cachin risk. Robust inflation is evaluated at 0.5 r*, r*, 1.5 r*. The exact robust optimizer is compared with uniform safety shrinkage.

## Pre-holdout success criterion
Progression requires: source-fit diagnostic pass; finite positive r*; D80=Q90-Q10 >=0.05 at r* for at least one budget and positive for both; certified robust feasibility; and a non-scalar robust allocation. Diagnostic radii cannot replace r* after observation.

The experiment retains all deviations and failures. A model redesign after a failed pre-holdout criterion is registered as a new stage before further holdout use.
