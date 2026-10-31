# Exploratory Fisher-constrained cover-matched sampling (2026-10-31)

**Manuscript:** DSP-D-26-02810, *Fisher–Rao-Guided Generative Steganography*. **Status: early independent research prototype; NOT original Algorithm 2, NOT incorporated into manuscript, NOT fully satisfying R2.3 or R2.7.**

## Core method

For a binary image x from the fixed Bernoulli-VAE generator P_theta(x), choose a random GF(2) linear hash H of shape (2,784); encrypt each 2-bit message with fresh secret independent one-time pad u; rejection-sample exact generator covers until Hx = message XOR u. Receiver recovers message as Hx XOR u, with no VAE inverse. As long as every bin has nonzero probability, decoding is exact over a LOSSLESS channel. Expected draws ~4.

For fixed H and uniform ciphertext, let q_b=P_theta(HX=b). The stego marginal is P_theta(x)/(4 q_{Hx}), and **TV(P_stego,P_theta) = 0.5 sum_b |q_b-1/4|**. Bernoulli independence allows exact Walsh-parity calculation of q_b. Numerically stable log-domain parity-product bounds show the hash-induced TV is below 1e-52 for each of 12 observed configurations. This is a **model-relative** statement; genuine MNIST photographs/images are NOT guaranteed covered by it.

Additional source movement: find Fisher-natural entropy-ascent direction proportional to F^{-1}grad H and compare with Euclidean gradient direction, calibrating both to **exact KL(P_theta||P_theta0)=0.02 nats**, so Pinsker gives TV(P_theta,P_theta0)<=0.1. Fisher is used only for constrained **source modulation**, not for the standard rejection encoder.

## Completed four-center exploratory experiment

4 latent centers, 3 methods, fixed 2-bit load, 180 cover+180 stego training and independent 260+260 test for each center/method, leave-one-center-out RBF-SVM pixel and public-encoder detector; model-known likelihood-ratio oracle. SHA-256 of VAE checkpoint: e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61.

All 1040/1040 test messages decoded for each of the 3 strategies (lossless only). Pixel-detector mean AUC: 0.497 matched, 0.496 Fisher, 0.518 Euclidean; model-oracle mean AUC 0.500, 0.536, 0.562 respectively. At matched KL, Fisher gained 0.597 nats of generator entropy vs Euclidean 0.572, on these **four points only**; neither proven payload nor quality improvement.

**Severe limitation:** random bit flips destroy the GF(2) message checksum: at 0.1% independent bit-flip probability, theoretical 2-bit recovery ~59%, at 1% ~25%. Even lossless-to-JPEG conversion is unaddressed. NumPy randomness is for scientific reproduction, not secure production. OTP synchronization and cryptographic entropy are additional requirements.

**Prior work and novelty:** Rejection sampling as a steganography mechanism is well-established (Hopper, Langford, von Ahn, *Provably Secure Steganography*, IEEE Transactions on Computers, 2009, DOI 10.1109/TC.2008.199). Compare also Huang et al., *OD-Stega*, EACL 2026, DOI 10.18653/v1/2026.eacl-long.36, and Woźniak et al., *Distribution-Preserving Latent Image Steganography*, Electronics 2026, DOI 10.3390/electronics15061321. The novelty of a Fisher/KL-constrained cover source adjustment in this setting **has not been demonstrated**.

**GitHub scope:** the companion `fisher_matched_sampling_core.py` implements and documents the mathematical encoder and Fisher direction, and `fisher_matched_sampling_summary.csv` contains verified aggregate outcomes. The full VAE benchmark, checkpoint, regression tests, per-center JSON and independent adversary evaluations are in the separate self-contained ZIP provided for the revision project; this repository snapshot alone is NOT yet a full end-to-end rerun environment.
