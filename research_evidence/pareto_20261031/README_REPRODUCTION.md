# NG-Stego Algorithm 2 — Pareto experiment, 31 October 2026

**Study:** DSP-D-26-02810, Version 1.0. This is a **new exploratory experiment**, not the original S5 experiment. The three submission documents are **not** updated with these findings.

## Scientific scope and limitations

- Fixed checkpoint: `data/s5_vae_mnist.pt` (SHA-256 `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`). Bernoulli(784) likelihood, learned MNIST VAE, 2-D latent.
- Pseudocode Algorithm 2 implemented with sampled Fisher score outer products and exact KL gradient. A diagonal stabilizer and Armijo backtracking are numerical safeguards that the paper's schematic pseudocode does not explicitly prescribe.
- 6 distinct random codebooks; 3 for detector training, 3 for testing; none contains the cover point. 2-bit message, 100 cover / 100 stego images per codebook for each method.
- Three RBF-SVM detection metrics: image pixels, features of public VAE encoder, and a **white-box oracle** likelihood-ratio test that knows the final parameter distributions. The oracle is *not* a realistic claim about an attacker who lacks secret codewords.
- Results are **not** about natural images or the native original iMEC / Discop media applications. They reflect adapted implementations on the same Bernoulli channel with their own decoders.
- Costs are explicitly separated: target-codeword precomputation for optimization, and per-image encoding for iMEC/Discop.
- Path endpoints are not security-certified. Target-KL loss alone does not control cover-to-stego KL; the experiments show this limitation. Cross-codebook generalization is tested, but only within one fixed model and 6 codebooks.

## Reproduce

```bash
python -m pip install numpy scipy scikit-learn torch matplotlib reportlab
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python pareto_algorithm2_v1.py --suite standard --n 100 --bootstrap 160
python pareto_algorithm2_v1.py --suite earlystop --n 100 --bootstrap 160
python evaluate_common_channel_baselines.py
python test_pareto_algorithm2_v1.py
python build_report.py
```

To regenerate baseline data from scratch, delete the generated `cache_iMEC_*.npz` and `cache_Discop_*.npz` files first. The cache is read only by the baseline script. `r27_algorithm2_direct_v1.py` and `benchmark_s5_comparison.py` are included at their original paths; the latter requires `_imec_reference/src`, `data/s5_vae_mnist.pt`, and the VAE implementation. The baseline runner calls the original iMEC source classes through a documented Bernoulli-medium adaptation.

## Files

- `pareto_algorithm2_v1.py` — direct numerical Algorithm 2 vs exact Fisher vs Euclidean, including zero-update control and fixed-step sweeps.
- `evaluate_common_channel_baselines.py` — adapted iMEC and Discop with same cover channel and a 2-bit payload; method-specific detectors and independent codebook-held-out test split.
- `test_pareto_algorithm2_v1.py` — check codeword separation, exact split, gradient, optimizer monotonicity, Pareto recomputation, data counts and baseline consistency.
- `pareto_algorithm2_results.json` / `_earlystop.json` — full runs and per-codebook measurements; CSVs summarise the results.
- `pareto_adapted_baselines.json` — adapted baselines including per-codebook AUCs and decoder reliability.
- `RAPPORT_PARETO_ALGORITHME2.md/.pdf`, PNG figures — analysis; no favorable results have been invented.

## Acceptance-review implications

The data **do not** establish that Fisher dominates Euclidean optimization in payload reliability, distortion, runtime and undetectability. Point R2.3 and point R2.7 remain **partially resolved** despite the direct experimental strengthening. A separate follow-up must compare native iMEC/Discop pipelines on their own channels, evaluate additional independent CNN-type detectors, and quantify robustness and confidence across independent image generators if the article attempts operational superiority claims.