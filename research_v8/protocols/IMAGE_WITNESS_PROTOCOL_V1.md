# Image Witness Protocol v1 — Cachin-Compatible Information-Geometric Steganographic Design

## Status
**Protocol freeze candidate: PASS for controlled witness design.**  
**Natural-image evidence: NOT STARTED.**  
This document freezes the scientific comparison before natural-image headline experiments are run. It is deliberately separate from the manuscript.

## 1. Scientific purpose
The image witness is not the primary novelty. Its purpose is to test one causal proposition of the framework:

> When the cover-source model is uncertain, optimizing only the nominal exact Cachin risk can yield a design that violates the same exact Cachin budget under plausible source shifts, whereas optimizing the same embedding family over a Fisher–Rao source-ambiguity set can preserve that budget by reallocating embedding probability across contexts.

The experiment must distinguish **robust reallocation** from the trivial alternative **uniformly reduce all embedding probabilities**.

## 2. Canonical security convention
Every theorem, implementation, table, and plot uses the original Cachin orientation

\[
D_{\rm KL}(P_C\|P_S).
\]

No result from the rejected manuscripts that used the reverse orientation is imported without rederivation.

## 3. Constructive image model

### 3.1 Cover residual model
Within embedding stratum \(g\), the declared analytical source model is

\[
X_g\sim \mathcal N(0,\sigma_g^2).
\]

The natural-image implementation will estimate local residual scale using a fixed, development-only estimator. The factorized Gaussian model is a **working probabilistic model**, not a claim that natural-image residuals are exactly independent Gaussian variables.

### 3.2 Symmetric ternary embedding channel
Each residual/pixel assigned to stratum \(g\) uses

\[
\Pr(\Delta=+1)=\beta_g,\qquad
\Pr(\Delta=-1)=\beta_g,\qquad
\Pr(\Delta=0)=1-2\beta_g,
\]

with \(0\le\beta_g<1/2\). The induced continuous stego density is

\[
q_{\sigma_g,\beta_g}(x)
=(1-2\beta_g)p_{\sigma_g}(x)
+\beta_g p_{\sigma_g}(x-1)
+\beta_g p_{\sigma_g}(x+1).
\]

The exact **model-level** Cachin cost for a stratum is

\[
C_g(\sigma_g,\beta_g)
=D_{\rm KL}\!\left(
\mathcal N(0,\sigma_g^2)\,\middle\|\,q_{\sigma_g,\beta_g}
\right).
\]

It is evaluated numerically by deterministic Gauss–Hermite quadrature and cross-checked against a quantized-pmf implementation before natural-image reporting.

### 3.3 Utility before coding
The independent ternary-channel entropy is

\[
H_3(\beta_g)
=-2\beta_g\log_2\beta_g
-(1-2\beta_g)\log_2(1-2\beta_g).
\]

For stratum counts \(n_g\), the theoretical embedding-rate envelope is

\[
R_{\rm ideal}(\boldsymbol\beta)
=\frac1N\sum_g n_g H_3(\beta_g).
\]

This quantity is **not** called achieved payload. Achieved payload requires a concrete coder/decoder.

## 4. Exact bridge to Filler–Fridrich / MiPOD local theory
For the Gaussian \(\pm1\) mixture path above, the score with respect to \(\beta\) at zero embedding is

\[
s_\beta(x)|_{\beta=0}
=2\left[e^{-1/(2\sigma^2)}\cosh(x/\sigma^2)-1\right].
\]

Therefore

\[
\boxed{
I_\beta(\sigma,0)
=4\left[\cosh(1/\sigma^2)-1\right]
}
\]

and

\[
D_{\rm KL}(P_\sigma\|Q_{\sigma,\beta})
=\frac12 I_\beta(\sigma,0)\beta^2+O(\beta^3).
\]

For large \(\sigma\),

\[
I_\beta(\sigma,0)
=\frac{2}{\sigma^4}+O(\sigma^{-8}),
\]

