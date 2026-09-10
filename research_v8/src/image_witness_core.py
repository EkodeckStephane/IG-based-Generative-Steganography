"""Analytic witness core for Cachin-compatible robust steganographic design.

Model
-----
Cover residual in stratum g: X_g ~ N(0, sigma_g^2).
Symmetric ternary +/-1 embedding with probability beta_g per direction:
Q_{sigma,beta} = (1-2 beta) N(0,sigma^2)
                 + beta N(-1,sigma^2) + beta N(+1,sigma^2).

Cachin risk uses the original orientation D(P_cover || P_stego).
Source mismatch is modeled by log-scale shifts log sigma'_g = log sigma_g + a_g^T delta.
For zero-mean Gaussian scale families the per-sample Fisher information for log sigma is 2,
so the normalized Fisher metric in delta coordinates is
Gbar = (2/N) sum_g n_g a_g a_g^T.

This module is research scaffolding. Natural-image claims require a frozen estimator,
real encoder/decoder, held-out images, and empirical steganalysis.
"""
from __future__ import annotations
import math
import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import minimize
from scipy.special import logsumexp

_GH_X, _GH_W = hermgauss(64)
_LOG_SQRT_2PI = 0.5 * math.log(2.0 * math.pi)


def _log_normal(x: np.ndarray, mean: float, sigma: np.ndarray | float) -> np.ndarray:
    sigma = np.asarray(sigma, dtype=float)
    return -_LOG_SQRT_2PI - np.log(sigma) - 0.5 * ((x - mean) / sigma) ** 2


def exact_cachin_kl_gaussian_lsbm(sigma: float, beta: float) -> float:
    """D(N(0,sigma^2) || Q_{sigma,beta}) in nats by Gauss-Hermite quadrature."""
    if sigma <= 0 or beta < 0 or beta >= 0.5:
        return math.inf
    if beta == 0:
        return 0.0
    x = math.sqrt(2.0) * sigma * _GH_X
    lp = _log_normal(x, 0.0, sigma)
    terms = np.vstack([
        math.log1p(-2.0 * beta) + lp,
        math.log(beta) + _log_normal(x, -1.0, sigma),
        math.log(beta) + _log_normal(x, +1.0, sigma),
    ])
    lq = logsumexp(terms, axis=0)
    return float(np.dot(_GH_W, lp - lq) / math.sqrt(math.pi))


def embedding_fisher_at_zero(sigma: float) -> float:
    """Exact Fisher information wrt beta at beta=0 for the Gaussian +/-1 mixture path.

    I_beta(sigma,0) = 4 [cosh(1/sigma^2) - 1].
    Hence D(P||Q_beta) = 0.5*I_beta*beta^2 + O(beta^3).
    """
    if sigma <= 0:
        return math.inf
    return 4.0 * (math.cosh(1.0 / (sigma * sigma)) - 1.0)


def local_fisher_kl(sigma: float, beta: float) -> float:
    return 0.5 * embedding_fisher_at_zero(sigma) * beta * beta


def mipod_large_sigma_kl(sigma: float, beta: float) -> float:
    """Large-sigma leading term of exact local KL: beta^2/sigma^4."""
    return beta * beta / sigma**4


def ternary_entropy_bits(beta: float) -> float:
    if beta <= 0:
        return 0.0
    if beta >= 0.5:
        return 1.0
    p0 = 1.0 - 2.0 * beta
    return -(2.0 * beta * math.log2(beta) + p0 * math.log2(p0))


def ideal_rate_bpp(counts, betas) -> float:
    counts = np.asarray(counts, float)
    betas = np.asarray(betas, float)
    return float(np.dot(counts, [ternary_entropy_bits(b) for b in betas]) / counts.sum())


def nominal_exact_risk(sigmas, counts, betas, eta_shift=None) -> float:
    sigmas = np.asarray(sigmas, float)
    counts = np.asarray(counts, float)
    betas = np.asarray(betas, float)
    if eta_shift is None:
        eta_shift = np.zeros_like(sigmas)
    shifted = sigmas * np.exp(np.asarray(eta_shift, float))
    vals = np.array([exact_cachin_kl_gaussian_lsbm(s, b) for s, b in zip(shifted, betas)])
    return float(np.dot(counts, vals) / counts.sum())


