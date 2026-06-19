"""
S1: Geodesics on the 2D Gaussian Statistical Manifold
===============================================================
Manifold: S_G = {N(mu, sigma^2) : mu in R, sigma > 0}
Fisher-Rao metric: g = diag(1/sigma^2, 2/sigma^2)  (in (mu, sigma) coords)

Analytical geodesics:
  - Fixed sigma: straight lines in mu  (trivial)
  - Fixed mu: sigma(t) = sigma_0 * exp(sqrt(2) * t / sigma_0)  (after normalizing)
  - General: semicircles in the upper half-plane (mu, sigma > 0)
    parameterized by center on the mu-axis and radius.

We solve the geodesic ODE numerically with RK4 and compare to the
analytical solution.

Geodesic completeness note:
  The manifold S_G for the univariate Gaussian family is geodesically
  complete: the metric is conformally equivalent to the Poincare
  half-plane metric, which is a complete Riemannian manifold.  This
  guarantees existence of minimizing geodesics between any two points.

Outputs:
  data/s1_geodesic_data.csv  -- trajectory comparison table
  figures/s1_geodesics.pdf   -- figure with four geodesic panels
"""

import numpy as np
from scipy.integrate import solve_ivp
import csv
import os

# -- paths -------------------------------------------------------------------
ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
FIG_DIR  = os.path.join(ROOT, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR,  exist_ok=True)

# -- Fisher metric and Christoffel symbols -----------------------------------
def fisher_metric(theta):
    """g = diag(1/sigma^2, 2/sigma^2)  at theta = (mu, sigma)."""
    mu, sigma = theta
    return np.diag([1.0 / sigma**2, 2.0 / sigma**2])

def christoffel(theta):
    """
    Non-zero Christoffel symbols Gamma^k_{ij} for N(mu, sigma^2).
    Returns dict  (k, i, j) -> value.
    """
    mu, sigma = theta
    s = sigma
    return {
        (0, 0, 1): -1.0 / s,   # Gamma^mu_{mu,sigma}
        (0, 1, 0): -1.0 / s,   # symmetric
        (1, 0, 0):  1.0 / (2 * s),  # Gamma^sigma_{mu,mu}
        (1, 1, 1): -1.0 / s,   # Gamma^sigma_{sigma,sigma}
    }

def geodesic_ode(t, y):
    """
    Geodesic ODE in state  y = [mu, sigma, mu', sigma'].
    d^2 theta^k / dt^2 + Gamma^k_{ij} * dtheta^i/dt * dtheta^j/dt = 0
    """
    mu, sigma, dmu, dsigma = y
    sigma = max(sigma, 1e-10)   # positivity guard: Gamma singular at sigma=0
    theta = (mu, sigma)
    Gam = christoffel(theta)
    d = 2
    accel = np.zeros(d)
    dtheta = np.array([dmu, dsigma])
    for (k, i, j), val in Gam.items():
        accel[k] -= val * dtheta[i] * dtheta[j]
    return [dmu, dsigma, accel[0], accel[1]]

# -- analytical geodesic: semicircle -----------------------------------------
def analytical_semicircle(mu0, sigma0, mu1, sigma1, n_pts=200):
    """
    The geodesic between two points on the upper half-plane equipped with
    the Poincare / Fisher-Rao metric ds^2 = dmu^2/sigma^2 + 2*dsigma^2/sigma^2
    (up to a global factor of 2) is a semicircle centred on the mu-axis.

    We use coordinates (x, y) = (mu, sigma * sqrt(2)) so the metric becomes
    the standard Poincare metric ds^2 = (dx^2 + dy^2) / y^2.
    Geodesics are then exactly Euclidean semicircles with centre on the x-axis.

    Centre c and radius R determined by:
        (mu0 - c)^2 + y0^2 = R^2
        (mu1 - c)^2 + y1^2 = R^2
    """
    y0 = sigma0 * np.sqrt(2)
    y1 = sigma1 * np.sqrt(2)

    if abs(mu0 - mu1) < 1e-10:
        # Vertical geodesic: fixed mu, sigma varies.
        # Under affine arc-length parametrization this corresponds to an
        # exponential trajectory in sigma (hyperbolic geodesic on the
        # mu-axis of the upper half-plane).
        t_arr = np.linspace(0, 1, n_pts)
        mus    = np.full(n_pts, mu0)
        sigmas = sigma0 * (sigma1 / sigma0) ** t_arr
        return mus, sigmas

    # Solve for centre c on the x-axis
    # (mu0 - c)^2 + y0^2 = (mu1 - c)^2 + y1^2
    # mu0^2 - 2*c*mu0 + y0^2 = mu1^2 - 2*c*mu1 + y1^2
    c = ((mu1**2 + y1**2) - (mu0**2 + y0**2)) / (2 * (mu1 - mu0))
    R = np.sqrt((mu0 - c)**2 + y0**2)

    angle0 = np.arctan2(y0, mu0 - c)
    angle1 = np.arctan2(y1, mu1 - c)
    # ensure we go through the upper half-plane (positive y)
    if angle0 > angle1:
        angle0, angle1 = angle1, angle0
        swap = True
    else:
        swap = False

    angles = np.linspace(angle0, angle1, n_pts)
    xs = c + R * np.cos(angles)
    ys = R * np.sin(angles)
    mus    = xs
    sigmas = ys / np.sqrt(2)
    if swap:
        mus    = mus[::-1]
        sigmas = sigmas[::-1]
    return mus, sigmas

