"""
S4: Geodesic vs. Euclidean Straight-Line Paths
=========================================================
Manifold: P_theta = N(mu, sigma^2 I_2), theta = (mu1, mu2, sigma)

Outputs:
  data/s4_path_comparison.csv  -- KL ratios, failure flags, curvature at endpoints
  figures/s4_path_comparison.pdf -- box plots and failure analysis
"""

import numpy as np, csv, os
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
FIG_DIR  = os.path.join(ROOT, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR,  exist_ok=True)

# -- Fisher metric for 2D isotropic Gaussian ---------------------------------
def fisher_2d_isotropic(mu1, mu2, sigma):
    """FIM for N((mu1,mu2), sigma^2 I_2) in parameterization (mu1, mu2, sigma)."""
    inv_s2 = 1.0 / (sigma**2)
    F = np.diag([inv_s2, inv_s2, 2.0 * inv_s2])
    return F

def christoffel_2d_iso(theta):
    """Non-zero Christoffel symbols for the 2D isotropic Gaussian."""
    s = theta[2]  # sigma
    return {
        (0, 0, 2): -1.0 / s,
        (0, 2, 0): -1.0 / s,
        (1, 1, 2): -1.0 / s,
        (1, 2, 1): -1.0 / s,
        (2, 0, 0):  0.5 / s,
        (2, 1, 1):  0.5 / s,
        (2, 2, 2): -1.0 / s,
    }

def geodesic_ode_2d(t, y):
    mu1, mu2, sigma, dmu1, dmu2, dsigma = y
    s = max(sigma, 1e-10)
    Gam = christoffel_2d_iso((mu1, mu2, s))
    accel = np.zeros(3)
    dtheta = np.array([dmu1, dmu2, dsigma])
    for (k, i, j), val in Gam.items():
        accel[k] -= val * dtheta[i] * dtheta[j]
    return [dmu1, dmu2, dsigma, accel[0], accel[1], accel[2]]

def shoot_geodesic(theta0, theta1, n_pts=200, tol=1e-8):
    """
    Solve geodesic BVP by shooting.
    Returns (success_flag, t_array, mus1, mus2, sigmas, error_msg)
    """
    def residual(v):
        y0 = list(theta0) + list(v)
        sol = solve_ivp(geodesic_ode_2d, [0, 1], y0, method='RK45',
                        t_eval=np.linspace(0, 1, 100), rtol=1e-9, atol=1e-11)
        if not sol.success or np.any(~np.isfinite(sol.y[:3, -1])):
            return [1e6, 1e6, 1e6]
        return (sol.y[:3, -1] - np.array(theta1)).tolist()

    # Initial guess: straight-line velocity
    v0 = np.array(theta1) - np.array(theta0)
    try:
        v_sol = fsolve(residual, v0, full_output=False, xtol=tol, maxfev=200)
        err = residual(v_sol)
        if np.linalg.norm(err) > 1e-3:
            return False, None, None, None, None, f"endpoint_err={np.linalg.norm(err):.2e}"

        y0 = list(theta0) + list(v_sol)
        t_eval = np.linspace(0, 1, n_pts)
        sol = solve_ivp(geodesic_ode_2d, [0, 1], y0, method='RK45',
                        t_eval=t_eval, rtol=1e-9, atol=1e-11)
        return True, sol.t, sol.y[0], sol.y[1], sol.y[2], ""
    except Exception as e:
        return False, None, None, None, None, str(e)

# -- KL divergence and sequential cost ---------------------------------------
def kl_gaussian_2d(mu1_a, mu2_a, sigma_a, mu1_b, mu2_b, sigma_b):
    """KL(N(mu_a, sigma_a^2 I) || N(mu_b, sigma_b^2 I))."""
    d = 2
    ratio = sigma_a / sigma_b
    diff_sq = (mu1_a - mu1_b)**2 + (mu2_a - mu2_b)**2
    return (d * (ratio**2 - 1 - 2*np.log(ratio)) / 2.0
            + diff_sq / (2 * sigma_b**2))

