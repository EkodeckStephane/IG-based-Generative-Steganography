# Theorem Strength Audit

## Retained theorem
**Source-mismatch separation on a nominal Cachin boundary.**

For an interior finite categorical source manifold with Fisher metric, a C2 embedding operator with positive induced support, a design satisfying C(p_hat,theta)=epsilon>0, and nonzero source Fisher-Rao sensitivity S_src, there exists r0>0 such that every 0<r<r0 satisfies R_r(p_hat,theta)>epsilon.

## Five simultaneous criteria
| Criterion | Status | Evidence |
|---|---|---|
| Formal model | PASS | finite simplex, Fisher metric, exact Cachin field, explicit ambiguity ball/risk |
| Nontrivial statement | PASS | local sensitivity implies strict loss of same-budget robust feasibility |
| Design-space constraint | PASS | excludes source-sensitive nominal-boundary designs; requires slack or stationarity |
| Effective use | PASS | constraint drives the robust rate-envelope optimizer |
| Confrontation with data | PASS | V3 tests separation, V4A gives low-effect boundary, V5/V6 give inter-source separation/design consequences |

Proof check: follow the unit Fisher-gradient geodesic gamma(t). Smoothness gives C(gamma(t),theta)=epsilon+t S_src+O(t^2); positivity and interiority ensure local KL smoothness, and for sufficiently small t the geodesic remains in the normal neighborhood. Hence the robust supremum exceeds epsilon. Supporting zero-radius, monotonicity and uniform-guarantee facts remain proposition-level.
