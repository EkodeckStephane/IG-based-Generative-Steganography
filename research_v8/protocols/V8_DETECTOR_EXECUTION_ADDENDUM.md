# V8 Detector Execution Addendum — frozen before strong-detector outcomes

**Status: FROZEN before SRM+EC / deep-detector scores are observed.**  
**Parent protocol:** `research_v8/protocols/OPERATIONAL_STC_STEGANALYSIS_PREREG_V8.md`

## Purpose

This addendum resolves execution details that were not fully specified in the parent V8 preregistration. It does not change the frozen V8 embedding designs, actual payloads, BOSSBase fit/calibration partition, detector families, or the hard C6 decision rule.

## Reference SRM implementation

Tier A uses the official DDE/Binghamton Linux implementation of the full Spatial Rich Model (SRM v1.1), downloaded from the DDE feature-extractor page. The extractor produces the 106 SRM submodels whose concatenated dimension is 34,671.

The default extractor settings are retained:
- residual truncation `T=2`;
- co-occurrence order `4`;
- default SPAM merge and symmetry settings;
- no LSB erasure;
- no parity-residual option.

The same executable and settings are used for cover and every stego condition.

## Image population and ordering

The canonical V4 split manifest is filtered to `fit` and `calibration`, then sorted exactly as the V8 STC campaign:
`split, rank_hash, image`.

This yields 3,500 fit and 1,500 calibration images. The V4/V5 holdout is never used for detector training, validation, checkpoint selection, or final testing.

## Handling of the three STC failures

The coding failures remain part of the operational record and are never relabeled as successful stegos.

For detector-facing method comparisons, the **primary matched analysis** at a given epsilon uses the intersection of images for which both `uniform_shrink` and `IG_matched` produced valid exactly recoverable codewords. Thus:
- epsilon 2e-4: all 5,000 non-holdout images;
- epsilon 8e-4: the common-success set excludes the union of the three retained failures.

A secondary sensitivity analysis may report detector scores with every generated image-condition output included, but it cannot replace the primary operational analysis.

For MiPOD, the primary comparison is restricted to the same image identities used in the corresponding common-success V8 analysis so that test populations are identical.

## Deep-learning train/validation/test separation

The frozen `calibration` split is detector test only and is never used for model or checkpoint selection.

Within the frozen `fit` split, a deterministic validation subset is formed before detector outcomes:
1. compute SHA-256 of `V8-DET-VAL|<filename>`;
2. sort fit filenames by the resulting hexadecimal digest, then by filename;
3. assign the first 500 eligible common-success fit images to validation;
4. use the remaining fit images for training.

For epsilon 2e-4 this produces 3,000 training + 500 validation images. For epsilon 8e-4 the same rule is applied after the common-success restriction.

Cover and corresponding stego always remain in the same side.

## Fixed deep seeds

The three required headline training seeds are:

`20260910, 20260911, 20260912`.

They control initialization, data shuffling, and stochastic augmentation where supported. No seed may be discarded because of an unfavorable score.

## Checkpoint rule

For each architecture, epsilon, method, and seed:
- training hyperparameters are fixed before calibration/test evaluation;
- the selected checkpoint is the epoch with the highest validation balanced accuracy;
- ties are broken by lower validation loss, then by the earlier epoch;
- the 1,500-image calibration split is evaluated only after checkpoint selection.

If an official implementation exposes only ordinary accuracy during validation, the execution wrapper additionally computes balanced accuracy from the same frozen validation predictions.

## Deep architecture policy

- **SRNet:** use the DDE/reference SRNet implementation or a source-faithful port whose architecture is verified against the reference before outcome use.
- **SiaStegNet:** use the official `SiaStg/SiaStegNet` implementation. Its SRM kernel bank must come from the official repository; it must not be silently replaced.
- At least three seeds are required for any deep result used to close C6.

A reduced epoch count, reduced image resolution, substitute network, or CPU-only pilot may be reported as engineering/profiling evidence, but cannot close the deep-detector requirement unless separately frozen and scientifically justified before final test evaluation.

## MiPOD baseline

MiPOD is generated with the public/reference implementation from `conseal`.

For each image and V8 epsilon, the MiPOD payload is matched to the actual V8 message length:

`alpha_i = message_bits_i / (512*512)`.

The payload is therefore matched image-by-image rather than only in expectation. The random seed is deterministic from SHA-256(`V8-MiPOD|epsilon|filename`). No payload is altered after detector outcomes.

## Classical EC and uncertainty

SRM vectors are concatenated in a fixed lexicographic submodel-name order. The Ensemble Classifier uses a public/reference implementation with its parameters recorded in the execution artifact.

Classical test uncertainty is estimated by paired bootstrap over cover/stego image identities with a fixed bootstrap seed and at least 2,000 resamples. ROC-AUC and balanced error are reported jointly.

## Hard interpretation rule

A detector result near chance is not called perfect security. A statistically meaningful detectability disadvantage of IG relative to uniform shrinkage is retained as negative evidence and must narrow the claims.

C6 can pass only under the original parent rule: operational message recovery, matched-payload SRM+EC, at least one repeated-seed deep reference, claim/code/data consistency, and transparent treatment of any disadvantage.