def sequential_kl(mus1, mus2, sigmas, L):
    """Compute sequential KL cost at L steps."""
    n = len(mus1)
    idx = np.linspace(0, n-1, L+1).astype(int)
    total = 0.0
    for k in range(L):
        i, j = idx[k], idx[k+1]
        total += kl_gaussian_2d(mus1[i], mus2[i], sigmas[i],
                                mus1[j], mus2[j], sigmas[j])
    return total

def path_energy(mus1, mus2, sigmas):
    """Compute path energy E[gamma] = integral g(gamma', gamma') dt."""
    n = len(mus1)
    dt = 1.0 / (n - 1)
    E = 0.0
    for i in range(n - 1):
        dm1 = (mus1[i+1] - mus1[i]) / dt
        dm2 = (mus2[i+1] - mus2[i]) / dt
        ds  = (sigmas[i+1] - sigmas[i]) / dt
        s   = 0.5 * (sigmas[i+1] + sigmas[i])
        E  += (dm1**2 + dm2**2 + 2*ds**2) / (s**2) * dt
    return E

# -- experiment --------------------------------------------------------------
def run_experiment(n_pairs=50, L_values=(64, 128, 256), seed=123):
    rng = np.random.default_rng(seed)

    rows = []
    n_success = 0
    n_fail = 0
    fail_reasons = {}

    for pair_idx in range(n_pairs):
        # Random endpoints in (mu1, mu2, sigma) space
        mu_range = (-3, 3)
        s_range  = (0.5, 2.5)

        theta0 = np.array([
            rng.uniform(*mu_range),
            rng.uniform(*mu_range),
            rng.uniform(*s_range)
        ])
        theta1 = np.array([
            rng.uniform(*mu_range),
            rng.uniform(*mu_range),
            rng.uniform(*s_range)
        ])

        # Straight-line path
        t_lin = np.linspace(0, 1, 500)
        sl_mu1  = theta0[0] + (theta1[0] - theta0[0]) * t_lin
        sl_mu2  = theta0[1] + (theta1[1] - theta0[1]) * t_lin
        sl_sig  = theta0[2] + (theta1[2] - theta0[2]) * t_lin

        # Geodesic path
        success, t_geo, geo_mu1, geo_mu2, geo_sig, err_msg = \
            shoot_geodesic(theta0, theta1, n_pts=500)

        if not success:
            n_fail += 1
            fail_reasons[err_msg] = fail_reasons.get(err_msg, 0) + 1
            # Use straight line as placeholder for geodesic
            geo_mu1, geo_mu2, geo_sig = sl_mu1.copy(), sl_mu2.copy(), sl_sig.copy()
            failed_flag = True
        else:
            n_success += 1
            failed_flag = False

        # Compute metrics
        dist_endpoints = np.linalg.norm(np.array(theta1) - np.array(theta0))

        # Path energy
        E_geo = path_energy(geo_mu1, geo_mu2, geo_sig)
        E_str = path_energy(sl_mu1, sl_mu2, sl_sig)

        for L in L_values:
            kl_geo = sequential_kl(geo_mu1, geo_mu2, geo_sig, L)
            kl_str = sequential_kl(sl_mu1, sl_mu2, sl_sig, L)
            ratio = kl_str / max(kl_geo, 1e-12)

            rows.append({
                "pair":         pair_idx,
                "L":            L,
                "theta0_mu1":   round(theta0[0], 3),
                "theta0_mu2":   round(theta0[1], 3),
                "theta0_sigma": round(theta0[2], 3),
                "theta1_mu1":   round(theta1[0], 3),
                "theta1_mu2":   round(theta1[1], 3),
                "theta1_sigma": round(theta1[2], 3),
                "endpoint_dist": round(dist_endpoints, 3),
                "E_geodesic":   round(E_geo, 6),
                "E_straight":   round(E_str, 6),
                "E_ratio":      round(E_str / max(E_geo, 1e-12), 4),
                "KL_geodesic":  round(kl_geo, 8),
                "KL_straight":  round(kl_str, 8),
                "KL_ratio":     round(ratio, 4),
                "failed":       failed_flag,
            })

        if (pair_idx + 1) % 10 == 0:
            fail_rate = 100 * n_fail / (pair_idx + 1)
            print(f"  Pair {pair_idx+1:3d}: success={n_success}, fails={n_fail} "
                  f"(rate={fail_rate:.1f}%)")

    print(f"\nOverall: {n_success} successes, {n_fail} failures "
          f"({100*n_fail/max(n_success+n_fail,1):.1f}% failure rate)")
    if fail_reasons:
        print("Failure reasons:")
        for reason, count in fail_reasons.items():
            print(f"  {reason}: {count}")

    return rows, n_success, n_fail

