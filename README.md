# Fisher–Rao-Guided Generative Steganography

This repository contains the source code, data, and manuscripts for the paper
**"Fisher–Rao-Guided Generative Steganography: Geodesic Embedding and Detection
Analysis"** submitted to *Digital Signal Processing*.

## Repository structure

- `IG_STEGO_PAPER.tex` / `IG_STEGO_PAPER.pdf` — main (non-anonymized) manuscript.
- `cas-refs.bib`, `cas-dc.cls`, `cas-common.sty`, `cas-model1-num-names.bst` —
  LaTeX class/style/bibliography files.
- `figures/` — figure PDFs used by the main manuscript.
- `ANO/` — double-anonymized submission package (flat directory with source,
  style files, and figures).
- `Supplementary_Data/` — Python scripts that reproduce all numerical
  experiments (S1–S5, S2-EXT, S2-ADAPTIVE) and curvature computations.
- `data/` — generated results and trained model checkpoint for Simulation S5.
- `cover_letter.tex` / `response_to_editor.tex` — submission correspondence.

## Compiling the manuscript

From the repository root:

```bash
pdflatex IG_STEGO_PAPER.tex
bibtex IG_STEGO_PAPER
pdflatex IG_STEGO_PAPER.tex
pdflatex IG_STEGO_PAPER.tex
```

For the anonymized version, compile inside `ANO/` in the same way.

## Reproducing the simulations

The `Supplementary_Data/` folder contains one script per experiment:

- `sim_s1_geodesics.py` — geodesics on the univariate Gaussian manifold.
- `sim_s2_gradient.py` — natural gradient on a diagonal Gaussian.
- `sim_s2_nondiagonal.py` — NG-Stego on a full Gaussian.
- `sim_s2_adaptive_comparison.py` — NG-Stego vs. Adam/RMSprop.
- `sim_s3_curvature.py` — curvature maps for Gaussian mixtures.
- `sim_s4_path_comparison.py` — geodesic vs. Euclidean path energy.
- `sim_s5_vae_mnist.py` — Fisher-guided embedding in a learned MNIST VAE.
- `compute_fisher_ball_volumes.py` — Fisher-ball volume checks.
- `run_all.py` — convenience runner for the whole suite.

Simulation S5 requires PyTorch and torchvision; the script downloads MNIST
automatically on first run.

## Data availability

The Python source code, simulation data, and trained model checkpoints for all
experiments are available in this repository. See the article's
**Availability of Data and Materials** statement for the permanent URL.
