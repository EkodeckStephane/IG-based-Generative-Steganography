# IG-based Generative Steganography — Cachin-Compatible Information-Geometric Security

This branch contains the current reproducible research materials for a **Cachin-compatible information-geometric framework for steganographic security and robust embedding design**.

Repository: **https://github.com/EkodeckStephane/IG-based-Generative-Steganography**  
Research branch: **`cachin-ig-robust-v8`**

## 1. Context

Information-theoretic steganography classically measures security through the relative entropy between the cover and stego distributions. In Cachin's formulation, a stegosystem is perfectly secure when

\[
D_{\mathrm{KL}}(P_C\Vert P_S)=0,
\]

and \(\varepsilon\)-secure when the same divergence does not exceed a prescribed budget. This scalar criterion is exact and remains the security constraint adopted in this work.

Local steganographic Fisher information provides a complementary tangent description of how detectability changes for infinitesimal embedding rates. Modern practical steganography, however, must also contend with **cover-source mismatch**: the true cover distribution may differ from the nominal source model used during sender design.

The project therefore asks how to preserve exact Cachin security while adding an intrinsic geometric description of **how that security varies with the cover source itself**, and whether this additional information can be exploited to construct more robust embedding allocations.

## 2. Problem

A single Cachin value can certify the nominal pair \((P_C,P_S)\), but it does not by itself describe how rapidly the security level changes when the cover-source distribution moves away from the nominal model.

Consequently, two designs may satisfy exactly the same nominal security constraint,

\[
D_{\mathrm{KL}}(P_C\Vert P_{S,A})
=
D_{\mathrm{KL}}(P_C\Vert P_{S,B})
=\varepsilon,
\]

while responding very differently to an admissible source shift. The practical question is then not whether Cachin's criterion should be replaced—it should not—but whether the **geometry around the exact Cachin risk** exposes useful structure that the scalar value alone does not encode.

A second problem is experimental. Any apparent gain must survive:

- exact KL orientation and numerical certification;
- comparison with local Fisher approximations;
- a trivial uniform safety-shrink baseline;
- quantized residual models rather than continuous approximations alone;
- cover-source mismatch estimated without holdout leakage;
- real message coding rather than ideal-entropy payload claims;
- reference and contemporary steganalysis.

## 3. Scientific question

> **Can exact Cachin security be embedded in an information-geometric source–embedding framework that recovers the established local Fisher regime, differentiates nominally iso-Cachin designs under bounded cover-source uncertainty, and turns that additional structure into a certifiably robust embedding allocation?**

The current evidence is deliberately separated into formal, controlled, natural-source, operational-coding, independent external-validation, and still-open modern-steganalysis layers.

## 4. Proposed framework

Let \(p\) denote the true cover-source distribution, \(\theta\) an embedding design, and \(T_\theta(p)\) the stego distribution induced by applying the embedding operation to source \(p\). The canonical security field is

\[
\boxed{C(p,\theta)=D_{\mathrm{KL}}\!\left(p\Vert T_\theta(p)\right).}
\]

This definition preserves Cachin exactly. For a nominal source \(\hat p\), a Fisher–Rao ambiguity set is introduced,

\[
\mathbb B_{\mathrm{FR}}(\hat p,r)
=
\{p:d_{\mathrm{FR}}(p,\hat p)\le r\},
\]

and the robust exact-Cachin risk is

\[
\boxed{
\mathcal R_r(\hat p,\theta)
=
\sup_{p\in\mathbb B_{\mathrm{FR}}(\hat p,r)}
D_{\mathrm{KL}}\!\left(p\Vert T_\theta(p)\right).
}
\]

At \(r=0\), the construction reduces exactly to the nominal Cachin risk. Along a smooth embedding-rate direction, its second-order tangent recovers the established steganographic Fisher-information regime.

### 4.1 Source-direction sensitivity

The source-direction Fisher–Rao gradient

\[
S_{\mathrm{src}}(p,\theta)
=
\|\operatorname{grad}^{\mathrm{FR}}_p C(p,\theta)\|_{g_p}
\]

gives the local sensitivity of exact Cachin risk to source displacement. For small radii,

\[
\mathcal R_r(p,\theta)
=
C(p,\theta)+rS_{\mathrm{src}}(p,\theta)+O(r^2).
\]

The mathematical ingredients—Fisher–Rao geometry, robust optimization, and relative-entropy variance—are established foundations. The contribution lies in their Cachin-compatible **source–embedding construction and its steganographic design consequences**.

### 4.2 Quantized residual witness

