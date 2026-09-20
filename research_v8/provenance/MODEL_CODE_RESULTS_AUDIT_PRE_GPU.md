# Model -> Code -> Results alignment audit

**Branch audited:** `cachin-ig-robust-v8`  
**Audit stage:** pre-GPU strong steganalysis  
**Rule:** no empirical claim is considered closed unless the model object, execution code, raw/retained evidence, aggregate, and manuscript wording can be connected without an unexplained transformation.

## Executive decision

The formal/design/coding chain is scientifically coherent, but final submission readiness remains blocked by strong steganalysis. The audit also identified and repaired provenance defects that would otherwise weaken reproducibility: the original V7 design JSON was absent from Git history, V4A's runner lived only in the Library, historical V6/V7 bundles were outside the repository, and the preliminary strong-detector scripts contained contradictory checkpoint rules and an incorrect mean-payload MiPOD helper.

After the repairs described in the pre-GPU reconciliation addendum, the strong-steganalysis campaign has one canonical protocol. Detector results have not yet been observed, so the reconciliation is prospective rather than outcome-driven.

## Alignment matrix

| Layer | Model / scientific object | Canonical code/evidence | Result status | Audit status |
|---|---|---|---|---|
| Formal core | `C(p,theta)=D_KL(p || T_theta(p))`; Fisher--Rao source ball; source-gradient sensitivity; nominal-boundary separation theorem | `formal/FORMAL_CORE_V1.md`; `src/image_witness_core.py`; `src/discrete_witness_core.py`; tests | analytic + numerical sanity evidence | PASS for bounded formal claims |
| Controlled witness / V3 | exact nominal Cachin boundary, finite-radius robust risk, iso-Cachin dispersion | prereg + retained `iso_cachin_confirmatory_v3_summary.json`; witness core functions | confirmatory summary retained | SCIENTIFIC ALIGNMENT PASS; one-command historical driver not currently retained |
| BOSSBase V4A | within-source radius and frozen materiality rule | `bossbase_v4a_closure_summary.json`; exact Library runner restored as provenance artifact | `r*=0.0379528`, D80 below 0.05; pivot retained | PASS after runner restoration; negative result correctly retained |
| V5 diagnostic | camera/log-scale nuisance diagnostic | retained protocol/closure statements | low-budget empirical mismatch retained | PASS as boundary/diagnostic claim; historical execution packaging is less complete than V8 |
| V6 PMF Fisher geometry | empirical residual-PMF Fisher modes; K=3; `r_shape`; robust optimizer; independent 131072-direction certification | V6 model/arrays/candidate/certification artifacts; historical external bundle retained | D80 0.481655/0.530772; rate gains 2.8849%/16.5025%; risk reductions 6.7272%/38.1360% | PASS for model-level claims |
| BOWS2 external | frozen V6 objects evaluated on independent native BOWS2 source | addendum + external runner bundle + `V6_BOWS2_256_EXTERNAL_RESULTS/SUMMARY` | IN-MANIFOLD EXTERNAL PASS | PASS |
| V7 screening | stochastic image-domain realization at matched ideal payload; 346-D screening only | original V7 package, original design SHA `a95f...`, retained screening result | AUCs near 0.5; GO TO STC | PASS as development screen only; exact screening driver is not independently retained as a standalone current script |
| V8 coding | actual-message STC at 90% of frozen ideal rate; exact decode criterion | vendored pySTC source, V8 runner, 20 raw blocks, clean-rerun manifest, restored original design | 5000/5000, 5000/5000, 4998/5000, 4999/5000 | PASS |
| Strong steganalysis | DDE-SRM+FLD, SRNet, SiaStegNet, MiPOD calibration at matched actual payload | pre-GPU reconciliation + canonical Colab scripts | no headline GPU detector outcomes yet | OPEN pending campaign |
| Manuscript | claims must be bounded by above evidence | `paper/main.tex` | V6/V7/V8 numeric tables align with retained summaries; BOWS2 result and strong-detector results are not yet integrated in final Results/Conclusion | NOT FINAL |

