# Prior-art positioning v2 — protected contribution boundary

## Direct lineage
1. **Cachin (1998; journal version 2004)** — exact passive-warden security via `D_KL(P_C||P_S)`.
2. **Filler & Fridrich (2009)** — steganographic Fisher information with respect to embedding change rate; perfect-security characterization for their MI class; capacity/root-rate and embedding optimization under stated assumptions.
3. **Ker (2009 and related work)** — estimation of steganographic Fisher information on real images and combinations of embedding functions.
4. **Liśkiewicz, Reischuk & Wölfel (2017)** — channel knowledge/uncertainty and detectability notions; uncertainty about the cover channel is not a new problem.
5. **Giboulot et al. (2020)** — cover-source mismatch in image steganalysis; empirically establishes source inconsistency as a practical issue.

## Cross-domain novelty killer
**Ketema et al. (2025), Journal of Statistical Computation and Simulation** use Fisher–Rao geodesic distance to define variational classes of input distributions for robustness analysis under distributional uncertainty. Therefore, “Fisher–Rao ball + worst-case robustness” is generic prior art and cannot be the mathematical novelty claim.

## Consequence for our positioning
The manuscript must present general Fisher–Rao robustness machinery as adopted mathematics. The candidate new contribution must be steganography-specific:

- define the exact **source–embedding Cachin risk field** `C(p,theta)=D_KL(p||T_theta(p))`;
- distinguish two physically different tangent axes: embedding variation (Filler–Fridrich) and cover-source variation (model mismatch);
- derive source-gradient sensitivity for actual stochastic embedding channels;
- formulate finite-radius robust Cachin security under a declared source ambiguity set;
- derive/test the strict gap between nominal Cachin boundary designs and robust-feasible designs;
- use this structure to produce a concrete multiparametric stegosystem and compare nominal vs robust design under identical exact KL budget and actual steganalysis.

## Claim discipline
Use wording such as “we formulate”, “we derive for the steganographic risk field”, and “we show experimentally under the stated model”. Avoid “first”, “unprecedented”, “new Fisher–Rao robustness theory”, or statements that Cachin cannot mathematically be extended by differentiation.