hence

\[
D_{\rm KL}(P_\sigma\|Q_{\sigma,\beta})
=\frac{\beta^2}{\sigma^4}+o(\beta^2\sigma^{-4}).
\]

This provides the controlled bridge to the local Fisher/deflection structure used in the Filler–Fridrich lineage and MiPOD. It is a recovery/connection result, not the novelty claim.

## 5. Source-mismatch manifold

### 5.1 Embedding strata
Natural images will be assigned to **K=8 embedding strata** using development-frozen quantiles of estimated log residual scale. This creates eight independent design coordinates

\[
\boldsymbol\beta=(\beta_1,\ldots,\beta_8).
\]

Using eight strata avoids reducing the applied witness to a two-parameter toy while keeping the design interpretable.

### 5.2 Two nuisance modes
Source uncertainty is intentionally lower dimensional than the embedding design. Let \(z_g\) denote the development-frozen standardized center of log-scale stratum \(g\). Model source shift as

\[
\log\sigma'_g
=\log\sigma_g+\delta_0+\delta_1 z_g.
\]

- \(\delta_0\): global residual-scale shift;
- \(\delta_1\): texture-dependent calibration shift.

These nuisance coordinates are fixed before holdout evaluation. They are not retuned to maximize an observed result.

### 5.3 Fisher–Rao geometry of source uncertainty
For a zero-mean Gaussian parameterized by \(\eta=\log\sigma\), Fisher information is exactly 2 per independent observation. Let

\[
a_g=(1,z_g)^\top.
\]

The image-size-normalized nuisance metric is

\[
\boxed{
\bar G
=\frac{2}{N}\sum_g n_g a_g a_g^\top.
}
\]

The declared source ambiguity set is

\[
\boxed{
\mathcal U_r
=\{\delta:\delta^\top\bar G\delta\le r^2\}.
}
\]

The radius \(r\) must be calibrated only from development-source variation or a development bootstrap. Holdout images and holdout source domains may not be used to select \(r\).

## 6. Four primary design comparators
All four operate on the **same K=8 embedding parameterization** whenever mathematically applicable.

### B0 — Local Fisher design
Maximize \(R_{\rm ideal}\) subject to the local quadratic/Fisher approximation of the nominal security budget. This is the direct local-theory comparator.

### B1 — Nominal exact-Cachin design

\[
\max_{\boldsymbol\beta} R_{\rm ideal}(\boldsymbol\beta)
\quad\text{s.t.}\quad
C(0,\boldsymbol\beta)\le\varepsilon.
\]

This isolates the gain of using exact endpoint KL instead of only the local approximation.

### B2 — Uniform safety shrinkage
Start from B1, replace

\[
\boldsymbol\beta\mapsto s\boldsymbol\beta,
\quad 0\le s\le1,
\]

and choose the largest scalar \(s\) satisfying the robust constraint. This is mandatory. It tests whether the proposed method is doing more than merely lowering payload.

### P — Fisher–Rao robust exact-Cachin design

\[
\boxed{
\max_{\boldsymbol\beta}R_{\rm ideal}(\boldsymbol\beta)
\quad\text{s.t.}\quad
\sup_{\delta\in\mathcal U_r}
C(\delta,\boldsymbol\beta)\le\varepsilon.
}
\]

The inner maximization is two-dimensional. Final runs must combine dense boundary coverage, local continuous refinement from the strongest candidates, and convergence/tolerance reporting. A coarse angular grid alone is insufficient for a Q1 guarantee claim.

## 7. External steganographic baselines
The framework comparison above is the causal comparison. External methods provide context and must not be forced into an artificial exact-KL equivalence if their native model does not supply one.

Mandatory external baseline:
- **MiPOD** using the reference DDE implementation or a verified reimplementation against reference outputs.

Additional spatial baselines, provided their reference implementations can be executed under the same image preprocessing:
- **S-UNIWARD**;
- **HILL**.

