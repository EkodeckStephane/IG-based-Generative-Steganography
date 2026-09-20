# V8 strong-steganalysis execution status

**Decision at this snapshot: STRONG-DETECTOR EXECUTION BLOCKED BY RUNTIME RESOURCES — C6 REMAINS OPEN.**

This document records what was actually executed after the V8 STC/raw-provenance closure and prevents a missing detector run from being misreported as scientific evidence.

## Completed before the detector run

- BOSSBase split archive rejoined and CRC-checked.
- Rejoined BOSSBase SHA-256: `396be6f36f8c183312d7223b745fcffb5748606c3c8ec79579f7c5703143e9b4`.
- Exactly 5,000 non-holdout images are selected by the frozen V4 manifest: 3,500 `fit`, 1,500 `calibration`; holdout remains excluded.
- V8 STC coding/raw provenance already PASS from the clean 20,000-record rerun.
- The historically referenced `v7_frozen_designs.json` was found not to have been versioned. The four eight-dimensional execution-cost vectors were recovered from the persisted raw identities
  `distortion_cost = sum_g rho_g * strata_changes_g`, quantized to the float32 execution values, and stored as `results/v7_frozen_designs_reconstructed.json`.
- This recovery is not a recalibration. A direct reproduction on `1086.pgm` under all four V8 conditions exactly reproduces the historical eligible-carrier count, message length, total number of changes, and all eight per-stratum change counts.
- The vendored low-level STC source rebuild passes encode/decode QA at rates 0.30, 0.48 and 0.64 with zero bit errors.

## Frozen detector implementations

The execution lock pins:

- SealWatch SRM + FLD Ensemble: `uibk-uncover/sealwatch@90af7175a70f9c7cf48072b011334add499805db`;
- ConSeal MiPOD: `uibk-uncover/conseal@dcb24caae710ca60ea8492028b3f6bad2c23afd3`;
- official SiaStegNet: `SiaStg/SiaStegNet@592d9e13f39f287d9c675f1b89272bcfb6a9627c`;
- public PyTorch SRNet reproduction: `albblgb/Deep-Steganalysis@1a5b8f88ce3c928e44ca22ad66010d23cd4a1262`.

The harnesses are versioned under `research_v8/steganalysis/`.

## Runtime facts measured in this execution environment

- Python: 3.13.5.
- PyTorch: 2.10.0+cpu.
- CUDA available: false.
- `sealwatch` and `conseal` are not preinstalled.
- Runtime package installation cannot reach the package index because DNS resolution is unavailable.
- The frozen SRNet reference batch (four cover/stego pairs = eight 512x512 images after concatenation) is terminated by the runtime for resource exhaustion.
- Reducing the benchmark to two 512x512 images permits execution but measured approximately 3.82 s and 2.59 s for two consecutive forward/backward optimizer steps. This benchmark is diagnostic only; the frozen scientific batch/protocol is not changed in response.
- No SRNet, SiaStegNet, SRM+EC or MiPOD result is inferred from these diagnostics.

## Scientific consequence

The prerequisites for C6 require actual SRM+EC results and at least one repeated-seed deep reference. Those measurements have not been produced in this runtime. Therefore:

- C6: **OPEN**;
- detector-facing non-inferiority: **NOT ESTABLISHED**;
- strong-steganalysis conclusions: **NOT AVAILABLE**;
- Gate 10: **NOT ELIGIBLE FOR FINAL PASS ASSESSMENT**;
- Senior Reviewer Q1/Rang A final prescreen: **DEFERRED UNTIL THE FROZEN DETECTOR CAMPAIGN HAS REAL OUTPUTS**.

This is a resource/execution boundary, not a favorable or unfavorable detector result. The manuscript must not state that contemporary steganalysis has passed until the frozen campaign has been executed.
