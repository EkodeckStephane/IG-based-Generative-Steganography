# DSP-D-26-02810 / Version 1.0 — Final scientific action plan
**Date:** 2026-11-04. **Status:** planned research, not completed or experimentally validated. **Sources:** attached F. Papangelou (2000), *Annals of Applied Probability*, 10(4), 1259–1273, DOI 10.1214/aoap/1019487616; Pavlichin & Weissman (2016), IEEE ISIT, 580–584, DOI 10.1109/ISIT.2016.7541365; current Version 1.0 manuscript.

## 0. Critical positioning
- Papangelou solves Wright–Fisher's variational action and establishes endpoint large-deviation rate J_{p,T}(q)=2 theta^2/T and conditional path concentration on the great circle (Theorems 1,2). Do not transfer the stochastic statement to a deterministic NG-Stego optimizer.
- Pavlichin–Weissman minimize the finite k-step sum of KL over the finite-alphabet simplex and show continuum optimal paths converge to Fisher geodesics. The general-purpose unconstrained variational idea is prior art.
- Manuscript's Theorem 3(iv) describes a prescribed regular path: sum KL = E[gamma]/(2N) + O(N^-2). This follows from standard local KL expansion, uniform remainder, and Riemann-sum approximation. Not itself new variation theory.
- Literature scan: prior geometric variational/constrained endpoints and gamma-convergence work must be surveyed before novelty assertions. See e.g. research on pullback information geometry, variational geodesics on Gaussian statistical manifolds, and Gamma convergence of entropic actions.

## P0-A: Generator-constrained discrete variational problem
Define image of generator M_G={P_theta : theta in Theta} with equivalence modulo nonidentifiable parameters. For fixed distributions P_a,P_b in M_G:
C_N^G(P_a,P_b)=inf_{P_1,...,P_{N-1} in M_G} sum_{i=1}^N KL(P_i||P_{i-1}), P_0=P_a,P_N=P_b.
Compare ambient C_N^amb minimizing over all positive distributions, and E_G[gamma]=integral_0^1 ||dot(gamma)||_F^2 dt.
**Target theorem, not yet proven:** under strong sufficient assumptions (compact smooth embedded identifiable submanifold in the strictly positive finite-alphabet simplex, uniform ellipticity, bounded third KL derivatives, separated endpoints), prove equicoercivity and Gamma convergence N C_N^G => (1/2) d_G(P_a,P_b)^2; minimizers or subsequences converge to generator-constrained length-minimizing constant-speed geodesics, with full convergence if unique. Investigate finite-N error rate O(1/N) only if explicit regularity on discrete optimizers and comparator is proved. Provide counterexamples for noncompact, singular Fisher, boundary and disconnected feasible sets.
**Required proof:** upper bound by discretizing a smooth minimizer; KL coercivity and mesh bound; lower bound via piecewise-geodesic interpolations and integral-action lower semicontinuity; identify equality case and topology of minimizers. Check existing general Gamma-convergence literature before claiming novelty.

## P0-B: Exact cost decomposition and model restriction
For an actual feasible curve gamma with endpoints P_a,P_b, define L=length_G(gamma), E=energy(gamma), d_G=intrinsic distance on M_G, d_A=ambient Fisher–Rao distance.
E-d_A^2 = [E-L^2] + [L^2-d_G^2] + [d_G^2-d_A^2].
Nonnegative components: speed parametrization, nonoptimal feasible route, restricted-model geometry. **Classical identity**, not claimed novel. The sought contribution is a new *measurable and predictive diagnostic* of codebook reachability, optimizer failure and embedding performance. For binary-independent VAE:
log Bhattacharyya = sum_i log(sqrt(p_i q_i)+sqrt((1-p_i)(1-q_i))), d_A=2 acos(exp(log B)).
Calculate d_G by independent boundary-value geodesic optimization and rigorous bounds where possible; do not substitute natural-gradient descent for the geodesic. If optimized endpoint misses target, compare only paths with the *same achieved endpoint* or explicitly report the endpoint gap.