def nominal_local_fisher_risk(sigmas, counts, betas) -> float:
    sigmas = np.asarray(sigmas, float)
    counts = np.asarray(counts, float)
    betas = np.asarray(betas, float)
    vals = np.array([local_fisher_kl(s, b) for s, b in zip(sigmas, betas)])
    return float(np.dot(counts, vals) / counts.sum())


def normalized_source_fisher_metric(counts, modes) -> np.ndarray:
    """Metric for nuisance delta when eta_g = a_g^T delta.

    modes[g,k] = coefficient of nuisance coordinate k in log-sigma shift of stratum g.
    Gbar = 2/N A^T diag(n_g) A.
    """
    counts = np.asarray(counts, float)
    A = np.asarray(modes, float)
    return (2.0 / counts.sum()) * (A.T @ (counts[:, None] * A))


def ellipse_boundary_2d(G: np.ndarray, radius: float, nphi: int = 720) -> np.ndarray:
    """Points delta satisfying delta^T G delta = radius^2 for SPD 2x2 G."""
    G = np.asarray(G, float)
    if G.shape != (2, 2):
        raise ValueError("2D nuisance geometry required")
    L = np.linalg.cholesky(G)
    phi = np.linspace(0.0, 2.0 * math.pi, nphi, endpoint=False)
    u = radius * np.column_stack([np.cos(phi), np.sin(phi)])
    return np.linalg.solve(L.T, u.T).T


def robust_exact_risk_2d(sigmas, counts, betas, modes, radius, nphi=720):
    sigmas = np.asarray(sigmas, float)
    counts = np.asarray(counts, float)
    betas = np.asarray(betas, float)
    A = np.asarray(modes, float)
    G = normalized_source_fisher_metric(counts, A)
    deltas = ellipse_boundary_2d(G, radius, nphi=nphi)
    risks = np.empty(len(deltas))
    for i, d in enumerate(deltas):
        risks[i] = nominal_exact_risk(sigmas, counts, betas, A @ d)
    j = int(np.argmax(risks))
    return float(risks[j]), deltas[j], A @ deltas[j]


def optimize_nominal_exact(sigmas, counts, epsilon, beta_max=0.2):
    g = len(sigmas)
    x0 = np.full(g, 0.01)
    con = {"type": "ineq", "fun": lambda b: epsilon - nominal_exact_risk(sigmas, counts, b)}
    res = minimize(lambda b: -ideal_rate_bpp(counts, b), x0,
                   bounds=[(1e-9, beta_max)] * g, constraints=con,
                   method="SLSQP", options={"ftol": 1e-12, "maxiter": 1000})
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def optimize_local_fisher(sigmas, counts, epsilon, beta_max=0.2):
    g = len(sigmas)
    x0 = np.full(g, 0.01)
    con = {"type": "ineq", "fun": lambda b: epsilon - nominal_local_fisher_risk(sigmas, counts, b)}
    res = minimize(lambda b: -ideal_rate_bpp(counts, b), x0,
                   bounds=[(1e-9, beta_max)] * g, constraints=con,
                   method="SLSQP", options={"ftol": 1e-12, "maxiter": 1000})
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def optimize_robust_exact_2d(sigmas, counts, modes, epsilon, radius, beta_max=0.2, nphi=240):
    g = len(sigmas)
    x0 = np.full(g, 0.006)
    con = {"type": "ineq", "fun": lambda b: epsilon - robust_exact_risk_2d(
        sigmas, counts, b, modes, radius, nphi=nphi)[0]}
    res = minimize(lambda b: -ideal_rate_bpp(counts, b), x0,
                   bounds=[(1e-9, beta_max)] * g, constraints=con,
                   method="SLSQP", options={"ftol": 2e-10, "maxiter": 700})
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def uniform_shrink_to_robust_feasibility(nominal_betas, sigmas, counts, modes, epsilon, radius, nphi=720):
    nominal_betas = np.asarray(nominal_betas, float)
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        risk, _, _ = robust_exact_risk_2d(sigmas, counts, mid * nominal_betas, modes, radius, nphi=nphi)
        if risk <= epsilon:
            lo = mid
        else:
            hi = mid
    return lo * nominal_betas, lo

