# Reproducibility package — Fisher–Rao-guided generative steganography

This repository contains the source code and results needed to reproduce the
numerical experiments of the paper
**"Fisher–Rao-Guided Generative Steganography: Geodesic Embedding and Detection
Analysis"** (submitted to *Digital Signal Processing*).

## Contents

```
Supplementary_Data/     Python source code for all experiments
figures/                Generated figure PDFs
  s1_geodesics.pdf
  s2_nondiagonal.pdf
  s2_adaptive_comparison.pdf
  s4_path_comparison.pdf
  s5_latent_paths.pdf
  s5_image_strip.pdf
  s5_detector_profile.pdf
data/                   Generated numerical outputs
  s5_vae_results.csv
  s5_vae_summary.json
  s5_vae_mnist.pt       trained VAE checkpoint for Simulation S5
```

## Prerequisites

- Python 3.9 or newer
- PyTorch and torchvision (for Simulation S5 only)
- NumPy, SciPy, Matplotlib

A minimal environment can be installed with:

```bash
pip install torch torchvision numpy scipy matplotlib
```

## Reproducing the results

All experiments are standalone scripts in `Supplementary_Data/`:

```bash
cd Supplementary_Data
python sim_s1_geodesics.py
python sim_s2_gradient.py
python sim_s2_nondiagonal.py
python sim_s2_adaptive_comparison.py
python sim_s3_curvature.py
python sim_s4_path_comparison.py
python sim_s5_vae_mnist.py          # downloads MNIST automatically
python compute_fisher_ball_volumes.py
```

Alternatively, run the whole suite:

```bash
cd Supplementary_Data
python run_all.py
```

### Outputs

- Each `sim_s*.py` writes its figures to `../figures/` and numerical outputs to
  `../data/`.
- `sim_s5_vae_mnist.py` also saves the trained VAE checkpoint to
  `../data/s5_vae_mnist.pt` and a results table to
  `../data/s5_vae_results.csv`.

The committed figure PDFs and CSV/JSON files correspond to the results reported
in the paper.

## Notes

- Simulation S5 (MNIST VAE) trains a small variational autoencoder from scratch.
  On a CPU this takes a few minutes; training can be accelerated with a GPU by
  installing the CUDA version of PyTorch.
- The raw MNIST dataset is downloaded automatically on first run and stored in
  `../data/MNIST/`; it is excluded from version control by `.gitignore`.


## Revised DSP submission: evidence scope (30 October 2026)

The revised manuscript distinguishes three independent tracks: (1) matched-channel MNIST-VAE S5 diagnostics, (2) native upstream iMEC/Discop runs, and (3) controlled complementary Discop and steganalysis runs. These tracks use different generators, datasets, and experimental objectives and must **not** be compared as if they were a single matched-carrier benchmark.

The native/controlled campaign is documented in the Google Drive evidence folder: https://drive.google.com/drive/folders/1xr3gYO8QTm7MoCLRVxFmfAMjzZr4PGhu . Protocol: `v2.1-one-shot-500-20261028` (master seed 20261014). The exported archive manifest records 5,320 files, 270,175,710 bytes, SHA-256 `184c45db08e420bfbfccbd09dc069f015e03481d1e77008c17e90821319d7c45`. This checksum is reported from the provided manifest and has not been reverified against the external archive.

Native iMEC GPT-2/WikiText-103 text: 100/100 decodes. Native Discop Transformer-XL/IMDb text reports 4.14291 bits/token over 100,000 tokens; ImageGPT/CelebA image reports 1.725796875 bits/token over 256,000 tokens. The native Discop statistics path uses nondeterministic `os.urandom` seeds. Controlled Discop text and image tests report 100/100 and 500/500 exact decodes respectively; image context equality is in quantized tokens, not original RGB bytes.

**Important validation limitation:** In the controlled 500-pair five-fold steganalysis study, SRM/FLD macro AUC is 0.46119 and ResNet18 macro AUC is 0.52278, but the mandatory positive-control health check passes for SRM/FLD (AUC 0.98407) and fails for ResNet18 (AUC 0.54156 against a prespecified 0.8 threshold). The campaign records `scientific_ready=false`; those detector results cannot support security conclusions. Native iMEC image evaluation was skipped because the ImageTransformer checkpoint was unavailable.

The full revised manuscript and response to reviewers are supplied as a separate submission package; this README update does not claim the repository already contains all revised code, images or figures.
