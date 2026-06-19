# Digital Signal Processing Maintenance Report

Date: 2026-06-19

## Target

The manuscript has been retargeted from the previous Elsevier/Information
Sciences framing to a new submission package for Elsevier's `Digital Signal
Processing`.

## Editorial Repositioning

- The title now foregrounds the application:
  `Fisher--Rao-Guided Generative Steganography: Geodesic Embedding and
  Detection Analysis`.
- The abstract now starts from generative/coverless steganography as a
  statistical signal-generation problem.
- The keywords now target DSP scope:
  generative steganography, statistical signal processing, detection theory,
  Fisher--Rao metric, natural-gradient optimization.
- The introduction now states explicitly that Fisher--Rao geometry is a tool
  for measuring statistical sensitivity in generated signals, not the paper's
  standalone mathematical destination.
- The contribution section was rewritten around:
  detection-aware generative embedding, sequential detectability path cost,
  NG-Stego optimization, curvature-based robustness diagnostics,
  Neyman--Pearson detection interpretation, and reproducible numerical
  validation.
- Key theorem/corollary blocks now include short `Steganographic consequence`
  paragraphs connecting the mathematical result to embedding, robustness, and
  detection.
- The conclusion now describes the work as a Fisher--Rao-guided
  signal-processing framework for generative steganographic embedding and
  detection.

## Cover Letter

- `cover_letter.tex` was replaced by a clean new-submission letter for
  `Digital Signal Processing`.
- The letter no longer mentions Information Sciences, previous manuscript
  numbers, appeal history, duplicate-submission checks, or resubmission.
- It positions the work under statistical signal processing, detection theory,
  information security, and mathematical methods for signal-processing models.

## Verification

- Article compiled with:
  `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Cover letter compiled with:
  `pdflatex`.
- Generated PDFs:
  `IG_STEGO_PAPER.pdf` -- 25 pages.
  `cover_letter.pdf` -- 2 pages.
- Final log audit found no unresolved citations, unresolved references, fatal
  LaTeX errors, emergency stops, or rerun-required warnings.
- BibTeX reports only two bibliographic metadata warnings for empty page fields:
  `imec2022` and `kingma2014vae`.
- The CAS double-column article still contains overfull/underfull box warnings,
  mostly from dense mathematical display content and narrow two-column layout.
  These are layout warnings, not compilation or reference failures.

## Fact, Cross-Reference, and Label Audit

- All `algorithm`, `figure`/`figure*`, and `table`/`table*` environments were
  checked for both captions and labels.
- Inventory:
  3 algorithms, 4 figures, and 8 tables.
- All corresponding labels are cited at least once in the manuscript:
  `alg:geodesic_solver`, `alg:ng_stego`, `alg:ng_stego_constrained`,
  `fig:s1`, `fig:s2ext`, `fig:s2adaptive`, `fig:s4`,
  `tab:novelty`, `tab:s1`, `tab:s2`, `tab:s2ext`, `tab:s2adaptive`,
  `tab:s3revised`, `tab:fisher_ball_volumes`, and `tab:s4`.
- The S4 table is now explicitly cited in the results paragraph, not only in a
  figure caption.
- Numeric cross-checks were applied to the simulation text:
  S3 scalar-curvature range now matches the table maximum (`326.6`), and S4
  figure/table wording now consistently reports 49 successful endpoint pairs
  out of 50 trials.
- Over-absolute novelty claims were softened to defensible formulations such as
  "we are not aware of..." and the prior-work comparison was narrowed to the
  precise missing element: no Fisher--Rao trajectory-level embedding cost with
  natural-gradient optimization for that cost.

## Submission Note

This DSP package should be treated as a new journal submission. Do not include
the previous Information Sciences response letter or appeal correspondence in
the submission files unless a journal explicitly requests submission history.
