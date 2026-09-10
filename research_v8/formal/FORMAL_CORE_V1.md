# Cachin-Compatible Information-Geometric Steganography — Formal Core v1

## Status
**Formalization gate: PASS for the finite-alphabet core.**  
**Novelty gate: conditional.** The generic use of Fisher–Rao geodesic neighborhoods for robustness analysis is prior art outside steganography; novelty must be protected at the steganographic construction level described below.

## 1. Canonical convention
For every rebuilt theorem and experiment, Cachin security uses the original orientation

\[
C(p,\theta)=D_{\mathrm{KL}}\bigl(p\,\|\,T_\theta(p)\bigr),
\]

where `p` is the cover-source distribution and `T_theta(p)` is the induced stego distribution. The rejected manuscript versions that define Cachin security as `D_KL(P_S || P_C)` are historical and must not be patched equation-by-equation; all dependent statements must be rederived.

## 2. Source–embedding security field
Let

\[
\mathcal P = \Delta_{K-1}^{\circ}
\]

be the interior categorical cover-source manifold, equipped with the Fisher metric

\[
g_p(u,v)=\sum_{i=1}^K \frac{u_i v_i}{p_i},
\qquad \sum_i u_i=\sum_i v_i=0.
\]

Let `Theta` parameterize a family of row-stochastic embedding channels `B_theta`. Define

\[
T_\theta(p)=pB_\theta,
\qquad
C(p,\theta)=D_{\mathrm{KL}}(p\|pB_\theta).
\]

The primary object is therefore not a new distance but a **security field** on source × embedding design space:

\[
\mathcal C:\mathcal P\times\Theta\to\mathbb R_{\ge0}.
\]

This separates three questions:

- Cachin: the exact value of `C(p,theta)` at a specified source/design pair;
- Filler–Fridrich: local behavior of `C` along an **embedding-rate direction** around zero embedding;
- proposed extension: local and finite-radius behavior of `C` along **cover-source/model directions**, plus robust design under that uncertainty.

## 3. Exact Cachin recovery
For a nominal source `p_hat`, define

\[
\mathcal S_\varepsilon(p)=\{\theta:C(p,\theta)\le\varepsilon\}.
\]

Then, by definition,

\[
\theta\in\mathcal S_\varepsilon(p)
\iff
D_{\mathrm{KL}}(p\|T_\theta(p))\le\varepsilon.
\]

Thus the framework preserves the exact Cachin criterion. For `epsilon=0`, Gibbs' equality condition gives `p=T_theta(p)` almost everywhere/on all positive-mass symbols.

**Novelty status:** not novel; this is a required compatibility property.

## 4. Filler–Fridrich tangent recovery
Fix a cover source `p` and a smooth embedding curve `theta(beta)` with no embedding at `beta=0`, so that

\[
T_{\theta(0)}(p)=p.
\]

Under standard regularity conditions,

\[
C(p,\theta(\beta))
=\frac{\beta^2}{2}\,I_{\mathrm{emb}}(p;\dot\theta(0))+O(\beta^3),
\]

where the quadratic term is the pullback Fisher information in the embedding direction. Under the mutually-independent embedding assumptions used by Filler–Fridrich, this recovers their steganographic Fisher-information regime.

**Novelty status:** not novel; this is a required recovery theorem and positioning bridge.

## 5. Fisher–Rao source uncertainty
For nominal cover model `p_hat`, define the exact categorical Fisher–Rao distance using the convention induced by the metric above:

\[
d_{\mathrm{FR}}(p,q)
=2\arccos\left(\sum_i\sqrt{p_iq_i}\right).
\]

Define the source ambiguity set

\[
\mathbb B_{\mathrm{FR}}(\hat p,r)
=\{p:d_{\mathrm{FR}}(p,\hat p)\le r\}.
\]

The **robust Cachin risk** of an embedding design is

\[
\mathcal R_r(\hat p,\theta)
=\sup_{p\in\mathbb B_{\mathrm{FR}}(\hat p,r)}
D_{\mathrm{KL}}\bigl(p\|T_\theta(p)\bigr).
\]

### Proposition 1 — zero-radius recovery
\[
\mathcal R_0(\hat p,\theta)=C(\hat p,\theta).
\]

### Proposition 2 — radius monotonicity
If `0 <= r1 <= r2`, then

