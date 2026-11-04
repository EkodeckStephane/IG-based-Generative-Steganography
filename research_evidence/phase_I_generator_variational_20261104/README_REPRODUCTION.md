# Phase I A1–A3 — reproducibility and scientific scope

Project: **DSP-D-26-02810 / Version 1.0**. Research date: **2026-11-04**.

**Official article, response and cover letter have not been edited by this package.** The source manuscript snapshot under `article/` is included only for provenance and must never replace the submission source.

## Files

- `source/A1_A3_VARIATIONAL_NOTE.tex`: English mathematical research note, theorem, proof and prior-art boundary; compiled in `results/A1_A3_VARIATIONAL_NOTE.pdf`.
- `AUDIT_PHASE_I_A1_A3.md` and `results/RAPPORT_SCIENTIFIQUE_PHASE_I_A1_A3.pdf`: French scientific assessment.
- `source/phase1_variational_experiment.py`: fully executed original experiment (Bernoulli ring + original MNIST-Bernoulli VAE).
- `source/test_phase1.py`: 9 numerical consistency tests.
- `source/sim_s5_vae_mnist.py`, `source/s5_vae_mnist.pt`: exact original project VAE definition and checkpoint. Model/checkpoint are included from the latest audited Version 1.0 ZIP; not retrained or modified.
- `results/phase1_results.json`, `results/phase1_summary.csv`, `figures/`: output of the experiment.
- `logs/numerical_run.log`, `logs/unit_tests.log`, `logs/latex_note_pass2.log`: execution/compilation evidence.
- `SHA256_MANIFEST.json`: exact SHA256 of files in this archive.

## Reproduction

From extracted archive root (Python 3.13 tested; virtual environment recommended):

```bash
pip install numpy==2.3.5 scipy==1.17.0 matplotlib==3.10.8 torch==2.10.0 torchvision==0.25.0
cd source
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python phase1_variational_experiment.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest test_phase1.py -v
```

LaTeX (pdflatex and LaTeX packages required):

```bash
cd source
pdflatex -interaction=nonstopmode -halt-on-error -output-directory ../results A1_A3_VARIATIONAL_NOTE.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory ../results A1_A3_VARIATIONAL_NOTE.tex
```

The checkpoint SHA-256 must equal `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`; the loader rejects mismatches. With CPU and pinned versions, all 9 automated tests passed. The VAE solver is a **numerical feasible-path search**, not a provably globally convergent algorithm. Reruns on different package versions can show small floating-point or optimization differences.

## Mathematical status / audit restrictions

A2 proof applies to a compact connected C3 embedded regular submanifold **without boundary** of the interior of a finite simplex. It proves the *minimal value limit* and compactness/convergence of global discrete minimizers, not algorithm convergence. Existing general variational discretization research must be credited; prior art review remains targeted, not exhaustive.

A3 exact generator-distance decomposition and toy circle model are analytical. The VAE is piecewise-ReLU and does not satisfy the A2 smoothness hypotheses globally. In VAE tests only the **ambient lower distance is exact**. Any path length is an intrinsic upper bound *in mathematics*, but the decimal outputs are high-order quadrature estimates, not interval-arithmetic certified upper bounds. `generator_excess_squared_interval` is an estimate, not a formal confidence interval. This study does not establish endpoint security, decoder reliability, superiority over iMEC/Discop or a new practical embedding method.

## Original related sources

- F. Papangelou (2000), DOI `10.1214/aoap/1019487616`.
- D. Pavlichin, T. Weissman (2016), DOI `10.1109/ISIT.2016.7541365`.
- M. Rumpf, B. Wirth (2015), DOI `10.1093/imanum/dru027`.
- J. Maas, M. Rumpf, C. Schönlieb, S. Simon (2015), DOI `10.1051/m2an/2015043`.
- F. Nielsen (2024), DOI `10.1016/bs.host.2024.06.003`.

## Release gate

Do not merge into the article before: independent proof review, tight reliable estimates of VAE d_G, codebook-held-out predictive evidence beyond conventional diagnostics, and independent reproduction of the model/detectors. GitHub public research source should match the manifest, while the submission Version 1.0 should remain unchanged.
