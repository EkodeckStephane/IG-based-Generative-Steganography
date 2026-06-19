 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compute local Fisher ball volumes for a 1D two-component Gaussian mixture.

Outputs:
  results/tables/fisher_ball_volumes.csv
  results/tables/fisher_ball_volumes.tex

Model:
  p(x; pi, mu1, mu2) =
      pi * N(x; mu1, sigma^2)
    + (1-pi) * N(x; mu2, sigma^2)

Parameters:
  theta = (pi, mu1, mu2)

The Fisher metric is computed by numerical quadrature:
  F_ij(theta) = ∫ p_theta(x) score_i(x) score_j(x) dx

The Fisher ball volume is estimated by Monte Carlo integration over the
local coordinate ellipsoid:
  E_p(r) = { delta : delta^T F(p) delta <= r^2 }

and integrating sqrt(det F(theta + delta)) over that ellipsoid.

This is a local numerical Fisher-ball estimate, appropriate for the
small-radius regime discussed in the manuscript.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd
from scipy.integrate import quad


# ---------------------------------------------------------------------
# Basic geometry
# ---------------------------------------------------------------------

def unit_ball_volume(d: int) -> float:
    return math.pi ** (d / 2) / math.gamma(d / 2 + 1)


def unit_sphere_area(d: int) -> float:
    return 2 * math.pi ** (d / 2) / math.gamma(d / 2)


def euclidean_ball_volume(d: int, r: float) -> float:
    return unit_ball_volume(d) * (r ** d)


def hyperbolic_ball_volume(d: int, r: float, K: float) -> float:
    """
    Volume of radius-r ball in d-dimensional space form of curvature K.

    For K < 0:
      V_K(r) = omega_{d-1} ∫_0^r (sinh(sqrt(-K)t)/sqrt(-K))^(d-1) dt

    For K = 0:
      Euclidean volume.

    For K > 0 this function returns the spherical comparison volume,
    but Bishop--Gromov usage here is mainly for K <= 0.
    """
    if abs(K) < 1e-14:
        return euclidean_ball_volume(d, r)

    omega = unit_sphere_area(d)

    if K < 0:
        a = math.sqrt(-K)

        def integrand(t: float) -> float:
            return (math.sinh(a * t) / a) ** (d - 1)

    else:
        a = math.sqrt(K)

        def integrand(t: float) -> float:
            return (math.sin(a * t) / a) ** (d - 1)

    val, _ = quad(integrand, 0.0, r, epsabs=1e-10, epsrel=1e-8, limit=200)
    return omega * val


# ---------------------------------------------------------------------
# GMM Fisher metric
# ---------------------------------------------------------------------

def gaussian_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    z = (x - mu) / sigma
    return np.exp(-0.5 * z * z) / (math.sqrt(2 * math.pi) * sigma)


def gmm_pdf(x: np.ndarray, pi: float, mu1: float, mu2: float, sigma: float) -> np.ndarray:
    n1 = gaussian_pdf(x, mu1, sigma)
    n2 = gaussian_pdf(x, mu2, sigma)
    return pi * n1 + (1.0 - pi) * n2


def gmm_scores(
    x: np.ndarray,
    pi: float,
    mu1: float,
    mu2: float,
    sigma: float,
) -> np.ndarray:
    """
    Scores for theta = (pi, mu1, mu2).
    Returns array shape (len(x), 3).
    """
    n1 = gaussian_pdf(x, mu1, sigma)
    n2 = gaussian_pdf(x, mu2, sigma)
    p = pi * n1 + (1.0 - pi) * n2
    p = np.maximum(p, 1e-300)

    d_pi = (n1 - n2) / p
    d_mu1 = pi * n1 * (x - mu1) / (sigma ** 2) / p
    d_mu2 = (1.0 - pi) * n2 * (x - mu2) / (sigma ** 2) / p

    return np.vstack([d_pi, d_mu1, d_mu2]).T