## P0-C: Steganographic variational problem with decision-relevant endpoints
Fixed endpoints cannot improve optimal final-object detection by altering the path alone. Define admissible message-specific endpoint sets A_m (decodability and distortion), jointly optimize codebook endpoints and trajectories subject to cover-vs-mixture detectability, reliability, payload and compute constraints; specify public/private information, keys and distribution of messages.
**Target result:** existence under compactness, first-order optimality incl. transversality for variable endpoints, stability of solution under FIM approximation, and an independently testable useful advantage over matched alternatives. Cite existing constrained-endpoint geodesic/transversality prior art.
Alternative threat models must be separate: endpoint-only adversary vs observer of a true stochastic sequence. Do not call a sequential-KL surrogate a security exponent without proving an actual stochastic transition law and an LDP.

## P0-D: ReLU and inexact FIM
Provide a rigorous smooth setting first. For the deployed ReLU Bernoulli VAE, handle activation-cell boundaries via a stratified/weak formulation or restrict theorem to smooth surrogate with transparent limitation. Study identifiability and FIM rank; regularization F+lambda I changes geometry. Prove/disprove perturbation results for discrete optimum and geodesics with explicit assumptions. R2.1 local affine-cell KL-Fisher and sampled metric error remain diagnostics, not whole-trajectory guarantees.

## P0-E: Preregister falsifiable experiment
At least (a) Gaussian and Bernoulli families with analytic ambient FR, (b) the existing MNIST Bernoulli VAE, (c) a genuinely independent generator/dataset if feasible. Codebooks selected independently of holdout, no cover-valued codeword, 1–4+ bits with fixed channel definitions.
Compare: true constrained geodesic via independently checked BVP, optimized discrete chained-KL path, Fisher-natural-gradient optimizer path, carefully tuned Euclidean paths, adapted iMEC/Discop on common channel, with native pipelines in a separate descriptive benchmark.
Report heldout decoding and error intervals, endpoint-KL/TV if calculable, adaptive pixel/public-latent detector AUC and CI, distortion, CPU/GPU cost, KL path action, E, L, d_A, numerical upper/lower d_G bounds, activation crossings and FIM errors. Equal endpoints, payload, distortion/security budgets and compute budgets where comparing geometric route efficiency. Record uncertainty and negative outcomes.
**Primary go/no-go**: Do model-restriction or path-suboptimality diagnostics predict held-out failure/robustness/cost meaningfully *beyond* endpoint KL, Euclidean distances, Fisher condition numbers, curvature, generator Jacobian norms and existing numerical diagnostics? Assess incremental predictive value with CIs; hold out entire codebooks and generators. If no added value, do not make this the manuscript's flagship contribution.

## P1: Detection duality and curvature
The affine Neyman–Pearson log-likelihood test for a regular exponential family is classical. Keep as interpretation unless a genuinely new, formally proven consequence connects chosen embedding endpoint/path and detector power under explicit adversary observations. Distinguish geodesic LC, e-geodesic and m-flat geometry. Test the two curvature effects on volume/separation vs Jacobi instability with controlled ablations, not post hoc causal interpretation.
Prove or remove unsupported volume and geodesic curvature-to-KL claims.

## P1: Manuscript refactor
Change manuscript Theorem 3(iv) to a standard lemma/fixed-path bridge. Put a *proved* constrained-discrete variational theorem (and any generator gap result) in its place as principal mathematical contribution only after proof and prior-art novelty audit. Reorganize experiments in 3 groups: mathematical limit; optimizer/geodesic fidelity; operational consequences. Compress repeated disclaimers into concise assumption statements plus a scope/limitations section. Keep S4/S5/S6 numbers untouched unless rerun on same protocol and proven wrong; don't suppress negative outcomes. Align abstract, introduction, all formal statements/proofs, figures/tables, conclusion, response to reviewers and cover letter in Version 1.0. Retain release label Version 1.0 rather than silently using 1.01. Build clean editor ZIP and distinct audit/reproducibility ZIP; check page numbering, algorithms, bibliography, refs, figures and all overfull boxes.

## Publication decision gates
G0: exact prior-art matrix and theory scope.
G1: formal proof with independent counterexample audit and reproducing numerics.
G2: verified constrained geometry/distance decomposition on actual generator.
G3: prospectively specified heldout predictive or operational gain against strong, fair baselines.
G4: independent full end-to-end code/data rerun and artifact manifests; GitHub synchronized and verified.
G5: mutually consistent manuscript, reviewer response and cover letter; all justified claims cited.
If G3 fails, position as an honest limited methodology/diagnostics paper or reconsider journal/claim scope. No acceptance prediction or claim of newly proved theorem before these gates pass.
