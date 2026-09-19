# BOSSBase V4A — Pre-holdout closure decision

**Decision: FAIL ON MATERIALITY — PIVOT BEFORE HOLDOUT.**

Frozen calibrated radius: r* = 0.0379528386130752. Primary criterion: D80>=0.05 at r* for at least one epsilon and positive for both.

| epsilon | D80 at r* | robust gain vs uniform shrink | non-scalar residual |
|---:|---:|---:|---:|
| 2e-4 | 0.021756 | 1.586% | 0.018053 |
| 8e-4 | 0.038699 | 1.928% | 0.018226 |

Both D80 values are positive but below 0.05. Parametric fit, finite radius, robust-budget certification, non-scalar design and fast/original-oracle numerical cross-checks pass. The diagnostic 1.5r* result is retained only as a boundary observation and does not replace the frozen primary radius.

Scientific consequence: small naturally calibrated within-source variation produces positive but sub-threshold iso-Cachin differentiation. The next source model is registered as a new stage rather than obtained by changing this criterion.
