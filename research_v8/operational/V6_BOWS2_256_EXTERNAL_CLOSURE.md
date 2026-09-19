# V6 BOWS2 256×256 External Validation — Closure

**Decision: IN-MANIFOLD EXTERNAL PASS**  
Execution date: 2026-09-19.

The supplied BOWS2 split archive was reunified and qualified before V6 pixel-statistic analysis. The reunified archive SHA-256 is `5e017969c09e8e1ed98205ce2155e96ffa56dbfe056693075726c3b0b0f3b316`. It contains exactly 10,000 PGM images; all are native `P5`, 256×256, 8-bit (`maxval=255`). No duplicate image SHA-256 was observed.

The protocol deviation from the earlier 512×512 expectation is governed by `V6_BOWS2_256_PREANALYSIS_ADDENDUM.md` (commit `61c68346570c3309b865846c2171f9cd14e62cb7`). No V6 fit, stratum threshold, predictor, support, smoothing rule, Fisher basis, radius, budget, candidate, or decision threshold was changed. The only implementation change was to apply the same 3×3 center lattice to the native 256×256 grid.

## Geometry transfer

- eligible residuals: 71,504,626;
- projected Fisher-shape norm: 0.1019049285;
- frozen radius: 0.2375032471;
- normalized orthogonal residual: 0.3840314971;
- diagnostic threshold: 0.60;
- stratum-mass TV mismatch: 0.1150650551.

Thus the external source remains inside the frozen V6 shape manifold under the predeclared diagnostics.

## Frozen-candidate external risks

At `epsilon=2e-4`:
- uniform-shrink direct BOWS2 risk ratio: 0.2218717293;
- V6 robust direct BOWS2 risk ratio: 0.1380995519.

At `epsilon=8e-4`:
- uniform-shrink direct BOWS2 risk ratio: 0.3738860005;
- V6 robust direct BOWS2 risk ratio: 0.3358477634.

The robust candidate remains below the security budget for both frozen budgets without BOWS2-driven rescaling or reoptimization.

## External iso-Cachin differentiation

For the 128 frozen designs per budget:
- `epsilon=2e-4`: D80 = 0.3814692611;
- `epsilon=8e-4`: D80 = 0.4078454864.

Both are positive and both exceed the frozen materiality threshold 0.05.

## Persisted evidence

- compact summary: `results/V6_BOWS2_256_EXTERNAL_SUMMARY.json`;
- detailed retained metrics: `results/V6_BOWS2_256_EXTERNAL_RESULTS.json`;
- full local-result SHA-256: `45e04f86bebb9a369f7c0ff8b8d5273ff5a065409979a9266cd1e52253737384`;
- compact-summary SHA-256 from the execution workspace: `b0dbbe4f9909b19b152551be49b8fea60049a7e5a74166b8509db345570210c9`;
- patched 256×256 replay-runner SHA-256: `5156e9b6512a00662f96df10aed72da6aa3cae7e21b6ffb4e719e1f090b10e4b`.

This closes the external-transfer requirement for V6. It does not by itself close the separate detector-facing strong-steganalysis requirement.