## Numerical cross-checks already satisfied

### V7 table

The manuscript values are consistent with `v7_operational_screening_results.json`:

- epsilon 2e-4, uniform: ideal bpp 0.058046, change/eligible 0.107950, AUC 0.505022;
- epsilon 2e-4, IG: 0.058046, 0.114292, 0.502361;
- epsilon 8e-4, uniform: 0.078550, 0.157984, 0.508172;
- epsilon 8e-4, IG: 0.078550, 0.168414, 0.502589.

### V8 table

The manuscript values are consistent with `V8_STC_RERUN_SUMMARY.json`:

- low budget: 5000/5000 for both methods, all-bit BER 0, mean message bpp 0.0521699936;
- high budget: uniform 4998/5000, BER 8.811685e-5; IG 4999/5000, BER 5.106109e-5; mean message bpp 0.0705995300 for both.

The paired change-fraction and PSNR differences in the manuscript also match the retained summary.

### V6 table

The manuscript values agree with the frozen V6 closure for D80, robust/uniform ideal rates, percentage rate gain, same-payload worst-risk reduction, and non-scalar residual.

### BOWS2

The independent BOWS2 summary and detailed result agree on decision, corpus qualification, Fisher-shape diagnostics, direct empirical risk ratios, and external iso-Cachin D80. No BOWS2-driven re-fit or re-scaling is present in the closure record.

## Repaired pre-GPU defects

1. **Conflicting deep seeds / checkpoint rules.** Reconciled prospectively. Final seeds: 12345, 23456, 34567. Checkpoint selection: deterministic internal validation from `fit`; `calibration` is test-only.
2. **MiPOD payload mismatch.** The earlier standalone helper used a global mean bpp. Canonical code now matches `message_bits_i/(512*512)` image-by-image and uses the frozen `V8-MiPOD|epsilon|filename` seed rule.
3. **Checkpoint overwriting.** Canonical names include model, epsilon, method, and seed; latest and best checkpoints are distinct and resumable.
4. **Missing original V7 design file.** Restored from the 2026-09-10 frozen operational package. Its SHA-256 is `a95f764bf7a92e21e3203aecb44c99b14a881f40f2bba6a221fb895d03a2d33b`, matching the design hash stored in V7 results.
5. **Historical provenance outside Git.** The exact V4A runner and the historical V6/V7 ZIP packages are retained under a provenance/reproduction area instead of relying only on the Library.
6. **Classical detector implementation ambiguity.** Final Tier A uses the official DDE Linux SRM executable (106 submodels, 34,671 dimensions) for feature extraction and the pinned SealWatch FLD Ensemble for classification. The pure-Python SealWatch SRM helper is not the canonical Tier-A extraction path.

## Remaining issues that are intentionally not papered over

- The exact historical V3 generator is not currently a standalone repository script. The model core, preregistration and retained confirmatory outputs exist, so the current claim is evidence-backed but not yet a perfect one-command archival replay.
- V7's exact standalone screening driver is not present in the retained operational ZIP; the frozen protocol, selected-image artifact, design file and complete results are retained. V7 is development-only and cannot close C6.
- The final manuscript has not yet incorporated the completed BOWS2 external result as a Results item, and strong detector outcomes do not yet exist. The manuscript must not be frozen until the GPU campaign is audited.

## Required final closure after Colab return

1. verify campaign manifest/hashes and exact code commit;
2. verify all 12 mandatory SRNet V8 runs (or another preregistered deep detector with all three seeds) and all SRM+EC conditions;
3. retain every adverse detector result and interrupted seed;
4. run paired identity-level uncertainty analysis and across-seed intervals;
5. update C6 only from those verified artifacts;
6. rewrite detector-facing Results/Discussion/Limitations and integrate BOWS2;
7. re-run claim -> code -> raw result -> aggregate -> manuscript audit;
8. only then execute Gate 10 and the final Senior Reviewer Q1/Rang A prescreen.