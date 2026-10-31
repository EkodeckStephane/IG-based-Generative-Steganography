# DSP-D-26-02810 — Audited 4-priority manuscript revision (2026-10-31)

**Three synchronized and Git-blob-verified manuscript sources**

- `Version_1.0/IG_STEGO_PAPER.tex` — Git blob `7e442aeea2acb8fd7886816d14d32f01093dfe64`
- `Version_1.0/response_to_reviewers.tex` — Git blob `78f43a5efe6c564bf37035b9be891b45b0aaacca`
- `Version_1.0/cover_letter.tex` — Git blob `59193008c87eaf1fa5d5bc8243bc168f5c627ffa`

**Four corrections:** (1) replaced overly general one-step NG convergence assertion with conditional *ideal exponential-map Riemannian* rate plus Bernoulli-ReLU activation-cell exact identity and single-step inexact-Fisher bound; (2) replaced invalid curvature-dependent KL inequality with bounded-metric comparison `m/(2M) d_g^2 <= KL <= M/(2m) d_g^2` in the specified convex region and local `KL = .5 d_g^2 + O(d_g^3)`; (3) explicitly credit the pre-existing general chained-KL/geodesic limit from Dmitri S. Pavlichin and Tsachy Weissman, *Chained Kullback-Leibler Divergences*, IEEE ISIT 2016, pp. 580–584, DOI `10.1109/ISIT.2016.7541365`; (4) align abstract/contributions/proofs/discussion/conclusion/reviewer response/cover letter.

**Checks performed on the identical local submission sources before publication:**
- Article 29 pages, reviewer response 8 pages, cover letter 1 page; all LaTeX compile.
- Eight experimental tables unchanged; only scientific-prior-art comparison table edited.
- Four used figure assets byte-identical to previous submission release.
- 51 bibliography entries, all cited; 151 cross-reference labels, no missing or duplicate labels.
- Six earlier math verification tests, 100 Bernoulli-logit same-cell numerical identities, 1000 KL/Fisher-distance comparisons, and sampled inexact-Fisher single-step checks pass.
- No obsolete S4 historical ratios in the three official submitted sources.

**Essential limits:**
- The contraction guarantee in a ReLU cell does not establish full-algorithm convergence across activation boundaries or a security guarantee.
- The chained-KL/Fisher-geodesic theorem is *not claimed as mathematically original*; novelty is the limited application-specific formulation and analysis.
- R2.3 and R2.7 remain experimentally incomplete in their full native/adaptive scope. No operational dominance of NG-Stego is claimed.
- There are **13** overfull-box warnings in the article build; final typography requires further polish.
- Source *.tex are synchronized here. The PDF binary assets and complete pre-submission material are delivered via the accompanying user ZIP; their GitHub publication is not asserted. Because of double-blind evaluation, sharing public author-identified links in editor-facing documents may require journal-policy review.

This note documents corrections and limitations; it does not imply editorial acceptance.