# --- Faster vectorized helpers for confirmatory controlled grid ---
def exact_cachin_kl_gaussian_lsbm_vec(sigmas, betas):
    """Vectorized exact KL for broadcast-compatible sigma/beta arrays."""
    s = np.asarray(sigmas, float)
    b = np.asarray(betas, float)
    if np.any(s <= 0) or np.any(b < 0) or np.any(b >= 0.5):
        raise ValueError("invalid sigma/beta")
    z = _GH_X
    x_over_s2 = (math.sqrt(2.0) * z) / s[..., None]
    a = np.exp(-0.5 / (s * s))[..., None]
    ratio = (1.0 - 2.0 * b)[..., None] + 2.0 * b[..., None] * a * np.cosh(x_over_s2)
    vals = -np.log(ratio)
    return np.sum(vals * _GH_W, axis=-1) / math.sqrt(math.pi)


def robust_exact_risk_2d_fast(sigmas, counts, betas, modes, radius, nphi=240, radial_levels=(1.0,)):
    sigmas = np.asarray(sigmas, float)
    counts = np.asarray(counts, float)
    betas = np.asarray(betas, float)
    A = np.asarray(modes, float)
    Gm = normalized_source_fisher_metric(counts, A)
    candidates = []
    for frac in radial_levels:
        if frac == 0:
            candidates.append(np.zeros((1, 2)))
        else:
            candidates.append(ellipse_boundary_2d(Gm, radius * float(frac), nphi=nphi))
    deltas = np.vstack(candidates)
    eta = deltas @ A.T
    shifted = sigmas[None, :] * np.exp(eta)
    bmat = np.broadcast_to(betas[None, :], shifted.shape)
    kl = exact_cachin_kl_gaussian_lsbm_vec(shifted, bmat)
    risks = (kl @ counts) / counts.sum()
    j = int(np.argmax(risks))
    return float(risks[j]), deltas[j], eta[j]


def optimize_robust_exact_2d_fast(sigmas, counts, modes, epsilon, radius, beta_max=0.2, nphi=120):
    if radius == 0:
        return optimize_nominal_exact(sigmas, counts, epsilon, beta_max=beta_max)
    g = len(sigmas)
    x0 = np.full(g, 0.004)
    con = {"type": "ineq", "fun": lambda b: epsilon - robust_exact_risk_2d_fast(
        sigmas, counts, b, modes, radius, nphi=nphi)[0]}
    res = minimize(lambda b: -ideal_rate_bpp(counts, b), x0,
                   bounds=[(1e-9, beta_max)] * g, constraints=con,
                   method="SLSQP", options={"ftol": 3e-10, "maxiter": 700})
    if not res.success:
        raise RuntimeError(res.message)
    return res.x


def uniform_shrink_to_robust_feasibility_fast(nominal_betas, sigmas, counts, modes, epsilon, radius, nphi=720):
    if radius == 0:
        return np.asarray(nominal_betas, float).copy(), 1.0
    nominal_betas = np.asarray(nominal_betas, float)
    lo, hi = 0.0, 1.0
    for _ in range(45):
        mid = 0.5 * (lo + hi)
        risk, _, _ = robust_exact_risk_2d_fast(sigmas, counts, mid * nominal_betas, modes, radius, nphi=nphi)
        if risk <= epsilon:
            lo = mid
        else:
            hi = mid
    return lo * nominal_betas, lo


def weighted_standardized_logsigma_modes(sigmas, counts):
    """Two nuisance modes [global scale, texture-dependent scale]."""
    sigmas = np.asarray(sigmas, float)
    counts = np.asarray(counts, float)
    w = counts / counts.sum()
    x = np.log(sigmas)
    mu = float(np.dot(w, x))
    sd = math.sqrt(float(np.dot(w, (x - mu) ** 2)))
    if sd <= 0:
        raise ValueError("heterogeneous sigmas required")
    z = (x - mu) / sd
    return np.column_stack([np.ones_like(z), z]), z
