# Fisher–Rao-Guided Generative Steganography — v1.0

## Article
- Editable manuscript: `paper/main.tex`
- LaTeX class: `elsarticle`
- Intended journal: *Digital Signal Processing*

## Compile
With a standard LaTeX distribution containing `elsarticle`, `amsmath`, `amssymb`, `amsthm`, `mathtools`, `bm`, `booktabs`, `graphicx`, and `hyperref`:

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The source was structurally checked for document/environment balance. A PDF compilation was not independently verified in this packaging session.

## Supplementary material
The repository also contains standalone Python scripts for the geometric simulations S1–S4, an exploratory latent-space VAE–MNIST experiment S5, selected output files and figures.

The S5 script uses a Fisher-preconditioned path; that path is not automatically a minimizing Fisher geodesic. The code and recorded results do not establish an operational Fisher–Rao message-decoding/security superiority over iMEC or Discop.

## Evidence boundary
The article contains a mathematically specified one-bit keyed Gaussian signaling example. Its Gaussian observation-law bounds should not be reinterpreted as tested guarantees for deep generative image steganography.

The presence of supplementary files in this archive does not certify a full numerical rerun or final journal-readiness.

## Archive
The GitHub `article-v1.0` branch may be downloaded as a ZIP using GitHub's source-code archive feature.
