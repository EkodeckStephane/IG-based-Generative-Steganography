# Supplementary Data README

## Associated manuscript

**Fisher--Rao Geometric Optimization and Detection for Generative Steganographic Transport**

This supplementary package provides the Python scripts used to reproduce the numerical simulations and auxiliary tables reported in the manuscript. The scripts cover the geodesic experiments, natural-gradient convergence experiments, curvature estimation experiments, path-comparison experiments, and local Fisher-ball volume estimation for Gaussian-mixture statistical manifolds.

## Package contents

| File | Purpose |
|---|---|
| `run_all.py` | Master script for launching the main simulations S1--S4. |
| `sim_s1_geodesics.py` | Simulation S1: geodesics on the univariate Gaussian statistical manifold. |
| `sim_s2_gradient.py` | Simulation S2: natural gradient versus Euclidean gradient in the diagonal Gaussian case. |
| `sim_s2_nondiagonal.py` | Simulation S2-EXT: natural gradient on the full non-diagonal Gaussian family. |
| `sim_s2_adaptive_comparison.py` | Simulation S2-ADAPTIVE: comparison of NG-Stego, diagonal NG, Adam, and RMSprop. |
| `sim_s3_curvature.py` | Simulation S3: curvature map for a two-component Gaussian mixture model. |
| `sim_s4_path_comparison.py` | Simulation S4: geodesic versus Euclidean straight-line embedding paths. |
| `compute_fisher_ball_volumes.py` | Auxiliary script for estimating local Fisher-ball volumes at representative GMM points. |

## Scientific purpose

The supplementary code supports the following numerical components of the manuscript:

1. **S1 -- Geodesic validation.**  
   Verifies numerical geodesic integration on the univariate Gaussian Fisher--Rao manifold by comparing numerical trajectories with the known Poincare half-plane geodesic structure.

2. **S2 -- Natural-gradient convergence.**  
   Compares Euclidean gradient descent and natural-gradient descent in the diagonal Gaussian case, where the Fisher metric is constant and diagonal.

3. **S2-EXT -- Non-diagonal Fisher metric.**  
   Extends the natural-gradient comparison to the full Gaussian family with both mean and covariance parameters, where the Fisher metric is non-diagonal and non-constant.

4. **S2-ADAPTIVE -- Adaptive optimizer comparison.**  
   Compares exact natural gradient, diagonal natural gradient, Adam, and RMSprop in the full Gaussian setting.

5. **S3 -- Curvature estimation.**  
   Computes coordinate-dependent and coordinate-invariant curvature quantities for a one-dimensional two-component Gaussian mixture model, including scalar curvature and Monte Carlo estimates of minimum sectional curvature.

6. **S4 -- Path comparison.**  
   Compares geodesic and Euclidean straight-line paths in terms of Fisher energy and sequential KL behavior.

7. **Fisher-ball volume table.**  
   Estimates local Fisher-ball volumes for representative GMM parameter points and reports comparisons with Euclidean tangent-space and constant-curvature comparison volumes.

## Requirements

The scripts require Python 3.9 or later.

Required packages:

```bash
pip install numpy scipy pandas matplotlib
```

The following standard-library modules are also used:

```text
argparse
csv
math
os
pathlib
subprocess
sys
time
warnings
```

## Recommended directory structure

Place all scripts in a `code/` directory and run them from that directory:

```text
project-root/
├── code/
│   ├── run_all.py
│   ├── sim_s1_geodesics.py
│   ├── sim_s2_gradient.py
│   ├── sim_s2_nondiagonal.py
│   ├── sim_s2_adaptive_comparison.py
│   ├── sim_s3_curvature.py
│   ├── sim_s4_path_comparison.py
│   └── compute_fisher_ball_volumes.py
├── data/
├── figures/
└── results/
    └── tables/
```

Most simulation scripts write outputs to directories relative to the script location, typically:

```text
../data/
../figures/
```

The Fisher-ball volume script writes by default to:

```text
results/tables/
```

## Running all main simulations

To run all S1--S4 simulations:

```bash
python run_all.py --all
```

If no flag is supplied, `run_all.py` runs all simulations by default.

Equivalent command:

```bash
python run_all.py
```

The master script can also run selected simulations:

```bash
python run_all.py --s1
python run_all.py --s2
python run_all.py --s2-ext
python run_all.py --s2-adaptive
python run_all.py --s3
python run_all.py --s4
```

## Running each script individually

### S1: Gaussian geodesics

```bash
python sim_s1_geodesics.py
```

Expected outputs:

```text
data/s1_geodesic_data.csv
figures/s1_geodesics.pdf
```

### S2: diagonal Gaussian natural-gradient comparison

```bash
python sim_s2_gradient.py
```

Expected output:

```text
data/s2_gradient_data.csv
```

### S2-EXT: full Gaussian non-diagonal Fisher metric

```bash
python sim_s2_nondiagonal.py
```

Expected outputs:

```text
data/s2_nondiag_data.csv
figures/s2_nondiagonal.pdf
```

### S2-ADAPTIVE: NG-Stego versus Adam/RMSprop

```bash
python sim_s2_adaptive_comparison.py
```

