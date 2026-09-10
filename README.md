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

The current evidence is deliberately separated into formal, controlled, natural-source, operational-screening, and still-open external/modern-steganalysis layers.

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

The project does **not** claim that Fisher–Rao geometry, robust optimization, or relative-entropy variance are new mathematical objects. The contribution is their Cachin-compatible **source–embedding construction and its steganographic design consequences**.

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

The repository does **not** redistribute BOSSBase images. Only manifests, fitted summaries, protocols and numerical results are retained.

**BOWS2** is reserved as the primary external validation source. That experiment is intentionally still open and will be executed only when the raw 10,000-image corpus is supplied to the working environment. No substitute dataset is silently used in its place.

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

On 800 frozen BOSSBase development/calibration images, matched-ideal-payload probabilistic stego realizations produced a lightweight SPAM-like detector AUC close to chance for both uniform-shrink and information-geometric allocations. This is recorded only as a **screening result**, not as modern steganalysis evidence.

### 6.8 STC campaign status

Real STC encoding/decoding has been brought into the current environment and tested successfully at the low level with zero BER in synthetic checks. The corrected image campaign uses the appropriate DDE matrix widths for the actual layered payload regime.

At the current repository snapshot, V8 remains **partially executed**. The available block results are retained for provenance; they must not be interpreted as the final 5,000-image STC result until the complete frozen campaign is aggregated.

## 7. Scientific positioning

The work is positioned relative to five established lines:

1. **Cachin security** — exact relative-entropy security remains the governing nominal constraint.
2. **Steganographic Fisher information** — Filler–Fridrich and Ker already establish local Fisher-information structure; this work treats that as prior art and a tangent regime to recover.
3. **Content-adaptive statistical detectability** — MiPOD provides a direct practical/local comparator through its variance-dependent allocation structure.
4. **Cover-source mismatch** — prior work establishes that model/source mismatch can reverse security rankings and degrade steganalysis; robust-optimization formulations have also been proposed on the detector side.
5. **General Fisher–Rao robustness** — intrinsic distributional robustness is established outside steganography and is not claimed as new mathematics here.

The protected contribution is therefore narrower:

> **A steganographic source–embedding security field that preserves exact Cachin security, separates embedding-direction Fisher sensitivity from source-direction Fisher–Rao sensitivity, derives finite-radius robust Cachin guarantees under a declared cover-model ambiguity set, and uses those guarantees to construct a multiparametric embedding design whose nominal-versus-robust behavior is experimentally falsifiable.**

No “first”, “unprecedented”, or generic “new Fisher–Rao theory” claim is made by this repository.

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
│   └── snapshot/
│       ├── MANIFEST.sha256
│       └── research_workspace_snapshot.zip
├── Supplementary_Data/        # Historical material inherited from main
├── data/                      # Historical material inherited from main
└── figures/                   # Historical material inherited from main
```

The `research_v8/snapshot/` archive is an exact compact snapshot of all useful current workspace artifacts included for reproducibility. Raw BOSSBase images and generated stego images are deliberately excluded.

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

The retained STC runner records real message bits, exact recovery status, modification counts and method/budget metadata. Failed codewords remain failures; the payload is not reduced post hoc to improve the success rate.

### 9.7 External validation

BOWS2 remains the primary external dataset. The exact external protocol is frozen before access to the corpus. When BOWS2 becomes available, use the predeclared validation scripts/protocol rather than recalibrating the BOSSBase-trained geometry on BOWS2.

## 10. Integrity and provenance

The project deliberately distinguishes:

- **conceptual** statements;
- **proved/derived** statements;
- **implemented** algorithms;
- **simulated** results;
- **measured** empirical results;
- **inferred** interpretations.

Historical negative results are not deleted merely because later pivots perform better. In particular, V4A remains part of the record because it demonstrates that intra-source sampling variation alone did not meet the predeclared natural-image materiality threshold.

The old rejected manuscripts are not used as a textual base for a future paper. `OLD_VERSION_CRITICAL_AUDIT.md` records the most important reason: previous drafts reversed Cachin's asymmetric KL orientation in places. All current equations, code and evidence are rebuilt under

\[
\boxed{D_{\mathrm{KL}}(P_C\Vert P_S)}.
\]

`research_v8/snapshot/MANIFEST.sha256` provides hashes for the browsable research artifacts in this branch.

## 11. Current evidence status and open blockers

Current status at this snapshot:

- exact Cachin compatibility: **supported**;
- embedding-direction Fisher tangent recovery: **supported in the declared smooth/local regime**;
- controlled iso-Cachin differentiation: **confirmed**;
- BOSSBase source-mismatch geometry: **supported with retained negative and positive pivots**;
- V6 high-resolution robust-risk certification: **supported**;
- probabilistic image realization: **screening complete**;
- real STC encoding/decoding: **implemented, campaign still incomplete in this snapshot**;
- SRM+ensemble / SRNet / SiaStegNet final campaign: **not yet complete**;
- BOWS2 primary external validation: **not yet executed**.

Accordingly, this branch is a **research/reproducibility branch**, not a claim that the final Q1 publication gate has already been passed. Final publication readiness requires completion of the frozen STC campaign, reference/contemporary steganalysis, BOWS2 validation, a claim–code–data cross-check, and the final hostile senior-reviewer audit.

## 12. Citation and reuse

This branch currently serves as a reproducibility record for an ongoing research study. Until the final manuscript metadata are frozen, cite the repository and the exact branch/commit used. Do not attribute journal acceptance or final-paper claims to this branch unless such metadata are later added explicitly.