Their primary purpose is empirical steganalysis context, not to claim that their distortion costs equal Cachin KL.

## 8. Actual message coding
The paper may report \(R_{\rm ideal}\) as a theoretical envelope, but an operational payload claim requires coding.

Primary coding route:
- Syndrome-Trellis Codes (STC), preferably a reference-compatible implementation;
- encode random frozen bitstreams per image;
- verify exact extraction;
- report requested payload, realized payload, coding loss, change rate, and failure rate separately.

The DDE Lab supplies public research implementations of MiPOD and STC-related steganographic algorithms; `pySTC` is a current Python interface derived from the Binghamton STC implementation and can be evaluated for cross-platform use. Licensing and numerical compatibility must be recorded before freezing the implementation.

## 9. Evidence layer A — controlled known-model experiment
Purpose: test the mathematical mechanism with known source parameters and controlled mismatch.

Required grid, frozen before confirmatory results:
- at least 4 heterogeneous residual-scale profiles;
- at least 3 Cachin budgets \(\varepsilon\);
- at least 4 uncertainty radii including \(r=0\);
- source shifts sampled both on and inside the Fisher–Rao ellipse;
- independent Monte Carlo cover draws per profile/condition.

Primary expected pattern, treated as falsifiable rather than guaranteed:
1. local Fisher and nominal exact designs agree only in sufficiently small-embedding regimes;
2. nominal exact designs can violate the exact budget under nonzero source mismatch;
3. robust designs remain within the exact model budget for the declared ambiguity set to numerical tolerance;
4. robust optimization produces a different allocation vector than uniform shrinkage and, where heterogeneity permits, a strictly higher rate at the same robust budget.

If item 4 does not occur beyond negligible numerical differences over the frozen profiles, the design contribution must be weakened or reformulated.

## 10. Evidence layer B — natural-image external validation

### 10.1 Datasets
Primary spatial-domain corpus:
- **BOSSBase 1.01**, 10,000 512×512 grayscale images.

External source corpus:
- **BOWS2**, 10,000 512×512 grayscale images, subject to successful retrieval and preprocessing provenance verification.

BOSSBase is currently absent from `Repare.zip`; the existing BOSSBase directory is empty. Therefore no result from the current package counts as this validation.

### 10.2 Frozen split roles
For the primary corpus, split by image identity before any learned/calibrated quantity is estimated. A candidate allocation is:
- 4,000 development/training images;
- 1,000 validation/calibration images;
- 5,000 final holdout images.

The exact split manifest and random seed must be frozen and hashed before headline evaluation. Cover/stego pairs from one image must never cross split boundaries.

### 10.3 What development data may determine
Development only:
- residual-scale estimator parameters if any are learned;
- K=8 stratum cutpoints;
- standardized \(z_g\);
- nuisance radius \(r\);
- optimization tolerances;
- detector hyperparameters.

The final holdout may only be consumed after these are frozen.

### 10.4 Source-shift evaluation
Two distinct claims must remain separated:

**In-model shifts.** Controlled log-scale nuisance shifts within \(\mathcal U_r\). These test the theorem/model guarantee.

**Out-of-model shifts.** Cross-source BOSSBase→BOWS2 and controlled processing changes. These test empirical external validity only. The Fisher–Rao theorem does not automatically cover them.

## 11. Steganalysis
At least two detector families should be used:

1. **SRM-type rich features + ensemble/SVM classifier** as a classical, CPU-feasible detector family;
2. **SRNet or another reproducible modern deep steganalyzer** as an unseen stronger detector when compute is available.

Aletheia is a reproducible open-source candidate toolbox that includes SRM extraction and SRNet training/inference. Exact version/commit and configuration must be frozen.

The detector used for final evaluation must not participate in optimizing \(\boldsymbol\beta\).

## 12. Primary metrics