# -- RK4 numerical geodesic --------------------------------------------------
def numerical_geodesic(mu0, sigma0, dmu0, dsigma0, T=1.0, n_pts=200):
    """Integrate geodesic ODE with dense output."""
    t_eval = np.linspace(0, T, n_pts)
    y0 = [mu0, sigma0, dmu0, dsigma0]
    sol = solve_ivp(geodesic_ode, [0, T], y0, method='RK45',
                    t_eval=t_eval, rtol=1e-10, atol=1e-12)
    return sol.t, sol.y[0], sol.y[1]  # t, mu(t), sigma(t)

def shooting_geodesic(mu0, sigma0, mu1, sigma1, n_pts=200, tol=1e-9, max_iter=50):
    """
    Boundary-value geodesic via shooting method.
    Returns (t, mus, sigmas) for the numerically computed geodesic.

    RK4 error bound: For a Lipschitz constant L_G of the Christoffel symbols,
    the global truncation error after N steps with step size h = T/N satisfies:
        |error| <= C * h^4 * T * exp(L_G * T)
    where C depends on bounds of the 5th derivative of the geodesic flow.
    For the Gaussian family, L_G ~ 1/min(sigma) near the boundary,
    so accuracy degrades as sigma -> 0.
    """
    from scipy.optimize import fsolve

    def residual(v):
        dmu0, dsigma0 = v
        # Normalise initial velocity so arc-length parameter spans [0,1]
        # (we'll just use raw velocity; RHS already integrates from 0 to 1)
        _, mus, sigmas = numerical_geodesic(mu0, sigma0, dmu0, dsigma0,
                                            T=1.0, n_pts=100)
        return [mus[-1] - mu1, sigmas[-1] - sigma1]

    # Initial guess: straight-line velocity
    v0 = [mu1 - mu0, sigma1 - sigma0]
    v_sol = fsolve(residual, v0, full_output=False, xtol=tol)
    t_arr, mus, sigmas = numerical_geodesic(mu0, sigma0, v_sol[0], v_sol[1],
                                            T=1.0, n_pts=n_pts)
    return t_arr, mus, sigmas

# -- geodesic length and path energy -----------------------------------------
def path_length(mus, sigmas):
    """Riemannian arc length along (mus, sigmas) trajectory."""
    L = 0.0
    for i in range(len(mus) - 1):
        dmu   = mus[i+1]    - mus[i]
        dsig  = sigmas[i+1] - sigmas[i]
        sig   = 0.5 * (sigmas[i+1] + sigmas[i])
        ds    = np.sqrt(dmu**2 / sig**2 + 2 * dsig**2 / sig**2)
        L    += ds
    return L

def path_energy(mus, sigmas, dt=1.0):
    """Discrete path energy E = integral g(gamma', gamma') dt."""
    n = len(mus)
    dt_step = dt / (n - 1)
    E = 0.0
    for i in range(n - 1):
        dmu  = (mus[i+1]    - mus[i])    / dt_step
        dsig = (sigmas[i+1] - sigmas[i]) / dt_step
        sig  = 0.5 * (sigmas[i+1] + sigmas[i])
        E   += (dmu**2 / sig**2 + 2 * dsig**2 / sig**2) * dt_step
    return E

# -- test cases --------------------------------------------------------------
TEST_CASES = [
    # (label, mu0, sigma0, mu1, sigma1)
    ("TC1: vary-mu",    0.0, 1.0,  3.0, 1.0),   # fixed sigma -> straight
    ("TC2: vary-sigma", 0.0, 0.5,  0.0, 2.0),   # vertical geodesic
    ("TC3: general-A",  0.0, 1.0,  2.0, 2.0),   # semicircle
    ("TC4: general-B",  1.0, 0.5,  3.0, 1.5),   # semicircle
]

N_PTS = 400

