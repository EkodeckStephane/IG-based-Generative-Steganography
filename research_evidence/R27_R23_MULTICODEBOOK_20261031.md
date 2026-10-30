# R2.7 / R2.3 - Four independently seeded codebooks (31 October 2026)

**Status: audited exploratory evidence; not an accepted claim of general NG-Stego security.** These findings are **unfavorable to the concealment of the path-based mechanism in the tested setting**. The official submission manuscript is *not* silently replaced by this separately scoped campaign.

## Design

- Model: same public 2-D-latent Bernoulli MNIST-VAE checkpoint as submission, SHA-256 `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`.
- Four separately seeded random four-point latent codebooks, seed values 5101, 5203, 5309, 5413; all have four distinct message codewords and **exclude the cover parameter z0=(0,0)**.
- 2 bits/message, 80 covers and 80 stegos per codebook per split; independent train and test sets. Detector train: **three books, 480 images**. Test: **one completely held-out book, 160 images**. Repeat over all four books.
- Algorithm 2 MC Fisher score estimator (256 model draws/update), exact-Fisher and Euclidean ablations, plus iMEC/Discop adapted to same fixed Bernoulli channel. 100 optimizer iterations, damping 1e-3 and KL objective tolerance 1e-5.
- Pixel logistic regression, pixel RBF-SVM, public-encoder Fisher/latent RBF-SVM, fusion RBF-SVM. No private path or message given to detectors. 300 stratified bootstrap resamples give descriptive 95% AUC intervals. Positive-control AUC=1.0.
- This is **not** the original class-mean S5 nor the native complete iMEC/Discop media pipelines. Baselines do not depend on the selected latent codebook, so held-out-book transfer is primarily a path-method question.

## Results

| Method | Decoded by ML-or-native receiver | Decoded by public VAE encoder | Targets converged | Held-out pixel RBF-SVM AUC, mean (range) |
|---|---:|---:|---:|---:|
| Algorithm 2 MC Fisher | 318/320 | 198/320 | 8/16 | 0.9519 (0.8661-1.0000) |
| Exact-Fisher ablation | 318/320 | 202/320 | 8/16 | 0.9535 (0.8675-1.0000) |
| Euclidean gradient ablation | 319/320 | 260/320 | 12/16 | 0.9781 (0.9319-1.0000) |
| iMEC channel adaptation | 320/320 | N/A | N/A | 0.5013 (0.4311-0.5483) |
| Discop channel adaptation | 320/320 | N/A | N/A | 0.4926 (0.4647-0.5306) |

**Important interpretation:** The ML receiver for trajectory methods is an *idealized* receiver with the four optimized output distributions. It is not interchangeable with the public VAE encoder receiver. The different methods' native coding mechanisms and distortions are not assumed identical. The nonlinear RBF SVM is not uniformly better than logistic regression; both were evaluated.

Algorithm 2 held-out RBF-SVM pixel AUCs: R1=0.8661 [0.7991,0.9252], R2=0.9845 [0.9699,0.9953], R3=0.9569 [0.9201,0.9842], R4=1.0000 [1.0000,1.0000]. No null cover codeword, hence the earlier 0.875 mixture-AUC ceiling does not apply.

## Files and exact reconstruction

All six code/data files are stored in this folder as `.gz` using unchanged bytes. Run:

```bash
python research_evidence/extract_multicodebook_sources.py
# To reproduce, obtain the manuscript project's complete companion bundle,
# containing Version_1.0/benchmark_s5_comparison.py, data/s5_vae_mnist.pt,
# and _imec_reference/src from the pinned upstream checkout.
DSP_PROJECT_ROOT=/path/to/submission-root OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python research_evidence/run_multicodebook.py --train 80 --test 80 --MC 256 --steps 100 --bootstrap 300
python research_evidence/audit_multicodebook.py
```

The exact source `run_multicodebook.py.gz` has Git blob SHA `888b8178c2ad5f00e75401dfe3e21d0d05bf03e1`; the full JSON gzip SHA is `7a4d4da2637121a5fa15435f8a524c91ce940627`. Both match independently computed local hashes.

**Reproducibility limit:** the public repository does *not yet* contain the complete benchmark wrapper and pinned upstream adapters needed for a GitHub-only end-to-end rerun. They are present in the separately delivered full submission ZIP. Do not call this a fully standalone GitHub experiment until those dependencies are added.

R2.3 and R2.7 **remain partially satisfied**. This experiment demonstrates a detectable vulnerability under an informed public-encoder threat model, not security; it does not perform minimax adversarial embedding training or validate across generators.
