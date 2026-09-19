# Claim–Evidence Matrix — V6/V8

| ID | Candidate claim | Required evidence | Current evidence | Status |
|---|---|---|---|---|
| C1 | The framework preserves Cachin's exact endpoint epsilon-security. | Exact definition/proof with correct KL orientation. | Formal core defines C(theta)=D_KL(P_C||P_theta), S_epsilon={C<=epsilon}; perfect-security recovery proved. | PASS |
| C2 | Filler–Fridrich steganographic Fisher information is recovered as a local/tangent limit under their assumptions. | Second-order KL expansion plus assumption mapping. | Formal derivation d(beta)=1/2 beta^2 g(v,v)+O(beta^3); MI-specific equivalence explicitly bounded to Filler–Fridrich assumptions. | PASS, wording bounded |
| C3 | Designs with the same nominal Cachin epsilon can have materially different robustness under bounded source variation. | Confirmatory iso-Cachin experiment with fixed thresholds, then independent-source transfer. | V6 BOSSBase D80=0.4817/0.5308; untouched BOWS2-256 external D80=0.3815/0.4078, both above 0.05. | PASS, model + external |
| C4 | The additional geometry is actionable for embedding design rather than merely descriptive. | Same embedding family/budget; robust optimizer vs uniform safety shrink; independent certification; non-scalar reallocation. | V6 gains +2.8849% and +16.5025%; non-scalar residuals 0.1598/0.1438; 131072-direction certification < epsilon. | PASS IN MANIFOLD |
| C5 | The frozen V6 source-robust construction transfers to an independent natural-image corpus without tuning. | BOWS2 untouched before frozen protocol; fixed candidates/designs; direct empirical-PMF risk; no retuning. | BOWS2 supplied as 10,000 native P5 256×256 images; pre-analysis resolution addendum frozen; geometry remains in-manifold (projected norm 0.10190 < 0.23750; normalized orthogonal residual 0.3840 < 0.60); robust direct risk ratios 0.1381 and 0.3358; external D80 0.3815 and 0.4078. | PASS |
| C6 | The resulting stegosystem is operationally secure against contemporary steganalysis at controlled payload. | Actual coding plus matched payload; SRM/SRNet-or-stronger; repeated splits/seeds; uncertainty; traceable raw evidence. | Aggregate V8 STC summary reports 20,000 encodings with 100%, 100%, 99.96%, 99.98% recovery across the four conditions, but only the 0–1500 raw block range is currently persisted on the canonical branch. Strong steganalysis remains separate. | OPEN — CODING SUMMARY POSITIVE, RAW PROVENANCE + STRONG DETECTOR PENDING |
| C7 | The method improves effective payload generally. | Broad multi-source evidence at matched robust risk and actual coding. | Gains are regime dependent; V4A is a negative/materiality boundary, while V6 gives +2.9%/+16.5% in the calibrated manifold. | REJECT GENERAL CLAIM; use bounded claim |

## Mandatory negative/boundary evidence

V4A materiality FAIL and the V5 empirical low-budget violation remain in the scientific record. They delimit narrower nuisance models and motivate the PMF-shape V6 repair. The BOWS2 pass does not erase those boundary results.

## External-evidence anchors

- `protocols/V6_BOWS2_256_PREANALYSIS_ADDENDUM.md`
- `operational/V6_BOWS2_256_EXTERNAL_CLOSURE.md`
- `results/V6_BOWS2_256_EXTERNAL_SUMMARY.json`
- `results/V6_BOWS2_256_EXTERNAL_RESULTS.json`