The image witness uses a deterministic non-overlapping 3×3 carrier lattice. A modifiable center pixel is predicted from neighbors that remain unchanged. The associated residual therefore undergoes an exact \(-1,0,+1\) translation when the center is modified.

Eight frozen residual/texture strata are assigned embedding probabilities \(\beta_1,\ldots,\beta_8\). In the discrete model,

\[
q_g(k)
=
(1-2\beta_g)p_g(k)
+\beta_g p_g(k-1)
+\beta_g p_g(k+1).
\]

The robust design maximizes ternary embedding utility subject to the worst exact-Cachin risk over the frozen source-uncertainty geometry.

## 5. Research assets and means used

### Software

- Python 3.13 research implementation;
- NumPy, SciPy, scikit-learn, Pillow/imageio and pytest;
- deterministic Gauss–Hermite and discrete-PMF KL oracles;
- Sobol directions for high-resolution robust-risk certification;
- a reconstructed C++11 STC path based on the public `pySTC`/DDE implementation for operational coding checks.

### Data

**BOSSBase 1.01** is used for natural-source development. The archive was reconstructed from the available multi-volume files and validated as 10,000 PGM `P5`, 512×512, 8-bit images with zero CRC mismatch against the reconstructed ZIP directory.

The frozen split is determined from filenames before pixel analysis:

- 3,500 images: fit/model estimation;
- 1,500 images: calibration;
- 5,000 images: holdout.

Raw BOSSBase is acquired independently; the repository retains the split manifest, fitted summaries, protocols and numerical results needed for reproduction.

**BOWS2** is the independent external-validation source. The supplied split archive was qualified before V6 pixel-statistic analysis and contains exactly 10,000 native PGM `P5`, 256×256, 8-bit images. Because the earlier preregistration expected 512×512 images, `research_v8/protocols/V6_BOWS2_256_PREANALYSIS_ADDENDUM.md` freezes the dimensional deviation before analysis. No resizing or V6 retuning is permitted.

## 6. Main results retained so far

The repository preserves both favorable and negative findings because the latter determine the framework's valid operating domain.

### 6.1 Exact formal and numerical sanity checks

The retained unit tests cover, among other items:

- the canonical Cachin orientation \(D(P_C\Vert P_S)\);
- Fisher–Rao simplex-gradient identities;
- reduction to relative-entropy variance in the replacement-channel case;
- local robust slope checks;
- exact discrete-vs-continuous cross-checks;
- the large-\(\sigma\) connection to the \(\sigma^{-4}\beta^2\) local structure used by MiPOD-like derivations.

### 6.2 Controlled robust-design grid

Across 48 controlled conditions, robust exact designs satisfied the robust budget and were non-scalar reallocations of the nominal exact design. The median rate advantage over uniform safety shrinkage was only about **0.44%**, with the strongest cases near **4%**.

This was retained as a boundary result rather than promoted into a universal capacity claim.

### 6.3 Confirmatory iso-Cachin differentiation

A separately frozen confirmatory experiment showed that equal nominal Cachin risk does not imply equal source robustness. The synthetic/discrete V3 study passed its predeclared validity and materiality checks; at the larger stress radius, the median central dispersion across iso-Cachin designs was about **0.190**.

### 6.4 BOSSBase intra-source result — negative but retained

The first natural calibration measured mostly intra-source fluctuations and produced a small Fisher–Rao radius,

\[
r^*\approx0.03795.
\]

At that radius the iso-Cachin central dispersion did **not** meet the predeclared materiality threshold \(D_{80}\ge0.05\). V4A was therefore closed as

**FAIL ON MATERIALITY — PIVOT BEFORE HOLDOUT**.

The threshold was not lowered after observing the result.

### 6.5 Inter-camera mismatch

Using camera-source variation learned from the non-holdout BOSSBase partitions, the automatically selected nuisance model retained three Fisher directions explaining about **99.13%** of the inter-source energy and produced

\[
r_{\mathrm{cam}}\approx0.28873.
\]

The iso-Cachin dispersion became large (approximately **1.74–1.84** under the retained statistic), and robust reallocation materially outperformed uniform shrinkage at the same robust budget.

### 6.6 Full-PMF Fisher geometry

A later pivot moved from a log-scale Gaussian nuisance manifold to Fisher geometry over the **residual PMFs themselves**. Three retained shape directions explain approximately **97.85%** of the inter-camera Fisher energy, with calibrated

\[
r_{\mathrm{shape}}\approx0.23750.
\]

The V6 primary iso-Cachin dispersions are approximately

\[
D_{80}=0.482,
\qquad
D_{80}=0.531,
\]

well above the frozen 0.05 materiality threshold.

After independent 131,072-direction certification, the robust rate advantage over uniform shrinkage is approximately:

- **+2.885%** at \(\varepsilon=2\times10^{-4}\);
- **+16.502%** at \(\varepsilon=8\times10^{-4}\).

The corresponding same-payload dual analysis reduces certified worst-case robust risk by about **6.73%** and **38.14%**, respectively.

### 6.7 Operational probabilistic screening

On 800 frozen BOSSBase development/calibration images, matched-ideal-payload probabilistic stego realizations produced a lightweight SPAM-like detector AUC close to chance for both uniform-shrink and information-geometric allocations. This result is recorded as the lightweight screening layer; the modern detector layer is evaluated separately.

### 6.8 Actual-message STC aggregate and provenance status

The retained aggregate V8 summary reports **20,000 image-condition encodings** over 5,000 development/calibration images, two security budgets and two matched-payload methods. At \(\varepsilon=2\times10^{-4}\), both methods report **5,000/5,000 (100%)** exact recovery. At \(8\times10^{-4}\), uniform shrinkage reports **4,998/5,000 (99.96%)** and the information-geometric allocation **4,999/5,000 (99.98%)**. The three coding failures remain in the aggregate.

A clean source-level reconstruction from the tracked `research_v8/vendor/pystc_minimal/` implementation was rebuilt and used to rerun all 5,000 non-holdout images under the unchanged frozen V8 protocol. The resulting 20,000 raw image-condition records are persisted under `research_v8/results/V8_STC_RERUN/`. The six historically retained blocks covering indices 0–1500 reproduce exactly on all scientific fields except execution time; the full rerun reproduces the same three failed image-condition cases and the previous aggregate metrics to numerical precision. The historical compiled binary itself is not claimed to have been recovered. The authoritative closure note is `research_v8/operational/V8_STC_RUNTIME_PROVENANCE_AND_RERUN_CLOSURE.md`.

### 6.9 Independent BOWS2 external validation

The V6 external test was executed on all 10,000 qualified native 256×256 BOWS2 images under the frozen V6 geometry and candidates. The geometry-transfer diagnostics remain inside the preregistered manifold: projected norm **0.10190 < 0.23750** and normalized orthogonal residual **0.3840 < 0.60**. The frozen robust candidates remain below budget with direct empirical risk ratios **0.1381** and **0.3358**. The external iso-Cachin dispersions are **D80=0.3815** and **D80=0.4078**, both above the unchanged 0.05 threshold. The frozen decision is therefore **IN-MANIFOLD EXTERNAL PASS**.

## 7. Scientific positioning

The work is positioned relative to five established lines:

1. **Cachin security** — exact relative-entropy security remains the governing nominal constraint.
2. **Steganographic Fisher information** — Filler–Fridrich and Ker already establish local Fisher-information structure; this work treats that as prior art and a tangent regime to recover.
3. **Content-adaptive statistical detectability** — MiPOD provides a direct practical/local comparator through its variance-dependent allocation structure.
4. **Cover-source mismatch** — prior work establishes that model/source mismatch can reverse security rankings and degrade steganalysis; robust-optimization formulations have also been proposed on the detector side.
5. **General Fisher–Rao robustness** — established intrinsic distributional-robustness theory provides the geometric foundation; the contribution here is its integration with the exact sender-side Cachin source–embedding field and the resulting design constraints.

The protected contribution is therefore narrower:

> **A steganographic source–embedding security field that preserves exact Cachin security, separates embedding-direction Fisher sensitivity from source-direction Fisher–Rao sensitivity, derives finite-radius robust Cachin guarantees under a declared cover-model ambiguity set, and uses those guarantees to construct a multiparametric embedding design whose nominal-versus-robust behavior is experimentally falsifiable.**

Priority wording is restricted to the source–embedding construction and its tested design consequences.

## 8. Repository structure on this branch

```text
IG-based-Generative-Steganography/
├── README.md
├── research_v8/
│   ├── formal/                 # Cachin-compatible formal core and SOTA positioning
│   ├── protocols/              # Frozen protocols, preregistrations and numerical locks
│   ├── provenance/             # Claim/evidence map, old-version audit, design freezes
│   ├── src/                    # Executable continuous/discrete/image/STC research code
│   ├── tests/                  # Numerical and mathematical QA
│   ├── results/                # Retained numerical outputs and STC block summaries
│   ├── operational/            # Closure notes, external-validation and operational docs
│   └── provenance/             # SHA-256 manifests for retained local artifacts
├── Supplementary_Data/        # Historical material inherited from main
├── data/                      # Historical material inherited from main
└── figures/                   # Historical material inherited from main
```