\[
\mathcal R_{r_1}(\hat p,\theta)
\le
\mathcal R_{r_2}(\hat p,\theta).
\]

Consequently the robust feasible design set shrinks monotonically with uncertainty radius.

### Proposition 3 — uniform guarantee
If

\[
\mathcal R_r(\hat p,\theta)\le\varepsilon,
\]

then every source `p` in the declared Fisher–Rao ball satisfies the exact Cachin condition

\[
D_{\mathrm{KL}}(p\|T_\theta(p))\le\varepsilon.
\]

These three statements follow directly from set inclusion/definitions. Their importance is semantic and steganographic, not mathematical novelty.

## 6. Two different tangent sensitivities
This distinction is central.

### 6.1 Embedding-direction sensitivity
Filler–Fridrich hold `p` fixed and vary embedding strength `beta`. Their local quadratic quantity describes how security degrades as embedding is introduced.

### 6.2 Source-direction sensitivity
The proposed robustness layer holds an embedding design fixed and varies the plausible cover source `p` around `p_hat`. Define

\[
S_{\mathrm{src}}(p,\theta)
=\left\|\operatorname{grad}^{\mathrm{FR}}_p C(p,\theta)\right\|_{g_p}.
\]

For any smooth risk field and an interior point with nonzero source gradient,

\[
\mathcal R_r(p,\theta)
=
C(p,\theta)+rS_{\mathrm{src}}(p,\theta)+O(r^2).
\]

This is a standard Riemannian first-order worst-direction expansion specialized to the exact Cachin risk field.

## 7. Closed form for a categorical embedding channel
Let `B` be a positive/compatible row-stochastic matrix and

\[
q=pB,
\qquad
C_B(p)=D_{\mathrm{KL}}(p\|q).
\]

Set

\[
a_k
=
\log\frac{p_k}{q_k}
+1
-\sum_j B_{kj}\frac{p_j}{q_j}.
\]

Direct differentiation gives

\[
\partial_{p_k}C_B(p)=a_k,
\qquad
\mathbb E_p[a]=C_B(p).
\]

The Fisher–Rao gradient on the simplex is therefore

\[
\boxed{
(\operatorname{grad}^{\mathrm{FR}} C_B)_k
=p_k\,[a_k-C_B(p)].
}
\]

and its squared intrinsic norm is

\[
\boxed{
S_{\mathrm{src}}^2(p,B)
=\sum_k p_k[a_k-C_B(p)]^2.
}
\]

This is the channel-aware cover-source sensitivity of exact Cachin risk. It is **not** Filler–Fridrich's Fisher information with respect to embedding rate.

### Corollary — replacement/distribution-coding channel
If every row of `B` equals a fixed output distribution `q`, then `pB=q`, and

\[
a_k=\log\frac{p_k}{q_k},
\]

so

\[
S_{\mathrm{src}}^2(p,q)
=
\operatorname{Var}_{p}\!\left[\log\frac{p_i}{q_i}\right]
=V(p\|q),
\]

the classical relative-entropy variance. The quantity `V(P||Q)` itself is not claimed as new. The proposed use is its role as the source-manifold sensitivity of an exact Cachin risk.

Hence

\[
\mathcal R_r(p,q)
=D_{\mathrm{KL}}(p\|q)
+r\sqrt{V(p\|q)}+O(r^2).
\]

## 8. Strict nominal-versus-robust separation
Assume `p != q`, both have full support, and the nominal design saturates a positive Cachin budget:

\[
D_{\mathrm{KL}}(p\|q)=\varepsilon>0.
\]

Then `V(p||q)>0`. Therefore

\[
\mathcal R_r(p,q)
=\varepsilon+r\sqrt{V(p\|q)}+O(r^2)>
\varepsilon
\]

for all sufficiently small positive `r`.

**Consequence:** a nontrivial design that merely saturates a nominal Cachin budget has no first-order robustness margin against cover-source mismatch. Robust design must either move inside the nominal security region or land at a source-stationary design.

This is a key falsifiable consequence to test experimentally.

## 9. Robust embedding-rate envelope
Let `U(theta)` be an explicitly justified embedding utility. Define

\[
R_{\mathrm{rob}}(\varepsilon,r;\hat p)
=
\sup_{\theta}
\left\{U(\theta):
\mathcal R_r(\hat p,\theta)\le\varepsilon\right\}.
\]