def fisher_metric_gmm(
    pi: float,
    mu1: float,
    mu2: float,
    sigma: float = 1.0,
    n_grid: int = 20001,
    padding: float = 8.0,
) -> np.ndarray:
    """
    Numerical Fisher metric for 1D two-component GMM.

    Integration is done on a finite grid covering the effective support.
    """
    lo = min(mu1, mu2) - padding * sigma
    hi = max(mu1, mu2) + padding * sigma

    x = np.linspace(lo, hi, n_grid)
    p = gmm_pdf(x, pi, mu1, mu2, sigma)
    s = gmm_scores(x, pi, mu1, mu2, sigma)

    F = np.zeros((3, 3), dtype=float)
    for i in range(3):
        for j in range(3):
            F[i, j] = np.trapz(p * s[:, i] * s[:, j], x)

    F = 0.5 * (F + F.T)

    # Numerical stabilization only.
    eig = np.linalg.eigvalsh(F)
    if eig.min() <= 1e-12:
        F += (1e-10 - eig.min()) * np.eye(3)

    return F


def sqrt_det_metric(theta: np.ndarray, sigma: float, n_grid: int) -> float:
    pi, mu1, mu2 = theta

    if not (1e-5 < pi < 1.0 - 1e-5):
        return 0.0

    F = fisher_metric_gmm(pi, mu1, mu2, sigma=sigma, n_grid=n_grid)
    det = np.linalg.det(F)

    if det <= 0 or not np.isfinite(det):
        return 0.0

    return math.sqrt(det)


# ---------------------------------------------------------------------
# Local Fisher ball volume
# ---------------------------------------------------------------------

