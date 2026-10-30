# R2.7 / R2.3: DIRECT Algorithm 2 validation — 2026-10-31

**Do not merge the figures below with the original MNIST class-mean S5 experiment or the prior 2026-10-30 diagnostic.** This is a separate bounded test with synthetic codebook endpoints.

## Exact experiment
- Public MNIST-VAE checkpoint SHA-256: `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`; input channel 784 Bernoulli pixels, 2-D latent.
- `z0=(0,0)`, `z1=(1.5,0.5)`; the fixed 4-point linear target codebook maps 2-bit messages to parameters. 120 train cover +120 train stego; independent 120 test cover +120 test stego per method. Balanced paired message assignments and comparable seeds.
- **Algorithm 2**: minimize `KL(P_z || P_target)` with **N=256 Monte Carlo samples from P_z for the Fisher score outer product** per iteration; damping `1e-3 I`, Armijo backtracking, tolerance `1e-5`, cap 100 iterations. Exact-Fisher and Euclidean GD ablations optimize the same objective and target codebook.
- The authors' iMEC encoder/decoder (via same Bernoulli-medium adapter) and Discop distribution-copy adaptation were run on the same cover channel `p(x|z0)`, fixed 2-bit messages. These are **controlled channel adaptations**, not their full native text/image pipelines.
- Detector 1: logistic regression on pixels. Detector 2: logistic regression on observable public-VAE encoder features and a Fisher-Mahalanobis feature; **private paths are never given to detectors**. AUC and percentile bootstrap 95% CI (200 replicates), exploratory sample sizes. The original study's SRM/ResNet detection results **must not** be assumed to apply to this new run.
- Checkpoint, gradients (finite difference <1e-8 relative), decoder Jacobian (finite difference <3e-11 relative), and Fisher covariance (model-sampled Monte Carlo 30k draws; <1.6% relative) were audited in `test_r27_algorithm2_direct.py`.
- Not an independent model evaluation, not a geodesic optimizer, not a proof of adaptive security, and no GPU/CPU runtime fair comparison. Report all outcomes, including non-convergence.

## Verified results (see CSV)
- Algorithm 2: **2/4 target solutions meet KL tolerance**, 60/120 exact decode, pixel AUC 0.86694, geometry AUC 0.86722.
- Exact Fisher ablation: 2/4 converge, 60/120 decode, pixel and geometry AUC equal at displayed precision.
- Euclidean GD: 3/4 converge, 120/120 decode, pixel AUC 0.87875, geometry AUC 0.89660.
- iMEC adapted: 120/120 exact decode, pixel AUC 0.45896, geometry AUC 0.51618.
- Discop adapted: 120/120 exact decode, pixel AUC 0.52368, geometry AUC 0.50021.
- The non-convergence corresponds to sizable terminal KL values (121.59 and 185.10 nats) for target codepoints 2 and 3. Since two method variants converge to the same local loss and both experience failure, do not claim universal convergence.
- The full experiment and auditor source are in `Version_1.0/research_evidence/r27_algorithm2_direct_v1.py` and `test_r27_algorithm2_direct.py` within the packaged research archive. The standalone GitHub `r27_algorithm2_core_standalone.py` reproduces the **optimizer core only**, not the complete detector/decoder comparison. The source of `benchmark_s5_comparison.py` is a prerequisite for full reruns and has not yet been uploaded to the public repository.

## Scientific interpretation
These results do **not** establish NG-Stego superiority or operational undetectability. They demonstrate a concrete local-optimization reliability limitation and meaningful detectability on this endpoint configuration. R2.3 and R2.7 are strengthened experimentally but **still partial**, as independent larger samples, real MNIST endpoints, native baselines and adversarial re-training remain out of scope.

## Additional interpretation: cover-valued codeword and AUC ceiling

Because the fixed four-point codebook **includes z0 as one valid message codepoint**, one quarter of stego examples is sampled from the exact cover distribution. In this balanced two-bit experiment, for any detector and the population AUC metric, the strongest possible separation of the other three codewords implies an upper limit of **AUC <= 1 - 0.25/2 = 0.875**. Sample AUC estimates may fluctuate above it. The measured Algorithm 2 pixel AUC of 0.86694 is near this ceiling; it must NOT be misinterpreted as low detectability. A more informative follow-up must exclude cover as a message codeword and evaluate new codebooks separately.

The three submission documents have NOT been edited with these exploratory numbers, because the experiment uses synthetic endpoints rather than the original MNIST class-mean protocol. The complete five-method runner, raw per-method outputs, and numeric audit are in the associated research ZIP. GitHub presently holds the standalone Algorithm 2 optimizer core and verified aggregate table; full repository-only reproduction of the detector benchmark is not yet certified.
