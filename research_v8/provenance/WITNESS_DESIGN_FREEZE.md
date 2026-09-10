# Information-Geometric Steganography — Witness Design Freeze

## Scientific object
The framework retains Cachin's exact passive-warden risk with the original orientation

C(p,q) = D_KL(p || q),

and equips the finite-alphabet probability simplex with Fisher–Rao geometry.

## Refined robustness object
Let p_hat be a nominal cover-source model and let T_theta(p) be the stego distribution induced by an embedding mechanism theta when the true cover source is p. Define

R_r(p_hat,theta) = sup_{p: d_FR(p,p_hat) <= r} D_KL(p || T_theta(p)).

At r=0 this is exactly nominal Cachin security for p_hat. The radius r therefore represents source-model uncertainty rather than an unobservable internal optimization path.

## Local identity on the categorical simplex
For fixed q and f(p)=D_KL(p||q), with Fisher metric g_p(u,v)=sum_i u_i v_i/p_i on the simplex tangent space,

grad_FR f |_i = p_i [ log(p_i/q_i) - D_KL(p||q) ].

Hence

||grad_FR f||^2 = Var_p[log(p_i/q_i)],

the classical relative-entropy variance. This quantity is not claimed as new. Its role here is as the first-order sensitivity of exact Cachin risk to Fisher–Rao-bounded cover-source mismatch:

R_r(p_hat,q) = D_KL(p_hat||q) + r sqrt(V(p_hat||q)) + O(r^2).

## Exact categorical witness
Use p_hat in the interior of a K-symbol simplex and a distributional/arithmetic-coding stegosystem with replacement distribution q. Compare:

1. Cachin-only nominal design: maximize H(q) subject to D_KL(p_hat||q) <= epsilon.
2. Local-Fisher design: use the second-order Fisher approximation only.
3. Proposed IG-robust design: maximize H(q) subject to R_r(p_hat,q) <= epsilon.
4. Oracle design: optimize against the true p after mismatch is revealed (evaluation reference, not deployable baseline).

Primary evidence is not that the robust design has higher nominal rate. The protected claim is that it provides a uniform exact-KL guarantee for every cover source inside the declared Fisher–Rao uncertainty ball, while the nominal design need not.

## Controlled numerical sanity case
p_hat=(0.6,0.3,0.1), epsilon=0.05 nat, r=0.20 under d_FR(p,q)=2 arccos(sum sqrt(p_i q_i)).

The prototype computes:
- nominal entropy-maximizing q approximately (0.471128, 0.324619, 0.204253), H=1.50653 bits/symbol, nominal KL=0.05, but worst KL on the r-ball about 0.12263 > 0.05;
- robust q approximately (0.552806, 0.306158, 0.141035), H=1.39409 bits/symbol, nominal KL about 0.00867, worst KL on the r-ball about 0.05.

This is a mathematical sanity check, not a paper result and not evidence on natural images.

## Image witness after analytic closure
Use a multiparameter ternary ±1 embedding channel on strata of natural-image residual/pixel statistics. For group g with cover pmf p_g and stochastic embedding matrix B_g(theta_g), the induced stego pmf is q_g=p_g B_g(theta_g). Under the declared factorization model, exact nominal Cachin risk is the sum of groupwise KL terms. Fisher blocks are computed from q_g(theta_g), not approximated by raw feature covariance. A syndrome-coding realization may then be used to measure actual payload/coding loss.

## Existing package disposition
- frstego_operational: retain only as historical/exploratory control. Its `empirical_fisher` explicitly uses feature covariance as a proxy, so it cannot support a formal Fisher claim.
- cpu_stego_experiments: retain only as exploratory applied validation; `Fisher-Diag` is a variance-aware proxy, not an exact Fisher metric.
- stego_q1_revision_package simulations: reusable for regression/sanity checks only; geodesic-path detectability is no longer a central security claim.
- THEORY_ONLY submissions: historical archive; do not use as textual base for the new manuscript.

## Hard gates before image experiments
1. Prove r=0 recovery of Cachin with exact KL orientation D(P_C||P_S).
2. Prove Filler–Fridrich local recovery under their assumptions.
3. Prove the Fisher-gradient/relative-entropy-variance identity and finite-radius security guarantee.
4. Audit novelty against channel-uncertainty/detectability work and cover-source mismatch literature.
5. Freeze the exact image source model, embedding channel and statistical unit before viewing headline results.