Until an achievability theorem is proved for a concrete encoder/decoder, this object must be called an **embedding-rate/utility envelope**, not Shannon capacity.

Properties:

1. `r=0` gives the nominal Cachin-constrained design problem;
2. `R_rob` is nonincreasing in `r` because the feasible set shrinks;
3. feasible designs carry a uniform exact-KL guarantee over the declared FR ambiguity set;
4. a nominal boundary optimum can be robust-infeasible even for arbitrarily small positive source uncertainty.

## 10. Exact categorical witness
For an ideal distribution coder with output law `q`, use the replacement-channel special case.

- **Nominal comparator:** maximize `H(q)` subject to `D_KL(p_hat||q)<=epsilon`.
- **Proposed robust design:** maximize `H(q)` subject to `R_r(p_hat,q)<=epsilon`.
- **Local diagnostic:** use the first-order approximation `D + r sqrt(V)` only as an approximation/ablation, never as the robust guarantee.
- **Oracle reference:** optimize after revealing the true source; this is an evaluation upper/reference, not a deployable baseline.

The categorical witness proves constructively that nominal feasibility and robust feasibility differ. It is not yet evidence about natural images.

## 11. Controlled sanity instance
Frozen instance:

- `p_hat=(0.6,0.3,0.1)`;
- `epsilon=0.05` nat;
- `r=0.20`;
- Fisher–Rao convention as above.

Numerically:

| design | q | H(q) bits/symbol | nominal KL | worst KL over FR ball |
|---|---|---:|---:|---:|
| nominal entropy-max | `(0.47112783,0.32461946,0.20425271)` | 1.506530 | 0.050000 | 0.122630 |
| robust candidate | `(0.55280680,0.30615730,0.14103590)` | 1.394094 | 0.008673 | 0.050000 |

The numerical inner maximization uses the exact categorical FR geometry but numerical search over the ball; these values are sanity-check evidence only.

## 12. Image witness specification after formal closure
The applied witness should use a genuinely multiparametric embedding channel, not the historical covariance proxy.

Candidate construction:

- partition natural-image residual/pixel contexts into predefined strata `g`;
- estimate nominal cover pmf `p_g` on a training-only source set;
- define a row-stochastic ternary `{-1,0,+1}` embedding channel `B_g(theta_g)`;
- induced stego law: `q_g=p_g B_g(theta_g)`;
- evaluate exact model-level Cachin risk `sum_g w_g D_KL(p_g||q_g)` under the declared factorization;
- compute Fisher quantities from derivatives of the actual probability model, never from raw feature covariance;
- realize payload with an explicit coding mechanism (e.g. syndrome coding/STC or another justified distribution matcher) before calling entropy an achieved payload;
- measure empirical steganalysis separately as external validity, not as proof of the information-theoretic theorem.

## 13. Novelty boundary after the latest prior-art search
Do **not** claim as new:

- Cachin/KL security;
- Fisher information in steganography;
- Fisher-based capacity/root-rate optimization;
- generic Fisher–Rao geometry;
- generic Riemannian constrained optimization;
- generic robustness analysis over Fisher–Rao neighborhoods;
- the existence of cover-source/channel uncertainty;
- relative-entropy variance.

The protected candidate contribution is narrower:

> A steganographic source–embedding security field that preserves exact Cachin security, separates embedding-direction Fisher sensitivity from source-direction Fisher–Rao sensitivity, derives finite-radius robust Cachin guarantees under a declared cover-model ambiguity set, and uses those guarantees to construct a multiparametric embedding design whose nominal-versus-robust behavior is experimentally falsifiable.

This wording intentionally avoids an unsupported priority claim.

## 14. Hard gate before natural-image headline experiments
Proceed only if all are true:

1. the channel-aware source-gradient formula survives symbolic/numerical checks;
2. the strict nominal-vs-robust separation is retained with exact KL orientation;
3. the image source model and uncertainty calibration are frozen without test-set tuning;
4. a concrete encoder/decoder makes claimed payload operational rather than an entropy surrogate;
5. baselines include nominal exact-KL optimization and a Filler/local-Fisher comparator where assumptions are applicable;
6. steganalysis uses contemporary unseen detectors and source-mismatch conditions;
7. no claim treats FR robustness as generic mathematical novelty.
