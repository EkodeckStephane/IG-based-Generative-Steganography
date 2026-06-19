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
cas-dc.cls              Elsevier CAS double-column class file
cas-common.sty          Elsevier CAS common style file
cas-model1-num-names.bst  Elsevier bibliography style
cas-refs.bib            Bibliography database
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
