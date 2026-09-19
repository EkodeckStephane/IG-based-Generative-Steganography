# BOSSBase V4A numerical method lock
Status: FROZEN BEFORE V4A EXECUTION AND BEFORE HOLDOUT PIXEL ANALYSIS.
Date: 2026-09-10.

- Source parameters, stratum counts, cutpoints and r* are exactly those in `bossbase_fit_model_v4.json` and `bossbase_calibration_v4.json`.
- Discrete-Gaussian support for risk computation: k=-255,...,255, with one extra point on each side for the +/-1 mixture. At the largest fitted sigma (~17.08), omitted model tail is negligible at double precision for the intended calculations; report if numerical normalization indicates otherwise.
- Epsilon: {2e-4, 8e-4} nat/eligible carrier.
- Iso-Cachin sample: N=128 per epsilon, PCG64 seeds 20260911 and 20261011. Direction components exp(N(0,0.9^2)), normalized by max, then exact scalar projection to C=epsilon; beta<=0.2.
- Robust radii: {0.5*r*, r*, 1.5*r*}.
- Primary robust evaluation: 720 boundary directions plus center.
- Verification at r*: 2880 boundary directions plus center for every 10th sample and empirical min/Q10/median/Q90/max neighborhoods. Relative discrepancy >5e-4 triggers full 2880-direction recomputation for that epsilon.
- Nominal optimizer: SLSQP with analytic objective gradient and exact discrete-KL constraint gradient, deterministic starts {0.005 all, 0.02 all, 0.05 all}; retain highest-rate feasible solution.
- Uniform-shrink baseline: bisection on scalar s in [0,1] applied to nominal optimum, evaluated with 720 directions and verified at 2880 directions.
- Robust optimizer: SLSQP with the active-direction exact KL gradient on a 720-direction robust oracle. Deterministic starts {uniform-shrink, 0.75*nominal, shrink*(1+linear ramp -0.2..0.2), shrink*(1-linear ramp)}. Final candidate must satisfy the 2880-direction robust budget within max(5e-9,5e-5*epsilon).
- Non-scalar criterion: weighted relative L2 residual after best scalar fit to nominal design >1e-3.
- No parameter may be selected using holdout pixels.