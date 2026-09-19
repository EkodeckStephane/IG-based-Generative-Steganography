# Positive and Boundary/Negative Results

## Positive results
1. Exact Cachin orientation D_KL(P_C||P_S) is used consistently.
2. The central source-mismatch separation theorem passes all five strong-theorem criteria.
3. Continuous/discrete numerical QA: **19/19 tests PASS**.
4. Controlled grid: 48 frozen cells, **0 robust-budget violations**; all positive-radius robust optima are non-scalar and improve on uniform shrinkage.
5. V3 independent confirmation: median D80 at r=0.12 = **0.1902**.
6. V6 empirical PMF geometry: three modes explain **97.85%** inter-camera Fisher energy; D80 = **0.4817** and **0.5308**.
7. Same robust risk: rate-envelope gains **+2.8849%** and **+16.5025%** over uniform shrinkage.
8. Same ideal payload: certified worst-risk reductions **6.7272%** and **38.1360%**.
9. V7 matched-payload lightweight AUC remains near chance for both methods.
10. Complete V8 STC: **20,000 encodings**. Low budget 5000/5000 success for both; high budget 4998/5000 uniform and 4999/5000 IG; successful-codeword BER=0.

## Boundary/negative results
1. Controlled-grid median rate gain is only **0.436%**; only 11.1% of positive-radius cells exceed 2%.
2. V4A natural within-source D80 = **0.0218/0.0387**, below frozen 0.05 materiality threshold.
3. V5 log-scale source geometry shows empirical PMF-shape misspecification at low budget, motivating V6.
4. Continuous Gaussian approximation is inadequate for final certification in the smoothest quantized strata; discrete/empirical PMFs are used instead.
5. V7 is a lightweight detector layer; strong SRM+ensemble/deep evaluation remains required for detector-facing conclusions.
6. BOWS2 external transfer remains the frozen independent cross-corpus test.
7. V8 retains three high-budget coding failures; no payload reduction removes them.
8. At matched message payload IG uses slightly more modifications (+0.00414/+0.00703 mean modification fraction) and slightly lower PSNR (-0.171/-0.200 dB), making strong steganalysis an important next measurement.

The evidence therefore supports a regime-dependent source-robust design contribution rather than a universal large-rate-gain narrative.