### Theoretical/model-level
- nominal exact \(D_{\rm KL}(P_C\|P_S)\);
- worst exact model KL over \(\mathcal U_r\);
- local-Fisher approximation error;
- robust budget violation indicator;
- ideal embedding-rate envelope;
- allocation vector \(\boldsymbol\beta\);
- robust-vs-uniform-shrink rate difference.

### Operational coding
- requested payload (bpp);
- realized payload (bpp);
- coding loss relative to ideal entropy;
- extraction BER / exact-decode success;
- modification rate.

### Empirical security
- balanced detection error or error probability under equal priors;
- ROC AUC as secondary summary;
- 95% paired/bootstrap intervals over images;
- source-specific and pooled estimates kept separate.

PSNR/SSIM may be descriptive but are not evidence of steganographic security.

## 13. Statistical protocol
- independent statistical unit: source image, not repeated detector evaluation;
- every proposed-vs-baseline comparison uses the same underlying covers whenever possible;
- use paired bootstrap confidence intervals over images for paired performance differences;
- report effect sizes and intervals, not isolated p-values;
- multiplicity correction for families of confirmatory pairwise detector comparisons;
- technical repetitions are used only for runtime variability, never as independent security samples;
- all failed embeddings/decodes remain counted and reported.

## 14. Required ablations
1. local Fisher vs exact nominal KL;
2. exact nominal vs robust exact;
3. robust exact vs uniform safety shrinkage;
4. source uncertainty radius \(r\);
5. one nuisance mode (global only) vs two nuisance modes;
6. theoretical entropy vs realized STC payload;
7. model-level guarantee vs unseen empirical steganalysis.

Ablations that change multiple factors simultaneously are not sufficient for causal attribution.

## 15. Hard NO-GO conditions
The applied contribution does not pass if any of the following occurs:

1. robust design violates its declared exact model-KL budget after high-resolution/adversarial inner-max verification;
2. its apparent gain is reproduced by uniform scalar shrinkage within negligible tolerance across the frozen controlled profiles;
3. local-Fisher and exact-KL code are mislabeled as equivalent outside the local regime;
4. achieved payload is claimed without a message coder/decoder;
5. natural-image test data influence stratum construction, radius calibration, model tuning, or method selection;
6. only PSNR/SSIM or a weak structural detector supports the security claim;
7. source-model guarantees are generalized to arbitrary real cover sources without evidence;
8. the manuscript calls generic Fisher–Rao distributional robustness itself novel;
9. code/data/tables disagree on KL orientation, budget, radius, payload, or sample counts.

## 16. Controlled sanity result already available — NOT headline evidence
Frozen two-stratum computational sanity case:
- \(\sigma=(1.2,2.2)\);
- counts \((1200,800)\);
- \(\varepsilon=2\times10^{-4}\) nat/pixel;
- normalized source FR radius \(r=0.12\).

Using high-resolution verification of the two-dimensional boundary:

| design | ideal rate (bpp) | nominal exact KL | worst exact KL |
|---|---:|---:|---:|
| local-Fisher | 0.473276 | 0.000190196 | 0.000282529 |
| nominal exact | 0.481937 | 0.000200000 | 0.000297171 |
| uniform shrink | 0.416731 | 0.000134286 | ~0.000200000 |
| robust exact | 0.418887 | 0.000138386 | ~0.000200000 |

The robust allocation is not a scalar multiple of the nominal allocation. In this single sanity instance its ideal-rate advantage over uniform shrinkage is only about **0.52%**, so this result proves computational non-equivalence but **does not yet establish a practically meaningful gain**. The confirmatory controlled grid must determine whether the effect is scientifically material.

## 17. Pre-registration decision
This protocol is frozen before natural-image headline results. Parameter values that remain to be set from development data (stratum cutpoints, \(z_g\), radius, exact train/validation identities) must be recorded in a versioned manifest before opening the final holdout. Any later protocol change must create a new exploratory branch and cannot silently replace this confirmatory specification.
