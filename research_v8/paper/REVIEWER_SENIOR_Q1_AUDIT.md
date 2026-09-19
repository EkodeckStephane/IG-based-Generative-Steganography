# Senior Reviewer Q1/Rank-A Prescreen — current final draft

## Calibration
Primary field: information-theoretic/image steganography. Secondary: information geometry, robust optimization, cover-source mismatch and steganalysis. Contribution: formal construction + robust design method + natural-image witness + actual-message coding validation.

## Overall assessment
The reconstructed paper has a coherent scientific object and a substantially improved promise-evidence chain. Exact Cachin orientation is correct, the central theorem constrains the implemented design problem, the strongest negative findings are retained, and complete STC evidence closes operational message realization. The remaining Q1-level evidence gap is empirical scope: independent BOWS2 transfer and strong detector-facing steganalysis.

## Promise/evidence
- Exact Cachin compatibility: **demonstrated**.
- Embedding-direction Fisher recovery: **demonstrated in declared local regime**.
- Source-mismatch boundary theorem: **demonstrated**.
- Iso-Cachin robustness differentiation: **demonstrated within declared source models**.
- Actionable non-scalar robust design: **demonstrated/certified within V6 model**.
- Actual-message realization: **demonstrated** by 20,000 STC encodings.
- Strong empirical warden resistance: **open**.
- Cross-corpus source transfer: **open**.

## Major issues
**M1 External transfer.** Execute the frozen BOWS2 protocol without BOWS2-driven refitting or threshold changes.

**M2 Strong steganalysis.** Execute SRM 34,671 + ensemble and at least one repeated-seed deep reference detector (SRNet/SiaStegNet class) at matched actual payload and source-disjoint evaluation. The slightly higher IG modification fractions at matched payload make this test scientifically necessary.

## Mathematics
The retained theorem is correct under its explicit interiority, positivity and C2 assumptions. It passes the five required strong-theorem criteria. Zero-radius recovery, radius monotonicity and uniform guarantees are appropriately kept below theorem status.

## Experimental validity
Strengths include frozen splits, preregistered decision rules, uniform safety shrinkage as a causal baseline, negative V4A retention, V5 model-mismatch disclosure, discrete/empirical PMF repair, independent 131,072-direction certification and complete failure-aware STC aggregation. V7 remains only a lightweight detector screen.

## Reproducibility
The branch contains formal core, protocols, code/tests, source-level STC implementation with license and final V8 aggregate. Large raw image outputs stay outside Git history and are tracked by manifests.

## Bibliographic/current-positioning audit
Critical primary references include Cachin 2004, Filler-Fridrich/Ker 2009, SRM 2012, MiPOD 2016, SRNet 2019, Giboulot et al. 2020, Sepak-Adam-Pevny 2022, Mallet-Benes-Cogranne 2024 systematic review, Yu et al. 2024 detector-side CSM adaptation, and Ketema et al. 2025 Fisher-Rao robustness.

## Recommended decision
**Major Revision.** The central theory/design/coding core is coherent and potentially publishable at Q1 level. M1 and M2 require substantive new experiments. The former STC major issue is closed.

## Minimum conditions for acceptance
1. Frozen BOWS2 external validation.
2. SRM+ensemble plus repeated-seed deep reference detector at matched actual payload.
3. Final claim-code-data-table-reference cross-check after those experiments.
4. Journal-specific formatting, authorship/affiliations/CRediT/data-code metadata.

**Gate 10: NO-GO until M1 and M2 close.**