def make_figure(rows, n_success, n_fail):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # Panel 1: KL ratio box plot by L (successful runs only)
    ax = axes[0]
    for L in (64, 128, 256):
        ratios = [r["KL_ratio"] for r in rows if r["L"] == L and not r["failed"]]
        ax.boxplot(ratios, positions=[L], widths=20, patch_artist=True,
                   boxprops=dict(facecolor="#1f77b4", alpha=0.7))
    ax.set_xticks([64, 128, 256])
    ax.set_xlabel("Discretization steps L", fontsize=11)
    ax.set_ylabel(r"$D_{KL}^{str} / D_{KL}^{geo}$", fontsize=11)
    ax.set_title("KL cost ratio by discretization\n(excluding failures)", fontsize=10)
    ax.axhline(1.0, color="red", lw=1, ls="--")
    ax.grid(True, alpha=0.3)

    # Panel 2: Path energy ratio histogram
    ax = axes[1]
    e_ratios = [r["E_ratio"] for r in rows if not r["failed"]]
    ax.hist(e_ratios, bins=20, color="#2ca02c", edgecolor="k", alpha=0.8)
    ax.axvline(np.median(e_ratios), color="red", lw=2, ls="--",
               label=f"Median = {np.median(e_ratios):.3f}")
    ax.set_xlabel(r"$E[\gamma_{str}] / E[\gamma_{geo}]$", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Path energy ratio distribution", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: Failure analysis by endpoint distance
    ax = axes[2]
    success_dists = [r["endpoint_dist"] for r in rows if not r["failed"]]
    fail_dists    = [r["endpoint_dist"] for r in rows if r["failed"]]
    ax.hist(success_dists, bins=15, color="#1f77b4", alpha=0.6,
            label=f"Success ({len(success_dists)})")
    if fail_dists:
        ax.hist(fail_dists, bins=5, color="#d62728", alpha=0.8,
                label=f"Failure ({len(fail_dists)})")
    ax.set_xlabel("Endpoint distance ||theta_1 - theta_0||", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title(f"Failure analysis\n({100*n_fail/max(n_success+n_fail,1):.1f}% failure rate)",
                 fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle("S4: Geodesic vs. Euclidean Path Comparison (REVISED)",
                 fontsize=11, y=1.02)
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "s4_path_comparison.pdf")
    fig.savefig(fig_path, bbox_inches="tight", dpi=150)
    fig.savefig(os.path.join(FIG_DIR, "s4_path_comparison.png"),
                bbox_inches="tight", dpi=150)
    print(f"Figure saved: {fig_path}")

# -- main --------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("S4 (REVISED): Geodesic vs. Euclidean Path Comparison")
    print("=" * 70)
    print("Revisions: failure rate analysis, path energy metric")
    print()

    rows, n_success, n_fail = run_experiment(
        n_pairs=50, L_values=(64, 128, 256), seed=123)

    # Summary
    success_rows = [r for r in rows if not r["failed"]]
    for L in (64, 128, 256):
        ratios = [r["KL_ratio"] for r in success_rows if r["L"] == L]
        mean_r = np.mean(ratios)
        std_r  = np.std(ratios)
        print(f"  L={L:3d}: mean KL ratio = {mean_r:.3f} +/- {std_r:.3f}  "
              f"(geodesic {(mean_r-1)*100:.1f}% cheaper)")

    # CSV
    csv_path = os.path.join(DATA_DIR, "s4_path_comparison_data.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV saved: {csv_path}")

    make_figure(rows, n_success, n_fail)
    print("S4 complete.")
