# V8 strong-steganalysis GPU campaign — Google Colab

This is the canonical execution path after the pre-GPU reconciliation addendum. Do not change seeds, splits, image resolution, epoch counts, detector architectures, or failure handling after observing detector results.

## Required Colab runtime

Use a GPU runtime. NVIDIA T4, L4, A100 or equivalent is acceptable. The notebook records the actual GPU and software versions in the result artifacts. Do not run the headline deep campaign on CPU.

## Data

The notebook downloads BOSSBase 1.01 from the DDE/Binghamton source when possible. A fallback Google Drive ZIP path is supported. The preflight requires exactly 10,000 native 512x512 PGM images and the frozen V4 manifest counts 3500 fit / 1500 calibration / 5000 holdout.

## Canonical code sources

The campaign pins:

- repository branch `cachin-ig-robust-v8` at the code commit written into the notebook;
- DDE full SRM 34,671D Linux package;
- SealWatch commit `90af7175a70f9c7cf48072b011334add499805db`;
- ConSeal commit `dcb24caae710ca60ea8492028b3f6bad2c23afd3`;
- SRNet reproduction commit `1a5b8f88ce3c928e44ca22ad66010d23cd4a1262`;
- official SiaStegNet commit `592d9e13f39f287d9c675f1b89272bcfb6a9627c`.

## Execution order

1. Mount Google Drive and create a persistent result directory.
2. Clone the exact repository commit and install pinned dependencies.
3. Download/extract BOSSBase and run `preflight_v8_gpu.py`.
4. Download the official DDE SRM Linux package and run its one-image 34,671D/106-submodel smoke test.
5. Run DDE-SRM feature extraction in resumable index shards with `research_v8/src/run_v8_srm_shard.py`. This computes cover, both V8 methods at both budgets, and MiPOD at exact image-specific V8 payload without storing 35,000 images.
6. Run `run_srm_ec_from_shards.py` to fit SealWatch FLD Ensembles and produce paired bootstrap intervals.
7. For each V8 deep condition, materialize only that condition locally with `materialize_v8_condition.py`, then run SRNet for the three fixed seeds. Checkpoints/results are persisted to Drive and are resume-safe.
8. Repeat SiaStegNet for the same four conditions and three seeds if resources permit. It is the preregistered independent deep stress test.
9. Run `aggregate_v8_strong_steganalysis.py`.
10. Run the result packager cell. Return only the final ZIP to ChatGPT; raw stego images and SRM feature arrays are not required for the final scientific audit unless a verification discrepancy is found.

## Minimum result set required to evaluate C6

The return ZIP must contain:

- `environment.json` and `COLAB_PREFLIGHT_LAST.json`;
- `srm_ec_results.json`;
- 12 SRNet JSON result files: 2 epsilons x 2 V8 methods x 3 seeds;
- SRNet best checkpoints or at least their retained SHA-256 hashes plus the JSONs that name those hashes;
- `strong_steganalysis_aggregate.json`;
- the campaign SHA-256 manifest.

SiaStegNet adds another 12 JSONs/checkpoint hashes and materially strengthens the final external-detector evidence. If SiaStegNet is incomplete, keep partial results; do not delete an unfavorable or interrupted seed.

## What not to do

Do not resize or crop BOSSBase for headline tests. Do not change the three seeds. Do not use the 1500 calibration images for early stopping or checkpoint selection. Do not replace MiPOD's image-specific payload by the mean bpp. Do not omit the three V8 coding failures from the coding report; only the predeclared common-success intersection is used for matched detector comparisons. Do not rerun seeds selectively because of their detector scores.