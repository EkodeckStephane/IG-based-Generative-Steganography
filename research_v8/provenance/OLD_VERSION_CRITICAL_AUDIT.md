# Critical audit note — rejected versions

## A. Cachin KL orientation error — CRITICAL
The rejected Information Sciences theory manuscript states Cachin security as

`D_KL(P_S || P_C)`

in `information_geometric_transport_THEORY_ONLY_submitted/main.tex`, lines 152–160 of the unpacked file.

The Digital Signal Processing version repeats the same definition in
`information_geometric_transport_THEORY_ONLY_submitted/Digital_Signal_Processing/IG_STEGO_PAPER.tex`, lines 283–291.

Cachin's criterion is `D_KL(P_C || P_S)`. Because KL is asymmetric, this cannot be treated as typographical. Any theorem, detector relation, Taylor expansion, optimization objective, table, or conclusion that depends on the reversed functional must be independently rederived under the canonical orientation.

### Disposition
- Do not patch THEORY_ONLY in place.
- Treat it as historical archive.
- Rebuild the formal paper from a fresh source after the formal/experimental gates close.

## B. Proxy Fisher implementations — MAJOR
`frstego_operational/frstego/geometry.py` uses empirical feature covariance as a stated Fisher proxy. That is not sufficient to support a formal Fisher-information claim about the probability model.

`cpu_stego_experiments` likewise contains variance-aware / diagonal proxy constructions. These remain exploratory controls only.

### Disposition
All new Fisher quantities must be derived from the actual probability law `p_theta` or the induced stochastic embedding channel, with explicit score derivatives and parameterization.

## C. Geodesic-path detectability — RETIRE AS CENTRAL CLAIM
An internal optimization path is generally not observed by Cachin's passive warden. The new framework therefore retains exact endpoint KL as security and uses Fisher–Rao geometry for source uncertainty, sensitivity, and constrained design rather than treating internal path length as detection probability.
