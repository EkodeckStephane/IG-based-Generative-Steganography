# V8 strong-steganalysis pre-GPU reconciliation addendum

**Status: FROZEN before any strong-detector outcome is observed.**

This addendum reconciles execution details that were specified inconsistently by `protocols/V8_DETECTOR_EXECUTION_ADDENDUM.md` and `steganalysis/V8_STRONG_STEGANALYSIS_LOCK.md`. It changes no embedding design, message, payload, BOSSBase split, detector family, baseline family, or hard C6 decision rule.

## 1. Authority and scope

The parent scientific preregistration remains `protocols/OPERATIONAL_STC_STEGANALYSIS_PREREG_V8.md`. The two later execution documents were both written before strong-detector outcomes but disagree on deep seeds and checkpoint selection. Because no strong-detector outcome has yet been used, this reconciliation is fixed prospectively and becomes the single operational authority for the GPU campaign.

## 2. Data and matched populations

The V4 manifest is authoritative.

- `fit`: 3500 image identities.
- `calibration`: 1500 image identities.
- holdout: excluded from detector fitting, validation, checkpoint selection, and final detector testing.

For each epsilon, primary detector analysis uses the common-success intersection of `uniform_shrink` and `IG_matched` actual-message STC outputs.

- epsilon 2e-4: 5000 non-holdout identities.
- epsilon 8e-4: exclude the union of the three retained V8 coding-failure identities (`6353.pgm`, `6606.pgm`, `9002.pgm`).

MiPOD is restricted to the same identities for the corresponding epsilon.

## 3. Deep train / validation / test rule

`calibration` is test-only.

Within the eligible `fit` identities, compute SHA-256 of `V8-DET-VAL|<filename>`, sort by digest then filename, and assign the first 500 identities to validation. All remaining eligible `fit` identities are training.

Therefore:

- epsilon 2e-4: 3000 train, 500 validation, 1500 test;
- epsilon 8e-4: 2998 train, 500 validation, 1499 test, because two failure-union identities are in `fit` and one is in `calibration`.

Cover and all stego derivatives of an identity always remain on the same side.

## 4. Deep seeds

The final headline seeds are the three seeds from the later dependency/execution lock:

`12345, 23456, 34567`.

No seed may be dropped because of an unfavorable result.

## 5. Checkpoint selection

For every `(architecture, epsilon, method, seed)`:

1. epoch count and optimization hyperparameters are fixed before final test evaluation;
2. evaluate only the internal validation set after each completed epoch;
3. select the checkpoint with highest validation balanced accuracy;
4. break ties by lower validation loss, then earlier epoch;
5. evaluate the frozen `calibration` test split exactly once after checkpoint selection.

The former `minimum training objective` rule is superseded by this rule because the earlier addendum had already reserved an internal validation split and the rule is less prone to overfitting than training-loss selection.

## 6. Architectures and fixed hyperparameters

### SRNet

Architecture: pinned public PyTorch reproduction `albblgb/Deep-Steganalysis@1a5b8f88ce3c928e44ca22ad66010d23cd4a1262`, `models/SRNet.py`, adapted only to one-channel 512x512 BOSSBase input.

- epochs: 100;
- optimizer: Adam;
- learning rate: 2e-4;
- weight decay: 1e-5;
- scheduler: StepLR(step_size=30, gamma=0.5);
- pair batch: 4 (8 images after cover/stego concatenation);
- input: native grayscale 512x512, divided by 255 as in the campaign wrapper;
- pair-preserving D4 augmentation during training only.

### SiaStegNet

Architecture: official `SiaStg/SiaStegNet@592d9e13f39f287d9c675f1b89272bcfb6a9627c`, including its official `SRM_Kernels.npy`.

- epochs: 500;
- optimizer: Adamax;
- learning rate: 1e-3;
- eps: 1e-8;
- weight decay: 1e-4;
- CE + 0.1 * ContrastiveLoss(margin=1.0);
- scheduler: MultiStepLR(milestones=[300,400], gamma=0.1);
- pair batch: 16 (campaign adaptation; official script default is 32 images per batch, but this fixed pair batch was chosen before outcomes to fit common Colab GPUs);
- input: native grayscale 512x512 values without 1/255 normalization, matching the official data path;
- pair-preserving D4 augmentation during training only.

Reduced resolution, reduced epochs, seed dropping, test-driven early stopping, or substitute architectures cannot close C6.

## 7. Classical Tier A

Full DDE Spatial Rich Model, 34,671 dimensions / 106 submodels, from the official Linux package `SRM_linux_make_v1.1.tar`, followed by the pinned SealWatch FLD Ensemble implementation at commit `90af7175a70f9c7cf48072b011334add499805db`.

- classifier seed: 12345;
- automatic `d_sub` and ensemble-size search;
- paired bootstrap: 10,000 identity resamples, seed 20260910;
- report balanced error, ROC-AUC, FPR, FNR, and paired IG-minus-uniform differences.

## 8. MiPOD baseline

Pinned ConSeal commit: `dcb24caae710ca60ea8492028b3f6bad2c23afd3`.

For every image, MiPOD payload is the exact actual V8 message length for that image:

`alpha_i = message_bits_i / (512*512)`.

The deterministic seed is SHA-256(`V8-MiPOD|epsilon|filename`) reduced to 32 bits. A global mean bpp must not replace this image-specific payload in the final campaign.

## 9. Provenance and persistence

Every detector result must contain:

- repository commit;
- external-reference commits;
- model / epsilon / method / seed;
- train/validation/test image names;
- selected epoch and validation metrics;
- final test per-image scores/errors;
- environment and GPU information;
- checkpoint SHA-256;
- raw-result SHA-256.

Checkpoint filenames must include model, epsilon, method and seed so that no condition can overwrite another.

## 10. Hard interpretation

C6 can pass only if coding/raw provenance remains PASS, SRM+EC is complete, at least one deep architecture completes all three fixed seeds, the claim/code/data audit passes, and any detector disadvantage of `IG_matched` is retained and reflected in the manuscript wording. SiaStegNet is a preregistered independent stress test; SRNet with all three seeds is sufficient for the minimum deep-reference closure condition in the parent V8 rule.