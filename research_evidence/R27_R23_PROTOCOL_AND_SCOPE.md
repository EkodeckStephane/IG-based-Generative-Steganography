# R2.7 / R2.3 controlled diagnostic — evidence, not a replacement for S5

**Status:** Completed on the existing 2-D-latent Bernoulli VAE checkpoint, with a synthetic endpoint pair `z0=(0,0)`, `z1=(1.5,0.5)`. Fixed seed 20261031; 120 cover and 120 stego training samples and separate 120+120 test samples per method. 300 stratified test bootstrap replicates. CPU.

**Scope:** This is NOT the manuscript's original MNIST class-mean S5 benchmark, NOT Algorithm 2 NG-Stego, and NOT an equivalence test of native image/text iMEC and Discop. iMEC's new-run comparison was not completed within computational budget, and no results are claimed for it. The original S5 iMEC figures must not be pooled with these results.

**Threat model:** detectors see the sampled image; the geometry-enabled detector is permitted to run the public VAE encoder and compute a local Fisher-Mahalanobis feature. It never receives the private embedding path or message. The "oracle" row uses the known Bernoulli mixture likelihood for path methods only and is *not* an empirical security guarantee.

**Key observations:** paths are detectable (pixel/latent AUC 0.86–0.90); the controlled Discop adaptation exhibits AUC 0.515 pixel-based and 0.593 latent-based. Fisher-path exact decode 117/120, Euclidean 113/120, Discop 120/120. Positive-control oracle AUC=1.0. These results neither prove superiority nor strong undetectability; a more complete high-powered comparison is needed.

**How to run:** Requires Python with NumPy, SciPy, scikit-learn and PyTorch, the submitted `benchmark_s5_comparison.py` source and its pinned local upstream adapters, plus `data/s5_vae_mnist.pt` (checkpoint SHA-256 `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`). The upstream code and benchmark wrapper are **not yet fully published in this repository**, so the present GitHub file alone is **not standalone**. The manuscript submission bundle includes the exact benchmark wrapper; this dependency must be resolved before claiming repository-only reproducibility.

**Risks/limits:** Only one endpoint pair and one seed; no independent unseen generators; no adversarial encoder retraining; logistic detector only; no power calculation; no multiple-test correction; bootstrap intervals are descriptive; no proof of general NG-Stego security. Execution runtimes are device-specific. We do not yet claim complete satisfaction of Reviewer 2 points 3 or 7.

Evidence files: `r27_r23_controlled_adversarial.py`, `r27_r23_controlled_adversarial_results.json`, `r27_r23_controlled_adversarial_results.csv`.
