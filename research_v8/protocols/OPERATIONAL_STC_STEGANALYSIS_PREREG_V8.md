# V8 — Actual-message STC realization and steganalysis preregistration

**Status: FROZEN before any STC-coded V6/V7 stego is generated.**
Date: 2026-09-10.

## Evidential purpose
V8 addresses the remaining operational claim: whether the frozen information-geometric allocation can be realized with recoverable secret messages and remains competitive under reference and contemporary steganalysis at matched payload. V8 is development evidence on BOSSBase fit+calibration; BOWS2 remains reserved for external confirmation when supplied.

## Frozen designs
Use the `uniform_shrink` and `IG_matched` beta/cost vectors from `v7_frozen_designs.json`. Their ideal ternary entropy rates are exactly matched within each epsilon. No beta, cost or scale may be changed after STC outcomes are observed.

For symmetric ternary embedding, assign per-stratum +/-1 cost
`rho_g = log((1-2 beta_g)/beta_g)`
up to a common positive factor. Non-carrier locations are wet/forbidden. Pixels at 0 or 255 are excluded before coding. Carrier lattice, predictor and eight context strata are exactly those frozen in V4--V7.

## Reference coding
Primary implementation: DDE Syndrome-Trellis Codes or `pySTC` based on that reference code. Use the low-level ternary +/-1 STC operation on the vector of eligible carrier centers only; do not rely on a wrapper that hides a length header in arbitrary full-image pixels.

For each image and epsilon, generate one deterministic random message shared by both compared methods using SHA-256(`V8|epsilon|filename`) as seed. Actual payload is fixed before coding to 90% of the common V7 ideal entropy rate per eligible carrier:
- epsilon=2e-4: 0.4789010282 message bits per eligible carrier;
- epsilon=8e-4: 0.6480707028 message bits per eligible carrier.
The integer message length for an image is floor(target_rate * N_eligible).

A deterministic carrier permutation derived from SHA-256(`V8-perm|epsilon|filename`) is permitted and must be identical between methods. Extraction uses the inverse ordering and the known message length.

## Coding endpoints
Report for every method/budget: exact message-bit recovery, coding failure rate, number of modifications, distortion cost, coding loss relative to V7 ideal entropy, PSNR, and realized per-stratum change frequencies. Operational coding PASS requires zero bit errors among successfully coded images and >=99% coding success. Any failure remains reported.

## BOSSBase operational split
Use all 5000 non-holdout images from V4: the 3500 frozen `fit` images are the detector-training source; the 1500 frozen `calibration` images are the detector-test source. Cover and corresponding stego stay in the same side. BOSSBase V4/V5 holdout is excluded from V8.

## Steganalysis tiers
All methods are evaluated at the same actual message length image-by-image.

Tier A — classical reference: Spatial Rich Model features with Ensemble Classifier (SRM+EC), using a public/reference implementation. No V7 SPAM-like feature may be called SRM.

Tier B — established deep reference: SRNet, trained/evaluated with fixed seeds and no cover/stego pair leakage.

Tier C — independent deep architecture: official SiaStegNet implementation. If resources permit, RMNet (2025) may be added as a contemporary stress-test; it is supplementary and does not replace SRNet/SiaStegNet.

For deep models, report training seed, checkpoint rule fixed before test evaluation, epochs, optimizer, learning-rate schedule, augmentation, hardware and test-time policy. A minimum of three training seeds is required for any headline deep-learning comparison. If compute resources make three seeds impossible, the deep result is exploratory and cannot close C6.

## Metrics and fairness
Primary security metric: detector error probability / balanced error with ROC-AUC reported jointly. Also report 95% uncertainty across seeds or paired bootstrap for classical fixed detectors. Compare `uniform_shrink` vs `IG_matched` at identical actual payload and source images. Do not compare a higher-payload IG stego to a lower-payload baseline as evidence of superior detectability.

Primary operational interpretation is non-inferiority at matched payload plus the independently certified V6 robust-risk advantage. A detector result near chance is not evidence of perfect security. A detector that significantly favors the baseline must be retained as negative evidence.

## Baselines
The operational paper must include at least one established adaptive spatial embedding reference (MiPOD is mandatory because of the direct Fisher lineage; S-UNIWARD or HILL is recommended) at the nearest feasible matched actual payload. These references are not required to satisfy the new robust-Cachin guarantee; they calibrate empirical detectability.

## Hard decision
C6 may become PASS only if: (i) actual message recovery passes; (ii) matched-payload evaluation is completed with SRM+EC and at least one deep reference with repeated seeds; (iii) no claim/code/data mismatch is found; and (iv) any detectability disadvantage is bounded and transparently reflected in the claims. BOWS2 remains a separate external-transfer gate.
