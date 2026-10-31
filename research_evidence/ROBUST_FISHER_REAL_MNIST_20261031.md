# DSP-D-26-02810 — Robust decoding, Fisher-specific ablations and actual MNIST images (2026-10-31)

**Status: experimental extension, NOT a replacement for NG-Stego Algorithm 2; R2.3/R2.7 NOT fully satisfied.** This repository records the audited scientific conclusions and the finite-source reference core. The entire 29-file experiment, original executed scripts, VAE checkpoint and MNIST raw files are in the independently hash-verified research ZIP delivered to the manuscript author. **Repository-only full rerun is not yet possible.**

## Independent experimental branches

1. Synthetic Bernoulli MNIST-VAE: 4 latent centres x [cover-matched, Fisher, Euclidean], calibration 6,000 and *independent* q-probability estimation 16,000, plus 170 held-out messages (2 bits) per channel. Additional 260 messages per centre per method, single image versus three *independently sampled* images.
2. Fisher entropy ablation, 48 prespecified Gaussian-sampled latent centres, same **exact KL constraint** for Fisher and Euclidean, budgets 0.005, 0.02, 0.08. VAE Fisher is the Jacobian-induced Bernoulli FIM. The Fisher direction is locally steepest in Fisher norm; no improvement in steganographic security follows from that alone.
3. **Real MNIST** (not VAE-generated): original 60,000/10,000 image IDX files from original user-provided revision archive; train splits 20,000 calibration / 20,000 distribution-tilt optimisation / 20,000 RBF-SVM detector training; 10,000 test pool. Evaluation: 420 independent 2-bit messages per configuration and 3 independent repetitions for each message. Source covers are *uniform over the finite test reservoir of 10,000 images*.
4. On real MNIST, Fisher is the categorical exponential-family FIM (covariance of two fixed source statistics), **not** the latent FIM of NG-Stego. A natural-gradient tilt maximises an auxiliary stability-margin utility locally at a fixed KL constraint.

## Real MNIST results, 420 messages / configuration

| Channel | Cover-matched, 1 image | Cover-matched, 3 images |
|---|---:|---:|
| Clean | 420/420 (100%) | 420/420 (100%) |
| independent bit flips 0.1% | 404/420 (96.2%) | 419/420 (99.8%) |
| independent bit flips 1% | 359/420 (85.5%) | 398/420 (94.8%) |
| JPEG quality 80 | 402/420 (95.7%) | 419/420 (99.8%) |
| JPEG quality 50 | 397/420 (94.5%) | 416/420 (99.0%) |
| Gaussian blur radius 0.6 | 419/420 (99.8%) | 420/420 (100%) |
| 28x28 -> 14x14 -> 28x28 bilinear | 409/420 (97.4%) | 420/420 (100%) |
| shift by 1 pixel with zero padding | 232/420 (55.2%) | 217/420 (51.7%) |

**Rate penalty:** 2 bits/image for one unaltered transmission versus **2/3 bit/image for triple repetition**. Shift failure is a real limit. Previous prototype parity GF(2) sometimes outperforms the robust projection under JPEG+thresholding; no universal robustness claim.

## Distribution guarantee and adverse results

For four measurable disjoint bins A_b with proposal mass q_b>0, uniformly masked payloads and conditional sampling: Q(x)=P(x)/(4 q_{b(x)}). Thus TV(Q,P)=0.5 sum_b |q_b-1/4|. On the finite MNIST-test reservoir we calculate TV(Q,P0) **exactly**, summing over all 10,000 sample-image probabilities, where P0 is uniform over that reservoir.

| Source distribution | Exact reservoir TV(Q,P0) | Margin utility, held-out | Pixel RBF-SVM AUC (95% bootstrap interval) |
|---|---:|---:|---:|
| Cover-matched | 0.0121 | 0.4586 | 0.4814 [0.4430, 0.5200] |
| Fisher exponential tilt, KL≈0.02 | **0.0741** | 0.4792 | 0.5271 [0.4911, 0.5623] |
| Euclidean exponential tilt, KL≈0.02 | **0.0750** | 0.4779 | 0.5131 [0.4737, 0.5500] |

The match baseline is closer to the empirical cover than either tilted version. **Fisher has not been shown to yield security superiority.** All AUCs are sample-estimates, not a formal indistinguishability guarantee.

## Fisher-specific ablation (VAE latent entropy, 48 independent centres)

| Fixed KL budget | Fisher improves entropy more on | Euclidean improves more on | Mean paired gain in Bernoulli entropy |
|---|---:|---:|---:|
| 0.005 | 46/48 | 2/48 | +0.01075 nat |
| 0.02 | 45/48 | 3/48 | +0.02047 nat |
| 0.08 | 42/48 | 6/48 | +0.04551 nat |

This is a verified **auxiliary objective** improvement, not a payload/detectability advantage. Its local optimum follows Cauchy-Schwarz in the Fisher metric.

## Limits and traceability

- Real MNIST grey-scale digits are not natural photographs; no high-resolution photo/caption/colour or social media degradation channel has been evaluated.
- The receiver needs the same thresholds and synchronized message mask; the research scripts use NumPy RNG and are **not cryptographically production-ready**.
- R2.3 still lacks operational adaptive security of original NG-Stego; R2.7 still lacks full native iMEC/Discop equivalence. Rejection sampling/partition methods are established prior art.
- Further independent image sources, realistic generative models, robust ECC, native baseline and adaptive detector campaigns remain necessary.
- Model checkpoint SHA-256: `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1d1ed61`. Full research ZIP SHA-256: `aa451968d0bee7d2dd5bba2c19214484be02d7c261185d63217e04e0978c4750`.
- Original scripts in delivered ZIP: `robust_fisher_experiment.py`, `repetition_and_fisher_ablation.py`, `attack_evaluation.py`, `real_mnist_robust_channel.py`, `test_scientific_invariants.py`. Full ZIP passed `testzip` and tests passed **again after extraction**.
- The actual article, review response, and cover letter were **not modified** on this exploratory result.

Data: LeCun et al. MNIST, see https://archive.ics.uci.edu/dataset/683/mnist ; Amari 1998 DOI 10.1162/089976698300017746.
