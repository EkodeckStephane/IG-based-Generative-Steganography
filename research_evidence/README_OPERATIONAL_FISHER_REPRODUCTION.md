# DSP-D-26-02810 — Fisher operational validation, 31 October 2026

**Status:** exploratory study on real MNIST finite source + separate Bernoulli VAE pilots. The existing manuscript, Response to Reviewers and Cover Letter are NOT changed by this study. No scientifically demonstrated operational Fisher advantage or complete Reviewer-2 R2.3/R2.7 satisfaction is claimed.

## Files and scientific scope

1. `operational_fisher_robust_7features.py`: full finite-source experiment, seven standardized features, Fisher and Euclidean conditional-success optimization constrained by train-set KL and TV; 15k calibration, 20k optimisation, 10k independent test.
2. `operational_fisher_robust_v2.py`: same design with two-dimensional exponential-tilt statistic.
3. `triple_exact_diagnostic.py`: exact enumeration of three independent repetitions of 2-bit masked messages, with 64 possible error triples, under each seeded attack.
4. `external_validation_20k.py`: evaluation of FROZEN optimisation parameters on independently held-out 20k original MNIST training images, not used in fitting.
5. `vae_generator_fisher_robustness.py`: entropy-guided generator-Fisher versus Euclidean perturbations under exact KL 0.02, 12 independent latent centres.
6. `vae_fisher_robust_objective.py`: score-function estimator of gradient of robust conditional decoding utility, with real decoder VAE Fisher, 8 latent centres; *not Algorithm 2*.
7. `test_operational_invariants.py`, `test_vae_fisher_score.py`: math and numeric tests.
8. `prototype_original.py`: original VAE reference helper used for checkpoint loading, Bernoulli decoder, Fisher and KL.
9. JSON numeric evidence, aggregate CSV, report PDF and figure; model checkpoint `s5_vae_mnist.pt`; `mnist_train_real.gz`, `mnist_test_real.gz`, original IDX gray images extracted from the project baseline.

## Pre-conditions

Python 3.11+ with `numpy scipy Pillow matplotlib torch scikit-learn reportlab`; tested with NumPy 2.3.5, SciPy 1.17, Pillow 12.3, PyTorch CPU 2.10, scikit-learn 1.8, ReportLab 4.4.9. Run from the extracted directory. Original MNIST train/test gz archives and checkpoint are included. The experiment is restricted to MNIST and Bernoulli VAE; no claims about natural-color photo generators, native iMEC/Discop, or real-world complete stealth.

## Exact execution

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python test_operational_invariants.py
python test_vae_fisher_score.py
python operational_fisher_robust_7features.py
mv operational_fisher_results.json operational_fisher_7features_results.json
python operational_fisher_robust_v2.py
mv operational_fisher_results.json operational_fisher_2features_results.json
python triple_exact_diagnostic.py
python external_validation_20k.py
python vae_generator_fisher_robustness.py
python vae_fisher_robust_objective.py
python make_summary.py
python build_report.py
```

The order matters: the two finite-source scripts both output `operational_fisher_results.json`, so rename each before running the next. Subsequent scripts load the two named files. The `README` is a reproduction guide, not a promise of bit-for-bit equality on all OS/hardware platforms for floating-point computations or synthetic randomness.

## Results and conclusions

Median-filtered centred moments, selected on a separate exploratory 5k training sample, markedly improve the original translation-sensitive projection decoder. Finite 10k test-source matched distribution yields mean symbol recovery **97.4678%** on six channels, exact *indexed-source* TV **0.01860**. The 7-feature conditional-score Fisher optimization with training-pool TV cap .05 improves this to **97.5183%** versus **97.5044%** for Euclidean, but the difference is only **0.0139 percentage points**, approximate bootstrap 95% interval **[-0.123,+0.148] points**, so no significant advantage is established. On separate held-out 20k validation, results are 97.4339% Fisher versus 97.4235% Euclidean. Fisher increases source TV relative to matched P0, harming statistical security. A TV cap checked on the training pool is not guaranteed to hold on a new pool.

Three-mask repetition: matched-source finite-pool exact accuracy is at least 99.515% across tested channels; throughput is 2/3 bit/image, with approximately four cover draws per encoded image. This requires three **independent** mask symbols. Single-image finite-TV is not a complete security assessment of multi-image correlations.

Actual Bernoulli-VAE FIM pilot with entropy objective: Fisher wins 5/12 centres, mean difference −0.183 percentage points against Euclidean; 8-centre robust-utility objective pilot: Fisher wins 4/8, mean difference −0.0286 points using common evaluation seeds. The direct VAE robust score gradient is mathematically appropriate for a conditioned uniform-message partition, but its Monte Carlo estimates remain noisy and it does not implement original Algorithm 2 NG-Stego. No direct advantage is established.

## Precise mathematical definitions

Finite empirical source images are unique 28×28 grayscale MNIST test samples. Source mass `P_theta(i) = exp(theta.T @ T_i) / sum_j exp(theta.T @ T_j)`. Given deterministic class `b(i) in {0,1,2,3}`, a fresh independent uniform 2-bit mask and rejection sampling, the output mass is `Q(i)=P_theta(i)/(4q_b(i))`, where `q_b=sum_{i in A_b} P_theta(i)`. TV(Q,P_theta) = 1/2 sum_b |q_b - 1/4|, and TV(Q,P0) = 1/2 sum_i |Q(i)-1/n| for the finite indexed source P0. The Fisher matrix for this finite-source family is Cov_{P_theta}(T), **not** the decoder VAE Fisher. The conditional objective and its gradient are `J(theta)=1/4 sum_b E_{P_theta(.|b)}[U(i)]` and `grad J = 1/4 sum_b Cov_{P_theta(.|b)}(U, T)`.

The separate Bernoulli-VAE Fisher score is `J_logits(z)^T (x-p(z))`; its exact Fisher is `J_logits^T diag(p(1-p)) J_logits`, used in the direct VAE pilot. The squared-rate gain from one-time mask and repeated robust statistics is not a new steganographic theorem; rejection sampling and natural gradients are established techniques.

## Constraints and nonclaims

This is an **exploratory** campaign; feature/decoder selection and multiple caps were tested, so the apparent Fisher improvements are NOT confirmatory. The Bernoulli VAE samples are independent pixel draws, unlike natural photographs. JPEG, resizing and translation are deterministic fixed routines; grayscale pixel inversions are random seeds, **not binary bit flips** of a ciphertext. The data-derived confidence interval assumes a fixed-weight first-order resampling approximation, not a full retraining/bootstrap. Real-distribution covertness, resistance to strong adaptive attacks, and parity with native iMEC/Discop are NOT established. The three official submission documents remain unchanged.

## GitHub

Public repository `EkodeckStephane/IG-based-Generative-Steganography`, directory `research_evidence`: protocol Markdown, code, numeric JSONs/CSVs and tests are synchronized and their Git blob SHA can be compared to the local `git hash-object` values. This repository may **not** include the two ~MNIST original gz data files and the neural checkpoint due binary-content connector limits; the ZIP provides these missing inputs. No unconditional GitHub-only reproducibility claim is made.
