# V8 strong-steganalysis execution lock

Status: FROZEN AFTER V8 CODING CLOSURE, BEFORE STRONG-DETECTOR RESULTS.

This lock operationalizes the already frozen requirements in `protocols/OPERATIONAL_STC_STEGANALYSIS_PREREG_V8.md`. It does not change any payload, split, embedding design, or decision rule.

## Frozen external references

- SealWatch (SRM + FLD Ensemble), commit `90af7175a70f9c7cf48072b011334add499805db`.
- ConSeal (MiPOD / optional S-UNIWARD or HILL simulation), commit `dcb24caae710ca60ea8492028b3f6bad2c23afd3`.
- Official SiaStegNet, commit `592d9e13f39f287d9c675f1b89272bcfb6a9627c`.
- PyTorch SRNet reproduction (architecture only), `albblgb/Deep-Steganalysis` commit `1a5b8f88ce3c928e44ca22ad66010d23cd4a1262`.

SealWatch is selected because its SRM implementation has 34,671 dimensions and its FLD ensemble implementation is based on the DDE Matlab reference implementation. ConSeal is selected for the mandatory MiPOD baseline. SiaStegNet uses the official authors' repository. SRNet is explicitly labelled a public PyTorch reproduction rather than the original TensorFlow code.

## Data lock

- BOSSBase V4 split manifest is authoritative.
- Detector train side: 3,500 `fit` cover/stego pairs.
- Detector test side: 1,500 `calibration` cover/stego pairs.
- V4/V5 holdout remains excluded.
- Pair leakage is forbidden.
- For V8 methods, actual message bits are identical image-by-image between `uniform_shrink` and `IG_matched` at each epsilon.
- Failed V8 codewords remain in the coding report. Detector datasets may include only successfully materialized stegos; excluded failures must be listed explicitly and cannot be silently replaced.

## Conditions

Primary V8 matched-payload comparisons:
1. epsilon 2e-4, uniform_shrink;
2. epsilon 2e-4, IG_matched;
3. epsilon 8e-4, uniform_shrink;
4. epsilon 8e-4, IG_matched.

Baseline calibration:
- MiPOD at nearest actual image bpp to each V8 budget, computed from the frozen V8 aggregate: approximately 0.05217 bpp and 0.07060 bpp.
- S-UNIWARD may be added at the same rates but does not replace MiPOD.

## SRM + Ensemble

- Feature extractor: full spatial SRM, 34,671 dimensions.
- Classifier: SealWatch FLD ensemble with its automatic d_sub and L search.
- Primary seed: 12345.
- Primary metrics: balanced error Pe and ROC-AUC.
- Uncertainty: paired bootstrap over test image identities, 10,000 replicates, seed 20260910.
- Comparison is paired by image between uniform and IG at the same epsilon.

## Deep detectors

Detectors: SRNet and official SiaStegNet.

Seeds: 12345, 23456, 34567.

For every seed:
- same 3,500 fit pairs for training;
- same 1,500 calibration pairs for final testing;
- no test-driven checkpoint selection;
- deterministic D4 pair-preserving augmentation (horizontal/vertical flips and 90-degree rotations);
- cover and its stego receive identical augmentation;
- batch sampling remains pair-aware.

Checkpoint rule: lowest training objective at the end of a completed epoch among epochs fixed before test evaluation. The calibration/test labels are not used for model selection.

Report per seed:
- balanced error;
- ROC-AUC;
- accuracy;
- false-positive and false-negative rates;
- epoch/checkpoint;
- training wall time and hardware.

Headline deep comparison requires all three seeds. Mean, standard deviation and a 95% t-interval across seeds are reported.

## Decision

C6 can pass only when:
1. coding/raw provenance remains PASS;
2. SRM+EC is complete;
3. at least one deep reference has all three seeds;
4. claim/code/data audit passes;
5. any detector disadvantage of IG relative to uniform is retained and bounds the paper's wording.

Near-chance detector performance is not called perfect security.


## Pre-GPU reconciliation

For the final GPU campaign, `../protocols/V8_GPU_RECONCILIATION_ADDENDUM.md` is the authoritative resolution of the earlier seed/checkpoint inconsistencies. It was frozen before any strong-detector outcome and supersedes conflicting execution details in this file without changing the parent V8 scientific decision rule.