`research_v8/provenance/LOCAL_WORKSPACE_MANIFEST.sha256` records the SHA-256 identifiers of retained workspace artifacts. Source code, protocols and compact numerical results are versioned directly on this branch; large image outputs remain outside Git history.

## 9. Reproducibility procedure

### 9.1 Clone the research branch

```bash
git clone --branch cachin-ig-robust-v8 \
  https://github.com/EkodeckStephane/IG-based-Generative-Steganography.git
cd IG-based-Generative-Steganography
```

### 9.2 Environment

Recommended:

- Python 3.11+; current retained execution used Python 3.13;
- GCC/G++ with C++11 support for the STC extension;
- NumPy, SciPy, scikit-learn, Pillow/imageio and pytest.

### 9.3 Run numerical tests first

```bash
pytest -q research_v8/tests
```

### 9.4 Inspect the formal core and frozen protocols

Start with:

```text
research_v8/formal/FORMAL_CORE_V1.md
research_v8/protocols/IMAGE_WITNESS_PROTOCOL_V1.md
research_v8/provenance/CLAIM_EVIDENCE_MATRIX_V6.md
```

Then follow the preregistered sequence from controlled grids through V3/V4/V5/V6 and the V7/V8 operational protocols.

### 9.5 BOSSBase

Obtain BOSSBase 1.01 independently. Do not commit the raw corpus to Git. Verify the corpus before use and reproduce the frozen split in:

```text
research_v8/results/bossbase_split_manifest_v4.csv
```

Development and calibration results must not be silently recomputed from the final holdout.

### 9.6 STC

The operational protocol is frozen in:

```text
research_v8/protocols/OPERATIONAL_STC_STEGANALYSIS_PREREG_V8.md
```

The retained STC runner records real message bits, exact recovery status, modification counts and method/budget metadata. Failed codewords remain failures; the payload is not reduced post hoc to improve the success rate. The source-level STC implementation used for the reproducibility closure is tracked in `research_v8/vendor/pystc_minimal/`, and the clean raw rerun plus its SHA-256 manifest are under `research_v8/results/V8_STC_RERUN/`.

### 9.7 External validation

BOWS2 is the completed primary external dataset. Reproduction must use the native 256×256 corpus, the frozen pre-analysis addendum, and the retained V6 objects without recalibration. The authoritative compact outputs are `research_v8/results/V6_BOWS2_256_EXTERNAL_SUMMARY.json` and `research_v8/results/V6_BOWS2_256_EXTERNAL_RESULTS.json`.

## 10. Integrity and provenance

The project deliberately distinguishes:

- **conceptual** statements;
- **proved/derived** statements;
- **implemented** algorithms;
- **simulated** results;
- **measured** empirical results;
- **inferred** interpretations.

Historical negative results are not deleted merely because later pivots perform better. In particular, V4A remains part of the record because it demonstrates that intra-source sampling variation alone did not meet the predeclared natural-image materiality threshold.

The current manuscript is rebuilt from the corrected formal core. `OLD_VERSION_CRITICAL_AUDIT.md` records the key historical defect: previous drafts reversed Cachin's asymmetric KL orientation in places. All current equations, code and evidence are rebuilt under

\[
\boxed{D_{\mathrm{KL}}(P_C\Vert P_S)}.
\]

`research_v8/provenance/LOCAL_WORKSPACE_MANIFEST.sha256` provides hashes for retained local research artifacts.

## 11. Current evidence status and open blockers

Current status at this snapshot:

- exact Cachin compatibility: **supported**;
- embedding-direction Fisher tangent recovery: **supported in the declared smooth/local regime**;
- controlled iso-Cachin differentiation: **confirmed**;
- BOSSBase source-mismatch geometry: **supported with retained negative and positive pivots**;
- V6 high-resolution robust-risk certification: **supported**;
- probabilistic image realization: **screening complete**;
- BOWS2 primary external validation: **PASS on all 10,000 native 256×256 images without retuning**;
- V8 STC actual-message coding and raw provenance: **PASS over a clean 20,000-record rerun; the original 0–1500 raw prefix is reproduced exactly on scientific fields, and all three historical failures recur**;
- SRM+ensemble / repeated-seed deep steganalysis: **still open as the detector-facing validation layer**.

The remaining empirical blocker is therefore the strong detector-facing steganalysis layer. After it is closed, the manuscript must undergo the final claim–code–data cross-check, theorem/figure/table audit, and Senior Reviewer Q1/Rang A prescreen.

## 12. Citation and reuse

This branch serves as the reproducibility record for the current research study. Until final manuscript metadata are frozen, cite the repository together with the exact branch/commit used; journal and archival metadata can be added once the target submission package is finalized.
