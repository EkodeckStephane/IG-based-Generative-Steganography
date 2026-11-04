# Critical reading of reference [13] and reviewers' opinions — 2026-11-04

**Status:** research assessment / proposed revisions; **no edits to the three official Version 1.0 submission documents**. The assessed local baseline is the latest 31-page Version 1.0 article in `DSP_D-26-02810_Version_1.0_Soumission_Completement_Reauditee.zip`.

## Grounded source interpretation
Pavlichin and Weissman, *Chained Kullback-Leibler Divergences*, IEEE ISIT 2016, pp. 580–584, DOI 10.1109/ISIT.2016.7541365. Author manuscript: https://pmc.ncbi.nlm.nih.gov/articles/PMC5677233/

- Their D^(k) **minimizes** sum of forward KL over intermediate distributions on the finite-alphabet simplex. Theorem 2 provides finite-step optimality conditions including Lambert-W updates. Theorem 3 eqs (30)–(31) gives `lim_{k->infty} k D^(k)(p||q)=2 arccos(sum sqrt(pq))^2` and the constant-speed great-circle limit of optimal paths under common-support hypotheses.
- Authors explicitly credit **F. Papangelou (2000)** for the previously studied continuum large-deviation/geodesic result, DOI 10.1214/aoap/1019487616.
- Eq. (28) in the author manuscript is `2 theta^2 + O(theta^4) + sum_x O(delta_x^3/sqrt(q_x))`; therefore it does **not** justify a general `O(theta^4)` KL remainder. Typically the cubic contribution remains.
- The supplied PMC *author manuscript* appendix p. 28 contains editorial placeholders (`why theta^(k)=O(1/k)?`, `Now use joint strict convexity ... complete proof?`). This is a limitation of the supplied document, not proof that the final published theorem is invalid. Verify against publisher's final typeset version if claiming proof completion.

## Distinction from manuscript Theorem 3(iv)
The submitted manuscript evaluates an **arbitrary fixed smooth parametric path** `gamma` using local KL expansion and a Riemann sum: `S_N(gamma)=E(gamma)/(2N)+O(N^-2)`. This is not the same mathematical statement as minimizing D^(k) over simplex paths. It applies beyond finite alphabets under uniform local smoothness/regularity (e.g. smooth KL third derivatives, gamma with bounded acceleration, nondegenerate Fisher metric). It is still essentially a standard Taylor/Riemann-sum consequence, not an automatically novel general theorem. For a full simplex minimizing geodesic, both formulae agree since `d_FR(p,q)=2 arccos(sum sqrt(pq))`, hence `E_min/2 = 2 theta^2`.

**Correction needed:** remove language saying 3(iv) is a *specialization of* [13]; cite [13] and Papangelou as distinct conceptually related prior optimal-path/large-deviation works, and identify (iv) as standard fixed-path local calculus. Do **not** infer Wright–Fisher large-deviation guarantees for NG-Stego unless a corresponding transition law is independently defined and proved.

## Current-version checks rebutting stale criticism
In the locally inspected **31-page Version 1.0** PDF, page 1 visibly says `1. Introduction` and `1.1. Background and Motivation`; source and extracted PDF show Algorithm 2 and Algorithm 3 both `while L(theta_t)>epsilon`. The alleged `2.1 Introduction` / inverted Algorithm 3 predicate concern a different or earlier version and should not be reported as defects of the checked file.

## Operational interpretation
- S6a: sampled-Fisher 251/300 and 9/12 converged targets; Euclidean 299/300 and 12/12, under their shared KL optimizer test.
- S6c (10 iterations): Fisher public decode 255/300, pixel AUC 0.987, cover KL 79.54, probability MSE 0.030140, 9.30 ms/codeword. Euclidean: 285/300, AUC 0.993, KL 83.68, MSE 0.031964, 22.56 ms/codeword. **Neither strictly Pareto-dominates the other across all reported objectives**; neither supports strong endpoint security.
- Channel-adapted iMEC 300/300 and AUC 0.507 is strong relative evidence under the tested conditions, but an AUC close to 0.5 is not a mathematical proof of undetectability. Different receivers and full native pipelines still matter.
- The paper's NP/m-flat identity is an algebraic consequence of exponential-family LLR and classical dual-affine coordinates. Its application-level interpretation may be useful, but a genuinely new mathematical theorem or novel steganalysis capability has **not** been demonstrated by this identity alone.

## Proposed scientific improvement, ordered
1. **Define the actual adversary observation model**: final object only vs sequence of intermediate states. Sequential KL is not endpoint-KL and is not a security rate for final-object-only observers.
2. **Derive a generator-constrained geometric gap**: for a smooth probability family embedded into an ambient simplex, `E(gamma)>=length_FR(gamma)^2>=d_generator^2>=d_ambient_FR^2` with `d_ambient_FR=2 arccos(Bhattacharyya coefficient)`. Separate reparameterization, nonoptimal trajectory, and restricted-generator expressivity gaps. These inequalities are classical; the contribution must be a new steganographic diagnostic plus *validated predictive benefit*.
3. **Use the actual VAE distribution**: for independent Bernoulli pixels compute `B(P_z,P_z')=prod_i[sqrt(p_i q_i)+sqrt((1-p_i)(1-q_i))]` in log-space, giving exact ambient Fisher–Rao lower bounds even when the latent model has ReLU kinks. Compare path length/energy and held-out detection, decoding and runtimes under fixed endpoint KL/payload.
4. **Ablate and falsify**: distinguish genuine constrained geodesics from natural-gradient *optimizer* trajectories; fixed endpoints, arc-length parameterization, matched budgets; test multiple seeds, codebooks and independent generators, no post-hoc method selection. Compare with stronger tuned Euclidean, iMEC/Discop adaptations, and native baselines only in separate contexts.
5. **Position the contribution** as a tested constrained-generator path diagnostic with explicit value for a *multi-step* embedding process, if results support it. If only final samples are observed, identical endpoint distributions imply identical optimal detection irrespective of latent trajectory.
6. **Editorial**: shorten repeated scope disclaimers, concentrate limitations in a single section, revise abstract/introduction/conclusion and reviewer response *only once new claims are substantiated*. Avoid unjustified claims that curvature caused S5 detection, that chained KL equals an operational information-leakage rate, or that NP dual-affinity is an original security theorem.

**Decision:** the present manuscript has a plausible rigorous methodology contribution but not yet a demonstrated unique operational benefit; major new experiments/theoretical connection are needed to meet a demanding novelty threshold. Acceptance cannot be assured.