def sample_unit_ball(n: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """
    Uniform samples in Euclidean unit ball in R^d.
    """
    z = rng.normal(size=(n, d))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    u = rng.random(n) ** (1.0 / d)
    return z * u[:, None]


def local_fisher_ball_volume(
    theta0: Tuple[float, float, float],
    r: float,
    sigma: float = 1.0,
    n_mc: int = 20000,
    n_grid_metric: int = 4001,
    seed: int = 123,
) -> Dict[str, float]:
    """
    Estimate:
      vol_g(B_g(theta0,r))

    using the local coordinate ellipsoid:
      delta^T F(theta0) delta <= r^2

    and integrating sqrt(det F(theta0 + delta)).
    """
    rng = np.random.default_rng(seed)
    theta0_arr = np.asarray(theta0, dtype=float)
    d = len(theta0_arr)

    F0 = fisher_metric_gmm(*theta0_arr, sigma=sigma, n_grid=n_grid_metric)
    det_F0 = np.linalg.det(F0)
    cond_F0 = np.linalg.cond(F0)

    L = np.linalg.cholesky(F0)
    Linv = np.linalg.inv(L)

    u = sample_unit_ball(n_mc, d, rng)

    # Transform Euclidean unit ball to Fisher ellipsoid:
    # delta = r * L^{-1} u, so delta^T F delta = r^2 ||u||^2
    deltas = r * (u @ Linv.T)
    theta_samples = theta0_arr[None, :] + deltas

    vals = np.array([
        sqrt_det_metric(theta, sigma=sigma, n_grid=n_grid_metric)
        for theta in theta_samples
    ])

    valid_ratio = np.mean(vals > 0)

    # Coordinate ellipsoid Euclidean volume:
    # vol(E) = vol(B_d(r)) / sqrt(det F0)
    coord_ellipsoid_volume = euclidean_ball_volume(d, r) / math.sqrt(det_F0)

    # Integral over E of sqrt(det F(theta)) dtheta
    vol_g = coord_ellipsoid_volume * float(np.mean(vals))

    # Local tangent-space approximation equals Euclidean d-ball volume
    # because sqrt(det F0) cancels det(F0)^(-1/2).
    vol_tangent = euclidean_ball_volume(d, r)

    return {
        "vol_g": vol_g,
        "vol0": vol_tangent,
        "det_F": det_F0,
        "cond_F": cond_F0,
        "valid_ratio": valid_ratio,
    }


# ---------------------------------------------------------------------
# Representative points
# ---------------------------------------------------------------------

def default_points() -> List[Dict[str, float]]:
    """
    Representative GMM points.
    Adjust these to match your Simulation S3 grid if needed.
    """
    return [
        {
            "point": "GMM interior A",
            "pi": 0.50,
            "mu1": -1.00,
            "mu2": 1.00,
            "K_comp": -1.0,
        },
        {
            "point": "GMM interior B",
            "pi": 0.50,
            "mu1": -1.50,
            "mu2": 1.50,
            "K_comp": -0.5,
        },
        {
            "point": "Near-boundary GMM",
            "pi": 0.10,
            "mu1": -0.30,
            "mu2": 0.30,
            "K_comp": 0.0,
        },
    ]


def load_points(path: Path | None) -> List[Dict[str, float]]:
    if path is None:
        return default_points()

    df = pd.read_csv(path)
    required = {"point", "pi", "mu1", "mu2"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in representative points CSV: {missing}")

    if "K_comp" not in df.columns:
        df["K_comp"] = -1.0

    return df.to_dict(orient="records")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--points", type=str, default=None,
                        help="Optional CSV with columns: point,pi,mu1,mu2,K_comp")
    parser.add_argument("--sigma", type=float, default=1.0)
    parser.add_argument("--radius", type=float, default=0.15)
    parser.add_argument("--n-mc", type=int, default=20000)
    parser.add_argument("--n-grid-metric", type=int, default=4001)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--outdir", type=str, default="results/tables")

    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    points = load_points(Path(args.points) if args.points else None)

    rows = []

    for idx, p in enumerate(points):
        theta = (float(p["pi"]), float(p["mu1"]), float(p["mu2"]))
        K_comp = float(p.get("K_comp", -1.0))

        result = local_fisher_ball_volume(
            theta0=theta,
            r=args.radius,
            sigma=args.sigma,
            n_mc=args.n_mc,
            n_grid_metric=args.n_grid_metric,
            seed=args.seed + idx,
        )

        d = 3
        vol0 = euclidean_ball_volume(d, args.radius)
        VK = hyperbolic_ball_volume(d, args.radius, K_comp)

        rows.append({
            "point": p["point"],
            "pi": theta[0],
            "mu1": theta[1],
            "mu2": theta[2],
            "radius": args.radius,
            "K_comp": K_comp,
            "vol_g": result["vol_g"],
            "vol_0": vol0,
            "V_K": VK,
            "vol_g_over_vol0": result["vol_g"] / vol0,
            "vol_g_over_VK": result["vol_g"] / VK if VK > 0 else np.nan,
            "det_F": result["det_F"],
            "cond_F": result["cond_F"],
            "valid_ratio": result["valid_ratio"],
        })

    df = pd.DataFrame(rows)

    csv_path = outdir / "fisher_ball_volumes.csv"
    tex_path = outdir / "fisher_ball_volumes.tex"

    df.to_csv(csv_path, index=False)

    latex_df = df[[
        "point",
        "radius",
        "K_comp",
        "vol_g",
        "vol_0",
        "V_K",
        "vol_g_over_vol0",
        "vol_g_over_VK",
        "cond_F",
    ]].copy()

    latex_df.columns = [
        "Point",
        "$r$",
        "$K$",
        "$\\vol_g(B_g)$",
        "$\\vol_0(r)$",
        "$V_K(r)$",
        "$\\vol_g/\\vol_0$",
        "$\\vol_g/V_K$",
        "$\\kappa(F)$",
    ]

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_df.to_latex(
            index=False,
            escape=False,
            float_format=lambda x: f"{x:.4g}",
            caption=(
                "Numerically estimated local Fisher ball volumes for "
                "representative Gaussian-mixture points. The hyperbolic "
                "comparison volume $V_K$ is an upper comparison quantity, "
                "not a lower bound on the actual Fisher volume."
            ),
            label="tab:fisher_ball_volumes",
        ))

    print(f"[OK] wrote {csv_path}")
    print(f"[OK] wrote {tex_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()