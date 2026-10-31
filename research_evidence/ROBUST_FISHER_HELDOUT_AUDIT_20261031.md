# Fisher–Rao and robust steganographic decoding: held-out comparative audit (31 Oct 2026)

**Status: scientifically negative/inconclusive for operational Fisher superiority. This is NOT the original NG-Stego Algorithm 2. Do not insert a success claim in the manuscript.**

## Trial design
The public checkpoint `data/s5_vae_mnist.pt` defines a 2D-latent Bernoulli image generator. Use a fixed 2-bit message partition based on median-filtered centred moments and conditional sampling. For each of 12 seeded initial latent centres per regime, calibrate the decoder with 1,600 independent synthetic covers, estimate the robust-decoding objective and its gradient with 4,500 independent generator samples, then evaluate on 6,500 separate generator samples. Four frozen channels: 1px vertical shift, 1% pixel inversion, JPEG quality 50, down/up-scaling 14/28. All methods share the exact sampled images and attack realizations within each centre.

Fisher and Euclidean use the **same** gradient and the same exact KL(P_z || P_z0) budget (.002 or .02 nat); only the update direction changes, respectively `(F+1e-6 I)^-1 g` and `g`. Both are one-step updates with full KL-budget radial search, not equal-final-objective convergence experiments. The unchanged-cover model is a necessary reference; a 16-direction training search was additionally run on **3** centres (different sample counts, not pooled).

The objective is mean exact conditional-success expectation estimated using self-normalised importance sampling from P_z0 and per-message-bin balancing. The score-function conditional-covariance gradient was independently checked against central finite differences. The Fisher metric is the exact Bernoulli logit-Jacobian Fisher matrix; every candidate's KL was numerically checked. A description of likelihood/TV limitations belongs with every result.

## Held-out results

| Centre distribution | KL cap | Fisher J | Euclidean J | Fisher - Euclidean (percentage points) | Centre bootstrap 95% CI (points) | Fisher wins |
|---|---:|---:|---:|---:|---|---:|
| Uniform [-0.55,0.55]^2 | .002 | .793218 | .793221 | -.000322 | [-.001775,+.001320] | 7/12 |
| Uniform [-0.55,0.55]^2 | .020 | .793899 | .793913 | -.001441 | [-.006361,+.003776] | 7/12 |
| Uniform [-1.5,1.5]^2 | .002 | .805686 | .805659 | +.002745 | [-.000329,+.006122] | 7/12 |
| Uniform [-1.5,1.5]^2 | .020 | .806411 | .806336 | +.007508 | [-.002650,+.018289] | 7/12 |

No interval excludes zero. The 24 centres across regimes use **the same underlying random uniform draws rescaled to different ranges**; do not treat the pooled 24 as independent.

At KL=.02 in a smaller diagnostic with 3 centres, a 16-angle training optimiser achieved mean held-out J=.800577, versus Fisher=.800355 and Euclidean=.800429. This diagnostic uses only 2,400 training and 4,000 held-out samples per centre and is **not** a matched-compute claim.

## Why the mathematical guarantee is not enough
For a positive-definite exact Fisher matrix F and the same estimated local gradient g, the local linear gain under the quadratic Fisher budget is maximised by d ∝ F^-1 g: by Cauchy–Schwarz, `(g^T F^-1 g)^(1/2) >= (g^T g)/(g^T F g)^(1/2)`. This **local first-order property** holds in our numeric tests; it does not imply higher held-out robust decoding, lower TV to covers, global optimum, detector resistance, or reliability of original NG-Stego.

The new trial was exploratory: the initial larger 9,500/16,000 protocol had to be reduced to 4,500/6,500 because of the execution budget **after an initial partial run**. CIs are centre-clustered fixed-estimator bootstrap CIs, not formal population security bounds. JPEG is applied to binary VAE images, not real photographs.

There is **no hard TV(Q,P0) bound in the optimiser**. `TV(Q,P_z)` is estimated from held-out message-bin occupancies, not proven exactly; a KL(P_z||P0) constraint alone does not fix the TV of rejection-conditioned output. The detector/adversarial evaluation of original Algorithm 2 and full iMEC/Discop pipelines remains outstanding.

## Scientific decision
Do not claim Fisher operationally outperforms Euclidean in this setting. The next discriminating experiment must modify the **original Algorithm 2** (not replace it with a matched-rejection scheme), enforce an independently verified cover-distribution constraint, evaluate a stronger adversary and native-compatible baselines, and report the accuracy/capacity/detectability/compute frontier; it must accept negative results.

References within repository: `research_evidence/robust_fisher_heldout_reproducer.py` (Github reference implementation), `research_evidence/robust_fisher_heldout_summary_20261031.json` (aggregates). The independently executed full local source and per-centre outputs remain in the audit ZIP delivered in ChatGPT; **Github and ZIP source files are not byte-identical**. Do not claim an exact rerun of the ZIP from Github is currently certified.
