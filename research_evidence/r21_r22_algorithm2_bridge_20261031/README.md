# R2.1/R2.2 — Actual Algorithm 2 + local Fisher geometry + public decoding

**31 October 2026 | Supplementary research evidence, not yet part of the DSP-D-26-02810 manuscript.**

The trained MNIST Bernoulli VAE has a 2-D latent and a 784-Bernoulli decoder; the checkpoint SHA-256 is `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`.

## R2.1: what was proved and checked

Inside one common affine ReLU activation cell of the decoder, the exact Bernoulli KL objective in the Algorithm-2 core obeys:

```
gradient_z KL(P_z || P_target) == F(z) @ (z - target)
```

Therefore, in this **local cell**, an undamped unit-step exact-Fisher update reaches the target in one step. For a positive definite sampled FIM and relative error `delta = || F^-1/2 (Fhat-F) F^-1/2 ||_2 < 1/2`, the undamped full step contracts the Fisher error norm by a factor at most `delta/(1-delta)`. This does **not** automatically prove convergence for the safeguarded implementation (damping + Armijo), across ReLU boundaries, or for arbitrary GAN/diffusion generators.

A standalone verification script (`verify_relu_cell_fisher_standalone.py`) produced max relative identity residual **1.625e-13**, exact-Fisher target error **6.483e-17**. Six targets and 8 repeats at each of N=32,128,512,2048: **182/192** cases met `delta<.5`; **0 conditional bound violations**.

The empirical pointwise FIM-error results near cover, target and actual optimized parameters are recorded in `joint_r21_MC_at_targets.csv`. The changes of activation masks along the **straight chords** from cover to the optimized points are in `joint_r21_ReLU_kinks.csv`: these are not observations of actual optimizer iterate crossings.

## R2.2: public receiver and model-aware steganalyst

Two independent experiments:

1. Six 2-bit codebooks, 3 development + 3 reporting, 100 held-out payload images per codebook. Real Algorithm-2 sampled Fisher (N=256, <=80 iterations), exact-Fisher and Euclidean ablations. Public VAE receiver uses the original target codebook in L2 and the fixed-cover Fisher quadratic norm.
2. Fresh separately seeded 1,2,3,4-bit codebooks, 4 codebooks per payload, 2 development + 2 held-out, 128 test images per held-out codebook and method; Algorithm 2 vs Euclidean. All payload codewords exclude the cover.

**Two-bit common experiment, 300 held-out stego messages per method:**

| Method | Target KL convergence | Public quadratic-Fisher decode | Sufficient packing-certificate events | Exact model-informed AUC |
|---|---:|---:|---:|---:|
| Algorithm 2 (sampled Fisher) | 9/12 | 251/300 | 233/300 | 1.000 |
| Exact-Fisher ablation | 9/12 | 249/300 | 233/300 | 1.000 |
| Euclidean gradient descent | 12/12 | 299/300 | 281/300 | 1.000 |

**Independent variable-payload experiment, 256 held-out stego images per k and method:**

| Bits | Algorithm-2 public decode | Euclidean public decode | Oracle AUC Algorithm-2 |
|---:|---:|---:|---:|
| 1 | 192/256 | 256/256 | 1.000 |
| 2 | 222/256 | 254/256 | 1.000 |
| 3 | 196/256 | 227/256 | 0.997 |
| 4 | 185/256 | 221/256 | 1.000 |

The packing certificate is the **conditional** statement that a public latent estimate within half the minimum codeword separation in the constant norm F(cover) must decode correctly. The measured fraction of such events is not a universal estimation guarantee, and the quadratic norm is not the **global Fisher-Rao geodesic distance**.

The `<=5%` one-sided error requirement and model-informed AUC `<=0.60` exploratory security requirement were **never met simultaneously** by any held-out codebook. AUC close to 1 means an adversary can distinguish the model-generated stego images. **No positive secure operational capacity or NG-Stego superiority has been established.**

## Reproducibility / current GitHub scope

This folder contains verified experiment CSVs, the local cellwise verification script and this protocol. The local cellwise test needs the VAE checkpoint as its command argument:

```bash
python verify_relu_cell_fisher_standalone.py /path/to/s5_vae_mnist.pt
```

The **full audited experiment sources**, pinned checkpoint, source of the Algorithm-2 implementation, supporting LaTeX proof, three-page French report, complete JSON outputs and seven passing regression tests are delivered together in the downloadable research ZIP from the ChatGPT revision workspace.

**The GitHub folder does not yet contain the full independent end-to-end evaluator or checkpoint. Repository-only reproduction of every reported statistic is not certified.** The previous Pareto and Algorithm-2 code published under `research_evidence/` is related but not a drop-in substitute for the bundled full source.

The journal manuscript, response and cover letter remain unchanged until editorial integration. This work is a transparent research diagnostic, **not** a claim that Reviewer 2 points 1 and 2 are fully satisfied.
