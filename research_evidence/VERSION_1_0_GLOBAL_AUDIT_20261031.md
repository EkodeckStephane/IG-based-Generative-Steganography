# DSP-D-26-02810 — Version 1.0 global editorial/scientific audit (2026-10-31)

## Authoritative revised release
The **audited release archive delivered in the current ChatGPT conversation** contains the revised article, point-by-point response, cover letter, complete experiment/source material and a one-page QA report. This note documents release evidence; it is **not a claim that all revised binaries or LaTeX sources have already been pushed to GitHub**.

Validated release source SHA-256 values:
- `Version_1.0/IG_STEGO_PAPER.tex`: `43d3651a132785c8b5d8d2c13ccf1cabeba04a0aa898dacdbee3afc764f78664`
- `Version_1.0/response_to_reviewers.tex`: `872738d29a8acb6b2ff68e911c69c2c4338588c8e10ae33b1b4287cc5606dc53`
- `Version_1.0/cover_letter.tex`: `bf4e7df2fae1f64cd77f9c86dda1e8235040065424f4f2f44113a6be42cf2473`

## QA completed on the archived revised sources
- Manuscript visibly labeled **Version 1.0**, 30 pages; response 8 pages; cover letter 1 page.
- 52 bibliography entries, all cited; 155 unique labels; no unresolved references in audit.
- S1–S5 eight pre-existing numeric experiment-table rows/sets preserved; S6 adds three separate direct-optimizer tables verified against saved JSON/CSV.
- S4 corrected-metric seven-resolution Gaussian check: energy 0.865107; sequential-KL 0.865108 at L=1024.
- S6 sampled-Fisher direct Algorithm 2: 251/300 held-out public codeword decodes, 9/12 converged targets. 1–4-bit sweep and a distinct multiobjective held-out comparison distinguish public VAE, scheme-native and model-informed receiver/detector assumptions.
- R2.1 cell-local ReLU/Fisher proof, 182/192 sampled perturbations meeting delta<1/2; finite-sample accuracy diagnostic. R2.2 fixed Fisher quadratic packing/decoding certificate.
- Original Pavlichin–Weissman chained KL/geodesic precedent acknowledged; direct operational security claims accurately scoped.
- Independent reproduction package: seven Algorithm 2 bridge unit tests passed and Pareto invariants passed.
- 11 LaTeX overfull warnings in the journal style remain as nonfinal typography QA.

## Public repo synchronization status
This commit **updates the scientific/QA record only**. The revised editorial LaTeX sources and their compiled PDFs in the conversation's release ZIP are the most recent Version 1.0, pending exact SHA-verifiable file sync to this repository. The historical repository versions must not be represented as byte-identical to that release until re-uploaded and checked. Baseline/code evidence already in the repo remains separately pinned.