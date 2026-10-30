# Fisher–Rao-Guided Generative Steganography — v1.0

## Contents

- `main.tex`: full editable LaTeX source, using Elsevier's `elsarticle` class.
- `VERSION`: article version identifier.

## Compilation

Install a TeX distribution containing `elsarticle`, `amsmath`, `amssymb`, `amsthm`, `mathtools`, `bm`, `booktabs`, `graphicx`, and `hyperref`. Then run:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

**Verification boundary:** LaTeX environment pairing and document delimiters have been checked; successful compilation has not been independently confirmed.

## Scientific scope

The manuscript contains a specified one-bit keyed Gaussian signaling example with exact receiver error and a KL-security upper bound under its stated assumptions. It does not claim operational security for a high-dimensional generative image codec. The VAE–MNIST example is described as exploratory, not an end-to-end message-decoding experiment.

The original 8.14 MB archive named `manuscript_source.zip` was located in the user's file library but could not be extracted by the available file-processing runtime. Consequently, this package contains the coherent v1.0 LaTeX manuscript assembled from the editable draft, **not a verified in-place edit of that original archive**. Source-to-source equivalence and final journal layout must be checked against the canonical submission.

The independent simulations and image datasets are intentionally kept outside this article-only ZIP; they remain in the project's main GitHub branch and existing Drive evidence folders.