def run_all():
    rows = []
    geod_data = {}

    for label, mu0, sigma0, mu1, sigma1 in TEST_CASES:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"  ({mu0:.2f}, {sigma0:.2f}) -> ({mu1:.2f}, {sigma1:.2f})")

        # Analytical
        an_mus, an_sigmas = analytical_semicircle(mu0, sigma0, mu1, sigma1, N_PTS)
        an_len  = path_length(an_mus, an_sigmas)
        an_E    = path_energy(an_mus, an_sigmas)

        # Numerical (shooting)
        try:
            t_arr, nu_mus, nu_sigmas = shooting_geodesic(
                mu0, sigma0, mu1, sigma1, n_pts=N_PTS)
        except Exception as e:
            print(f"  Shooting failed: {e}")
            continue

        nu_len = path_length(nu_mus, nu_sigmas)
        nu_E   = path_energy(nu_mus, nu_sigmas)

        # Straight-line (Euclidean) comparison
        t_lin  = np.linspace(0, 1, N_PTS)
        sl_mus   = mu0    + (mu1    - mu0)    * t_lin
        sl_sigmas = sigma0 + (sigma1 - sigma0) * t_lin
        sl_len  = path_length(sl_mus, sl_sigmas)
        sl_E    = path_energy(sl_mus, sl_sigmas)

        # Endpoint error
        ep_err_mu  = abs(nu_mus[-1]    - mu1)
        ep_err_sig = abs(nu_sigmas[-1] - sigma1)
        ep_err     = np.sqrt(ep_err_mu**2 + ep_err_sig**2)

        # Length / energy discrepancy between numerical and analytical
        len_err = abs(nu_len - an_len) / max(an_len, 1e-12)
        E_err   = abs(nu_E  - an_E)   / max(an_E,   1e-12)

        # RK4 error estimate (theoretical bound)
        # For RK45 with local tolerance tol, global error ~ tol over unit interval
        rk4_tol = 1e-10  # rtol used in solve_ivp
        min_sigma = min(min(nu_sigmas), 1e-6)
        lipschitz_G = 1.0 / min_sigma  # Lipschitz of Christoffel symbols ~ 1/sigma
        # Conservative bound: error <= C * tol * exp(L_G * T)
        error_bound = rk4_tol * np.exp(lipschitz_G * 1.0)

        print(f"  Analytical length  = {an_len:.6f}")
        print(f"  Numerical  length  = {nu_len:.6f}  (rel err {len_err:.2e})")
        print(f"  Straight   length  = {sl_len:.6f}")
        print(f"  Endpoint error     = {ep_err:.2e}")
        print(f"  Theoretical RK4 error bound = {error_bound:.2e}")
        print(f"  Energy improvement = {(sl_E - nu_E)/sl_E * 100:.1f}%")

        rows.append({
            "test_case":        label,
            "mu0": mu0, "sigma0": sigma0, "mu1": mu1, "sigma1": sigma1,
            "analytical_length": round(an_len, 8),
            "numerical_length":  round(nu_len, 8),
            "straight_length":   round(sl_len, 8),
            "length_rel_error":  f"{len_err:.2e}",
            "endpoint_error":    f"{ep_err:.2e}",
            "rk4_error_bound":   f"{error_bound:.2e}",
            "geodesic_energy":   round(nu_E, 8),
            "straight_energy":   round(sl_E, 8),
            "energy_reduction_%": round((sl_E - nu_E) / sl_E * 100, 2),
        })

        geod_data[label] = {
            "analytical": (an_mus, an_sigmas),
            "numerical":  (nu_mus, nu_sigmas),
            "straight":   (sl_mus, sl_sigmas),
            "endpoints":  ((mu0, sigma0), (mu1, sigma1)),
        }

    # CSV
    csv_path = os.path.join(DATA_DIR, "s1_geodesic_data.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nCSV saved: {csv_path}")

    return rows, geod_data

# -- figure ------------------------------------------------------------------
def make_figure(geod_data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.flatten()

    titles = list(geod_data.keys())
    colors = {"analytical": "#1f77b4", "numerical": "#d62728", "straight": "#7f7f7f"}

    for ax, label in zip(axes, titles):
        d = geod_data[label]
        an_mus, an_sigmas = d["analytical"]
        nu_mus, nu_sigmas = d["numerical"]
        sl_mus, sl_sigmas = d["straight"]
        (mu0, sigma0), (mu1, sigma1) = d["endpoints"]

        ax.plot(an_mus, an_sigmas, color=colors["analytical"], lw=2.5,
                label="Analytical geodesic", zorder=3)
        ax.plot(nu_mus, nu_sigmas, color=colors["numerical"],  lw=1.5,
                ls="--", label="Numerical (RK45)", zorder=4)
        ax.plot(sl_mus, sl_sigmas, color=colors["straight"],   lw=1.2,
                ls=":", label="Euclidean straight", zorder=2)

        ax.scatter([mu0, mu1], [sigma0, sigma1], zorder=5, color="k", s=50)
        ax.set_xlabel(r"$\mu$", fontsize=12)
        ax.set_ylabel(r"$\sigma$", fontsize=12)
        ax.set_title(label, fontsize=10)
        ax.legend(fontsize=8, loc="best")
        ax.set_ylim(bottom=0)
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        r"Geodesics on $\mathcal{S}_\mathcal{G}=\{N(\mu,\sigma^2)\}$"
        "\nFisher-Rao metric: analytical vs. numerical (RK45 shooting)",
        fontsize=12, y=1.01
    )
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "s1_geodesics.pdf")
    fig.savefig(fig_path, bbox_inches="tight", dpi=150)
    print(f"Figure saved: {fig_path}")

    # Also save PNG for quick viewing
    fig.savefig(os.path.join(FIG_DIR, "s1_geodesics.png"), bbox_inches="tight", dpi=150)

# -- main --------------------------------------------------------------------
if __name__ == "__main__":
    rows, geod_data = run_all()
    make_figure(geod_data)
    print("\nS1 complete.")
