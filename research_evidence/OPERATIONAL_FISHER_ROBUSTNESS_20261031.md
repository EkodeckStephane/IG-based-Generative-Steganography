# Operational Fisher–Rao steganography research — 31 October 2026

**Status: exploratory evidence, NOT definitive Reviewer-2 R2.3/R2.7 validation; the three submission documents are unchanged.**

## Question tested

Can a Fisher natural-gradient step improve **end-to-end two-bit decoding after image transformations**, under explicit KL and total-variation bounds, rather than merely increase generator entropy? The experiment uses *original MNIST grayscale images* sampled from a **finite empirical pool**, with 4-message-bin conditional sampling and independent uniformly masked message symbols. This does **not** execute the manuscript's original NG-Stego Algorithm 2. Its Fisher matrix is **Cov(T)** for a categorical exponential tilt of a real-image pool, **not the VAE latent generator FIM**.

## Data separation and methods

Original MNIST 60k train, 10k test, no new data downloaded. Training images 0–4999 for exploratory decoder selection, 5000–19999 for calibration, 20000–39999 for distribution fitting, 40000–59999 as a separate frozen-parameter validation set; all 10k original test images used for independent evaluation. Two feature sets for the categorical tilt: two centred image moments, and seven standardized image features (moments/centroid/foreground/intensity). Preprocessing for decoding: 3×3 median, foreground threshold, centred moments, 4 calibrated bins. Evaluated attacks: JPEG Q50, Gaussian blur 0.6, 28→14→28 bilinear resizing, 1-pixel vertical translation, random inversion rates 0.1% and 1%.

For source weights p_theta(i), message-bin masses q_b and independent uniform OTP masks, exact finite-pool stego marginal **Q(i)=p_theta(i)/(4 q_{b(i)})**; total variation TV(Q,P0) and average one-image symbol correctness per attack are calculated by source enumeration. Fisher/natural and Euclidean gradients are optimized **only** on the fitting pool, with KL<=0.02 and training-pool TV caps 0.03/0.05/0.075. Caps are not guaranteed to hold on unseen pools.

## Key results at training TV cap 0.05, 7-feature tilt

- Matched source, no displacement: 10k test mean transformed one-image correctness **97.4678%**, exact finite-source TV **0.01860**. Separate validation 20k: **97.3503%**.
- Fisher step: 10k **97.5183%**, TV **0.04674**, KL **0.00613**. Separate validation 20k: **97.4339%**, TV **0.04610**.
- Euclidean step: 10k **97.5044%**, TV **0.05026**, KL **0.00961**. Separate validation 20k: **97.4235%**, TV **0.04839**.
- Fisher–Euclidean difference: **+0.0139 percentage points** on 10k test, approximate stratified/fixed-weight bootstrap interval **[-0.123,+0.148] percentage points**; it includes zero. On the second 20k validation pool **+0.0104 percentage points**. **No statistically established end-to-end Fisher benefit.**
- Clean decode is 100% by construction. Matched-source one-image success on 10k: JPEG50 97.545%, blur 97.025%, resize 94.354%, shift 99.074%, 0.1% bit flip 99.547%, 1% bit flip 97.261%.
- With three independent masked transmissions of the same message, analytically enumerating all 4^3 error vectors yields matched-source success: JPEG50 **99.903%**, blur **99.859%**, resize **99.515%**, shift **99.979%**, 0.1% flip **99.997%**, 1% flip **99.883%**. This reduces useful rate to **2/3 bit per image**; independence requires a fresh mask for each repetition.
- Expected cover draws per encoded image ~4 for the matched source. Source-resampling performance depends on this **finite original MNIST pool** and does not extrapolate to arbitrary real-world photographs.

## Validation, security and novelty constraints

Independent test code checks normalized Q, TV(Q,p_theta)=(1/2)sum_b|q_b-1/4|, score gradient by centered finite differences, positive FIM eigenvalues, Fisher local first-order steepest ascent, and repetition success extremes. The 7-feature training FIM condition number is ~1471; numerical conditioning matters.

This experiment was exploratory: the robust median-moment decoder was selected using 5k training images, and several TV caps and feature configurations were examined. Stochastic attacks are evaluated under documented fixed-seed realizations, not over all channel noise. Measured 1-image TV on the finite pool does not automatically prove strong secrecy of multiple-image communications. Euclidean gradients depend on parameterization; whitening can reproduce the natural direction. Rejection-sampling steganography is prior art (Hopper, Langford & von Ahn, 2002); natural gradient is prior art (Amari, Neural Computation 1998, doi:10.1162/089976698300017746). No novel robust information-theoretic security theorem is claimed.

**Scientific verdict:** the robust decoder improves materially on the previous translation-sensitive partition, but the advantage is not attributable to Fisher. Do **not** claim R2.3/R2.7 are fully resolved. A direct generator-FIM/Algorithm-2 comparison with faithful baseline decoders and independent steganalysis remains needed. The CSV alongside this report contains all 14 rows of tested comparisons; the full Python runner, exact triplicate evaluator, datasets and tests are provided in the companion research ZIP because the GitHub repository is not yet standalone for this complete experiment.

## Addendum: actual Bernoulli-VAE generator Fisher pilot

To distinguish the empirical-source Fisher above from the **actual decoder VAE Fisher**, we independently ran a pilot across 12 deterministic latent centres uniformly drawn from [-0.65,0.65]^2 (seed 20261031+7), comparing Fisher versus Euclidean **entropy-ascent** directions with exact identical Bernoulli KL = 0.02, and matched generator p0. For each centre/method, 900 new calibration draws and 1,000 new evaluation draws were used. The same median-filter/centred-moment 2-bit partition and six image transformations were used. The conditioned uniform-message detection-quality estimator was sample-reweighted by 1/(4q_bin), with q_bin estimated on each evaluation set. This is a pilot with Monte Carlo estimation uncertainty and different random images for each method, not matched-pair security validation. No original Algorithm 2 or detector evaluation is claimed.

**Result:** Fisher improves mean robust single-image correctness over Euclidean in **5/12** centres; Euclidean wins in **7/12**. Mean Fisher–Euclidean difference = **-0.1826 percentage points**, descriptive centre-level 95% t interval **[-0.4630, +0.0977] percentage points**. This does **not** establish either method's superiority. The actual generator-Fisher entropy gain previously observed does not automatically translate into robust decoding gain. See the companion 12-centre CSV.

The companion research ZIP contains `vae_generator_fisher_robustness.py`, the original checkpoint, dependency `prototype_original.py`, and the JSON results. GitHub currently provides aggregate evidence and methodological documentation; repository-only complete reproduction is **not yet certified**.
