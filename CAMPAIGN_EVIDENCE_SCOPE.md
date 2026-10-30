# DSP revision evidence scope — 2026-10-30

Manuscript: DSP-D-26-02810, *Fisher–Rao-Guided Generative Steganography: Geodesic Embedding and Detection Analysis*.

Evidence folder: https://drive.google.com/drive/folders/1xr3gYO8QTm7MoCLRVxFmfAMjzZr4PGhu

Protocol: v2.1-one-shot-500-20261028, master seed 20261014.

| Track | Evidence | Scope |
| --- | --- | --- |
| Matched S5 | MNIST-VAE; same Bernoulli pixel channel for path codes, iMEC and Discop adapters | Different from native generators |
| Native iMEC | GPT-2/WikiText-103; 100/100 exact text decodes | ImageTransformer native image run unavailable (checkpoint missing) |
| Native Discop | Transformer-XL/IMDb 4.14291 bits/token (100,000 tokens); ImageGPT/CelebA 1.725796875 bits/token (256,000 tokens) | Native statistics, not matched-channel image security; os.urandom internal |
| Controlled Discop | 100/100 exact text decodes, 500/500 exact image decodes | Quantized token image context, not original RGB equality |
| Controlled steganalysis | 500 source pairs, five paired folds; SRM/FLD macro AUC 0.46119, ResNet18 macro AUC 0.52278 | Not security-validated |

**Prespecified detector health gate:** positive-control macro AUC must be >= 0.8. SRM/FLD passes (0.98407), ResNet18 fails (0.54156). The campaign declares scientific_ready=false. Do not use the controlled steganalysis results as security confirmation or to claim that any method is undetectable.

The evidence export manifest reports 5,320 files, 270,175,710 bytes, sha256 `184c45db08e420bfbfccbd09dc069f015e03481d1e77008c17e90821319d7c45`. The archive was not separately downloaded and rehashed in this update.

The native, controlled and matched-channel tracks must never be conflated. This file summarizes evidence and does not itself bundle 270 MB of experimental data.