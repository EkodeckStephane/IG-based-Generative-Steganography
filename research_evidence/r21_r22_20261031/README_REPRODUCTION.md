# DSP-D-26-02810 — R2.1 & R2.2 mathematical/experimental verification

**31 October 2026. Research evidence only; NOT inserted into the three submission documents.**

## Exact model / hash

`data/s5_vae_mnist.pt` is the pinned two-dimensional, 784-output Bernoulli VAE checkpoint. SHA-256: `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`.

Requirements: Python 3.11+, `numpy`, `scipy`, `torch`, `scikit-learn`. For rebuilding PDF report, `reportlab`, `matplotlib`, `Pillow`; for LaTeX appendix, `pdflatex`, `amsmath` and `hyperref`. No internet access required after obtaining dependencies and the checkpoint.

## Execution

```bash
python -m pip install numpy scipy torch scikit-learn matplotlib reportlab Pillow
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python -m unittest test_r21_r22 -v
python r21_r22_experiment.py --checkpoint data/s5_vae_mnist.pt --out .
python r21_smooth_geodesic_stability.py
python build_r21r22_report.py
pdflatex -interaction=nonstopmode -halt-on-error R21_R22_THEOREMS_AND_PROOFS.tex
```

## Scientific interpretation

- R2.1: local inexact variable Fisher one-step theorem; conditional `C^{1,1}` initial-value geodesic stability lemma; not global guarantees or general GAN/diffusion results. The checkpoint's ReLU decoder exhibits jump discontinuities in the Fisher metric across activation boundaries, invalidating direct use of the smooth geodesic lemma there.
- R2.1 MC Fisher: 6 latent centers; N in 32,128,512,2048; eight independent replicates per center and N; comparison to model-based `F=J^T diag(p(1-p))J`.
- R2.2: 4 independent codebook rotations at each of four radii for 1,2,3,4 bits: 64 configurations, 16,384 Bernoulli messages. Codeword distances are **only nominal fixed-at-cover quadratic Fisher distances**, not verified global Fisher–Rao geodesic separations. The model-known decoder and oracle steganalyzer are privileged diagnostics, not an available secure production system.
- This is not a rerun of NG-Stego Algorithm 2; it probes the feasibility of connecting geometric spacing, reliable message decoding, and detectability. All tested codebooks are highly detectable by a model-aware score in this parameter regime.
- No proof of a positive secure capacity or a universal improvement of Fisher over Euclidean optimization is asserted.

## Output map

- `R21_R22_THEOREMS_AND_PROOFS.tex/pdf`: precise conditions and mathematical proofs (English).
- `RAPPORT_R21_R22_20261031.pdf`: French audit summary and figures.
- `r21_r22_experiment.py`, `r21_smooth_geodesic_stability.py`, `test_r21_r22.py`: source and verification tests.
- `r21_sampled_fisher_trials.csv`, `r21_local_optimizer_trials.csv`, `r21_smooth_geodesic_results.json`: R2.1 evidence.
- `r22_operational_payload_trials.csv`, `r22_aggregate.csv`: R2.2 evidence.
- `experiment_results.json`, `SHA256_MANIFEST.json`: aggregate outputs and file checksums.

### What remains

1. A smooth, independently validated generator (or rigorous piecewise-smooth geodesic analysis) with a proper fixed-endpoint geodesic stability experiment. Pointwise Monte Carlo Fisher estimates do not provide derivative control.
2. R2.2 experiment on the **true NG-Stego Algorithm 2** with precommitted security and error limits, equal budgets, actual Fisher distance, independent codebooks, and realistic transforms. Present experiments support only a diagnostic connection, **not** full Reviewer-2 compliance.

The three submission documents were deliberately left unchanged. Cite the new evidence only after a formal manuscript integration/audit.