Expected outputs:

```text
data/s2_adaptive_data.csv
figures/s2_adaptive.pdf
```

### S3: GMM curvature map

```bash
python sim_s3_curvature.py
```

Expected outputs include:

```text
data/s3_curvature_data.csv
data/s3_scalar_curvature.csv
data/s3_vmin_confidence.csv
data/s3_grid_convergence.csv
figures/s3_curvature.pdf
figures/s3_grid_convergence.pdf
```

### S4: geodesic versus Euclidean path comparison

```bash
python sim_s4_path_comparison.py
```

Expected outputs:

```text
data/s4_path_comparison.csv
figures/s4_path_comparison.pdf
```

### Local Fisher-ball volume table

```bash
python compute_fisher_ball_volumes.py
```

Expected outputs:

```text
results/tables/fisher_ball_volumes.csv
results/tables/fisher_ball_volumes.tex
```

A fully explicit reproducible command is:

```bash
python compute_fisher_ball_volumes.py   --sigma 1.0   --radius 0.15   --n-mc 20000   --n-grid-metric 4001   --seed 123   --outdir results/tables
```

## Optional custom input for Fisher-ball volumes

`compute_fisher_ball_volumes.py` accepts an optional CSV file through:

```bash
python compute_fisher_ball_volumes.py --points representative_points.csv
```

The CSV must contain:

```text
point,pi,mu1,mu2
```

and may optionally contain:

```text
K_comp
```

Example:

```csv
point,pi,mu1,mu2,K_comp
GMM interior A,0.50,-1.00,1.00,-1.0
GMM interior B,0.50,-1.50,1.50,-0.5
Near-boundary GMM,0.10,-0.30,0.30,0.0
```

## Output interpretation

### Data files

The CSV files contain the numerical values used to create manuscript tables and figures. They are intended to allow direct verification of the reported simulation summaries.

### Figures

The PDF figures reproduce the visual results used in the manuscript. Depending on the local environment, figure fonts or layout may vary slightly, but the numerical data should be unchanged when the same seed and parameters are used.

### Fisher-ball volume table

The LaTeX output

```text
results/tables/fisher_ball_volumes.tex
```

can be included in the manuscript using:

```latex
\input{results/tables/fisher_ball_volumes.tex}
```

## Reproducibility notes

1. The scripts use fixed default seeds where stochastic sampling is involved.
2. Monte Carlo estimates may vary slightly if the random seed or sample size is changed.
3. Increasing Monte Carlo sample sizes or integration grids improves numerical stability but increases runtime.
4. The GMM curvature computations rely on finite differences and numerical integration; near degenerate mixture configurations, the Fisher metric may become ill-conditioned.
5. The geodesic shooting methods may fail for difficult endpoint configurations. The scripts record or report failure information where applicable.
6. The Fisher-ball volume estimates are local numerical approximations. They should not be interpreted as exact global geodesic-ball volumes.

## Methodological limitations

The supplementary simulations are designed to support the theoretical claims of the manuscript in low-dimensional, tractable statistical families. They do not constitute an operational validation of a full image-steganography system. In particular:

- the experiments are performed on Gaussian and Gaussian-mixture statistical manifolds;
- deep generative models are discussed theoretically but are not fully benchmarked here;
- Fisher-ball volume estimates are local and small-radius approximations;
- curvature estimates for GMMs are numerical and may be sensitive near singular mixture configurations;
- comparisons with Adam and RMSprop are synthetic optimizer comparisons, not full steganographic system benchmarks.

## Suggested manuscript linkage

The supplementary files correspond to the following manuscript simulations:

| Manuscript item | Supplementary script |
|---|---|
| Simulation S1 | `sim_s1_geodesics.py` |
| Simulation S2 | `sim_s2_gradient.py` |
| Simulation S2-EXT | `sim_s2_nondiagonal.py` |
| Simulation S2-ADAPTIVE | `sim_s2_adaptive_comparison.py` |
| Simulation S3 | `sim_s3_curvature.py` |
| Simulation S4 | `sim_s4_path_comparison.py` |
| Fisher-ball volume table | `compute_fisher_ball_volumes.py` |

## Troubleshooting

### Import errors

Install missing packages:

```bash
pip install numpy scipy pandas matplotlib
```

### Missing output directories

The scripts generally create output directories automatically. If a script fails because of path permissions, create the folders manually:

```bash
mkdir -p data figures results/tables
```

### Long runtime

S3 curvature estimation and Fisher-ball volume estimation can be slower than the other scripts because they use numerical Fisher-metric evaluations, finite differences, and Monte Carlo sampling. Reduce grid sizes or Monte Carlo sample sizes for a quick test, then restore default settings for final reproduction.

### Different numerical results

Small differences can occur because of package versions, floating-point arithmetic, or random sampling. Use the default seeds and parameters for reproducibility.

## Citation

When using this supplementary material, cite the associated manuscript:

```text
Fisher--Rao Geometric Optimization and Detection for Generative Steganographic Transport.
```

## Contact

Corresponding author:

```text
Stéphane Gaël R. EKODECK
stephane-gael.ekodeck@facsciences-uy1.cm
```
