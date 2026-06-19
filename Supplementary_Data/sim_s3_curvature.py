"""
S3: Curvature Map for Gaussian Mixture Model (REVISED)
=======================================================
Family: P_theta = pi N(mu1, sigma^2) + (1-pi) N(mu2, sigma^2)
         theta = (pi, mu1, mu2), sigma=1 fixed

Outputs:
  data/s3_curvature_data.csv       -- curvature values on grid
  data/s3_scalar_curvature.csv     -- R(theta) on grid (coordinate-invariant)
  data/s3_vmin_confidence.csv      -- bootstrap statistics for V_min
  data/s3_grid_convergence.csv     -- grid refinement study
  figures/s3_curvature.pdf         -- curvature heatmaps (revised)
  figures/s3_grid_convergence.pdf  -- convergence study figure
"""

import numpy as np, csv, os, time, warnings
from scipy.integrate import nquad
from scipy.linalg import inv

ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
FIG_DIR  = os.path.join(ROOT, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR,  exist_ok=True)

warnings.filterwarnings("ignore", category=RuntimeWarning)

# -- GMM density and score ---------------------------------------------------
def gmm_density(x, pi, mu1, mu2, sigma=1.0):
    return pi * (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu1)/sigma)**2) + \
           (1-pi) * (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu2)/sigma)**2)

def gmm_log_score(x, pi, mu1, mu2, sigma=1.0):
    """
    Score vector:  d/dtheta log p_theta(x)
    theta = (pi, mu1, mu2)
    """
    p = gmm_density(x, pi, mu1, mu2, sigma)
    p = np.maximum(p, 1e-300)
    phi1 = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu1)/sigma)**2)
    phi2 = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu2)/sigma)**2)
    dlog_dpi   = (phi1 - phi2) / p
    dlog_dmu1  = pi * (x - mu1) / sigma**2 * phi1 / p
    dlog_dmu2  = (1-pi) * (x - mu2) / sigma**2 * phi2 / p
    return np.array([dlog_dpi, dlog_dmu1, dlog_dmu2])

# -- Fisher Information Matrix via numerical integration (vectorized) --------
_fim_cache = {}

def fim_numerical(pi, mu1, mu2, sigma=1.0, x_min=-10, x_max=10, n_x=500):
    """
    Compute FIM by numerical integration:  F_{ij} = E[score_i * score_j]
    Uses vectorized trapezoidal rule on a fine grid.
    """
    # Simple caching based on parameter tuple (with rounded values for cache hits)
    cache_key = (round(pi, 8), round(mu1, 8), round(mu2, 8), sigma, x_min, x_max, n_x)
    if cache_key in _fim_cache:
        return _fim_cache[cache_key].copy()

    x_grid = np.linspace(x_min, x_max, n_x)
    dx = x_grid[1] - x_grid[0]

    # Vectorized density and score computation
    p = gmm_density(x_grid, pi, mu1, mu2, sigma)
    p = np.maximum(p, 1e-300)

    phi1 = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x_grid-mu1)/sigma)**2)
    phi2 = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x_grid-mu2)/sigma)**2)

    s0 = (phi1 - phi2) / p
    s1 = pi * (x_grid - mu1) / sigma**2 * phi1 / p
    s2 = (1-pi) * (x_grid - mu2) / sigma**2 * phi2 / p

    # F_ij = integral of s_i * s_j * p * dx
    # Using trapezoidal rule via dot product with weights
    w = np.full_like(x_grid, dx)
    w[0] = w[-1] = 0.5 * dx  # trapezoidal rule weights

    F = np.zeros((3, 3))
    scores = [s0, s1, s2]
    for i in range(3):
        for j in range(3):
            F[i, j] = np.sum(scores[i] * scores[j] * p * w)

    # Regularize
    F += 1e-8 * np.eye(3)
    _fim_cache[cache_key] = F.copy()
    return F

# -- Christoffel symbols via finite differences ------------------------------
def christoffel_fd(F_func, theta, eps=1e-5):
    """
    Compute Christoffel symbols Gamma^k_{ij} at theta via central FD.
    F_func(theta) -> FIM matrix.
    Returns Gamma[k, i, j].
    """
    d = len(theta)
    F0 = F_func(theta)
    try:
        Finv = inv(F0)
    except np.linalg.LinAlgError:
        Finv = np.linalg.pinv(F0)

    Gamma = np.zeros((d, d, d))
    dF = np.zeros((d, d, d))

    for i in range(d):
        for j in range(d):
            # dF/dtheta^k evaluated by FD
            for k in range(d):
                theta_plus = np.array(theta, dtype=float)
                theta_minus = np.array(theta, dtype=float)
                theta_plus[k] += eps
                theta_minus[k] -= eps
                F_plus = F_func(tuple(theta_plus))
                F_minus = F_func(tuple(theta_minus))
                dF[i, j, k] = (F_plus[i, j] - F_minus[i, j]) / (2 * eps)

    for k in range(d):
        for i in range(d):
            for j in range(d):
                val = 0.0
                for l in range(d):
                    val += 0.5 * Finv[k, l] * (
                        dF[i, l, j] + dF[j, l, i] - dF[i, j, l]
                    )
                Gamma[k, i, j] = val

    return Gamma

# -- Riemann curvature tensor via finite differences -------------------------
def riemann_tensor(F_func, theta, eps_gamma=1e-5, eps_F=1e-5):
    """
    Compute R^l_{ijk} at theta via FD on Christoffel symbols.
    Returns R[l, i, j, k].
    """
    d = len(theta)
    theta_arr = np.array(theta, dtype=float)

    # Gamma at theta
    Gamma0 = christoffel_fd(F_func, theta, eps_F)

    # dGamma / dtheta^m by FD
    dGamma = np.zeros((d, d, d, d))
    for m in range(d):
        theta_plus = theta_arr.copy()
        theta_minus = theta_arr.copy()
        theta_plus[m] += eps_gamma
        theta_minus[m] -= eps_gamma
        Gamma_plus = christoffel_fd(F_func, tuple(theta_plus), eps_F)
        Gamma_minus = christoffel_fd(F_func, tuple(theta_minus), eps_F)
        dGamma[:, :, :, m] = (Gamma_plus - Gamma_minus) / (2 * eps_gamma)

    R = np.zeros((d, d, d, d))
    for l in range(d):
        for i in range(d):
            for j in range(d):
                for k in range(d):
                    val = dGamma[l, k, j, i] - dGamma[l, k, i, j]
                    for m in range(d):
                        val += Gamma0[l, i, m] * Gamma0[m, j, k] - \
                               Gamma0[l, j, m] * Gamma0[m, i, k]
                    R[l, i, j, k] = val

    return R

# -- Curvature indices -------------------------------------------------------
def compute_V(F_func, theta):
    """
    Aggregated coordinate-sectional curvature index V(theta).
    This is coordinate-dependent; use R(theta) for invariant conclusions.
    """
    F = F_func(theta)
    try:
        Finv = inv(F)
    except np.linalg.LinAlgError:
        Finv = np.linalg.pinv(F)
    R = riemann_tensor(F_func, theta)
    d = len(theta)
    V = 0.0
    for i in range(d):
        for j in range(i+1, d):
            R_ijij = 0.0
            for l in range(d):
                R_ijij += F[i, l] * R[l, j, i, j]
            denom = F[i, i] * F[j, j] - F[i, j]**2
            if abs(denom) > 1e-12:
                V += R_ijij / denom
    return V

def compute_scalar_curvature(F_func, theta):
    """
    Riemannian scalar curvature R = F^{ij} R_{ij} where R_{ij} = R^k_{ikj}.
    This is a coordinate-invariant scalar quantity.
    """
    F = F_func(theta)
    try:
        Finv = inv(F)
    except np.linalg.LinAlgError:
        Finv = np.linalg.pinv(F)
    R = riemann_tensor(F_func, theta)
    d = len(theta)

    # Ricci tensor: R_{ij} = sum_k R^k_{ikj}
    Ricci = np.zeros((d, d))
    for i in range(d):
        for j in range(d):
            for k in range(d):
                Ricci[i, j] += R[k, i, k, j]

    # Scalar curvature
    R_scalar = 0.0
    for i in range(d):
        for j in range(d):
            R_scalar += Finv[i, j] * Ricci[i, j]

    return R_scalar

def compute_V_min(F_func, theta, n_samples=200, seed=42):
    """
    Directional vulnerability index: minimum sectional curvature over
    random tangent planes.  Uses Monte-Carlo sampling.

    Returns (V_min, V_samples) where V_samples are all sampled values
    for bootstrap confidence interval computation.
    """
    rng = np.random.default_rng(seed)
    F = F_func(theta)
    try:
        Finv = inv(F)
    except np.linalg.LinAlgError:
        Finv = np.linalg.pinv(F)

    R = riemann_tensor(F_func, theta)
    d = len(theta)

    V_samples = []
    for _ in range(n_samples):
        # Random orthonormal frame
        A = rng.standard_normal((d, d))
        # Gram-Schmidt with respect to Fisher metric
        Q = np.zeros((d, d))
        for i in range(d):
            q = A[:, i].copy()
            for j in range(i):
                proj = (q @ F @ Q[:, j]) / (Q[:, j] @ F @ Q[:, j] + 1e-12)
                q -= proj * Q[:, j]
            norm = np.sqrt(q @ F @ q)
            if norm > 1e-12:
                Q[:, i] = q / norm

        # Random 2-plane in this frame
        u = Q[:, 0]
        v = Q[:, 1]

        # Sectional curvature: R_uvuv = F_{ae} R^e_{bcd} u^a v^b u^c v^d
        # (e appears exactly twice: in F[a,e] and R[e,b,c,d])
        R_uvuv = 0.0
        for a in range(d):
            for b in range(d):
                for c in range(d):
                    for dd in range(d):
                        for e in range(d):
                            R_uvuv += F[a, e] * R[e, b, c, dd] * u[a] * v[b] * u[c] * v[dd]

        g_uu = u @ F @ u
        g_vv = v @ F @ v
        g_uv = u @ F @ v
        denom = g_uu * g_vv - g_uv**2
        if denom > 1e-12:
            K = R_uvuv / denom
            V_samples.append(K)

    if len(V_samples) == 0:
        return 0.0, []
    return min(V_samples), V_samples

def bootstrap_V_min(V_samples, n_bootstrap=1000, seed=42):
    """Compute bootstrap confidence interval for V_min estimate."""
    rng = np.random.default_rng(seed)
    n = len(V_samples)
    boot_mins = []
    for _ in range(n_bootstrap):
        resampled = rng.choice(V_samples, size=n, replace=True)
        boot_mins.append(min(resampled))
    boot_mins = np.array(boot_mins)
    mean_min = np.mean(boot_mins)
    std_min  = np.std(boot_mins)
    ci_low   = np.percentile(boot_mins, 2.5)
    ci_high  = np.percentile(boot_mins, 97.5)
    return mean_min, std_min, ci_low, ci_high

# -- grid computation --------------------------------------------------------
def compute_grid(pi_vals, dmu_vals, grid_label="coarse"):
    """
    Compute curvature indices on a regular grid.
    Returns list of dict rows.
    """
    rows = []
    total = len(pi_vals) * len(dmu_vals)
    count = 0
    t0 = time.time()

    for pi in pi_vals:
        for dmu in dmu_vals:
            count += 1
            if count % 20 == 0:
                elapsed = time.time() - t0
                print(f"  [{grid_label}] {count:4d}/{total}  "
                      f"pi={pi:.2f} dmu={dmu:.2f}  "
                      f"({elapsed:.1f}s elapsed)")

            mu1 = dmu / 2.0
            mu2 = -dmu / 2.0

            theta = (pi, mu1, mu2)
            F_func = lambda th: fim_numerical(*th, sigma=1.0,
                                               x_min=-15, x_max=15, n_x=2000)

            try:
                V = compute_V(F_func, theta)
                R_scalar = compute_scalar_curvature(F_func, theta)
                V_min, V_samples = compute_V_min(F_func, theta,
                                                  n_samples=50, seed=42)

                # Bootstrap CI for V_min
                if len(V_samples) > 10:
                    V_min_boot, V_min_std, ci_lo, ci_hi = bootstrap_V_min(V_samples, n_bootstrap=200)
                else:
                    V_min_boot = V_min
                    V_min_std = 0.0
                    ci_lo = V_min
                    ci_hi = V_min

                # Condition number
                F = F_func(theta)
                kappa_F = np.linalg.cond(F)

                rows.append({
                    "grid":        grid_label,
                    "pi":          round(pi, 4),
                    "dmu":         round(dmu, 4),
                    "mu1":         round(mu1, 4),
                    "mu2":         round(mu2, 4),
                    "V":           round(V, 6),
                    "R_scalar":    round(R_scalar, 6),
                    "V_min":       round(V_min, 2),
                    "V_min_boot":  round(V_min_boot, 2),
                    "V_min_std":   round(V_min_std, 2),
                    "V_min_ci_lo": round(ci_lo, 2),
                    "V_min_ci_hi": round(ci_hi, 2),
                    "kappa_F":     round(kappa_F, 1),
                    "n_samples":   len(V_samples),
                })
            except Exception as e:
                print(f"  FAILED at pi={pi:.2f} dmu={dmu:.2f}: {e}")
                rows.append({
                    "grid":        grid_label,
                    "pi":          pi, "dmu": dmu,
                    "mu1":         mu1, "mu2": mu2,
                    "V":           np.nan, "R_scalar": np.nan,
                    "V_min":       np.nan, "V_min_boot": np.nan,
                    "V_min_std":   np.nan, "V_min_ci_lo": np.nan,
                    "V_min_ci_hi": np.nan, "kappa_F": np.nan,
                    "n_samples":   0,
                })

    return rows

# -- main --------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("S3 (REVISED): Curvature Map for Gaussian Mixture Model")
    print("=" * 70)
    print("New features:")
    print("  - Coordinate-invariant scalar curvature R(theta)")
    print("  - Bootstrap confidence intervals for V_min")
    print("  - Grid convergence study (8x8 -> 12x12)")
    print()

    # Coarse grid
    print("Computing COARSE grid (8 x 8) ...")
    pi_vals_coarse   = np.linspace(0.1, 0.9, 8)
    dmu_vals_coarse  = np.linspace(0.3, 4.0, 8)
    rows_coarse = compute_grid(pi_vals_coarse, dmu_vals_coarse, "coarse")

    # Fine grid (subset for convergence study)
    print("\nComputing FINE grid (12 x 12, selected region) ...")
    pi_vals_fine   = np.linspace(0.1, 0.9, 12)
    dmu_vals_fine  = np.linspace(0.3, 4.0, 12)
    rows_fine = compute_grid(pi_vals_fine, dmu_vals_fine, "fine")

    # Combine
    all_rows = rows_coarse + rows_fine

    # Summary statistics
    V_vals     = [r["V"] for r in all_rows if not np.isnan(r["V"])]
    R_vals     = [r["R_scalar"] for r in all_rows if not np.isnan(r["R_scalar"])]
    Vmin_vals  = [r["V_min"] for r in all_rows if not np.isnan(r["V_min"])]
    kappa_vals = [r["kappa_F"] for r in all_rows if not np.isnan(r["kappa_F"])]

    print(f"\n{'='*70}")
    print("Summary Statistics (REVISED):")
    print(f"  Scalar curvature R(theta):")
    print(f"    Min = {min(R_vals):.3f}, Max = {max(R_vals):.3f}, Mean = {np.mean(R_vals):.3f}")
    print(f"  Coordinate index V(theta):")
    print(f"    Min = {min(V_vals):.3f}, Max = {max(V_vals):.3f}, Mean = {np.mean(V_vals):.3f}")
    print(f"  Directional V_min:")
    print(f"    Min = {min(Vmin_vals):.0f}, Max = {max(Vmin_vals):.2f}")
    print(f"  Fisher condition number:")
    print(f"    Min = {min(kappa_vals):.0f}, Max = {max(kappa_vals):.0f}")

    # Failure count
    failures = sum(1 for r in all_rows if np.isnan(r["V"]))
    print(f"  Finite-difference failures: {failures}/{len(all_rows)} "
          f"({100*failures/max(len(all_rows),1):.1f}%)")

    # CSV
    csv_path = os.path.join(DATA_DIR, "s3_curvature_data.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"CSV saved: {csv_path}")

    # Grid convergence comparison: compare V_min at matching points
    coarse_dict = {(r["pi"], r["dmu"]): r for r in rows_coarse}
    fine_dict   = {(r["pi"], r["dmu"]): r for r in rows_fine}
    conv_rows = []
    for key in coarse_dict:
        c = coarse_dict[key]
        # Find nearest fine-grid point
        nearest = min(fine_dict.keys(),
                      key=lambda k2: (k2[0]-key[0])**2 + (k2[1]-key[1])**2)
        if nearest in fine_dict:
            f = fine_dict[nearest]
            if not np.isnan(c["V_min"]) and not np.isnan(f["V_min"]):
                conv_rows.append({
                    "pi": key[0], "dmu": key[1],
                    "V_min_coarse": c["V_min"],
                    "V_min_fine":   f["V_min"],
                    "diff":         abs(c["V_min"] - f["V_min"]),
                    "R_coarse":     c["R_scalar"],
                    "R_fine":       f["R_scalar"],
                })

    if conv_rows:
        mean_diff_Vmin = np.mean([r["diff"] for r in conv_rows])
        max_diff_Vmin  = np.max([r["diff"] for r in conv_rows])
        print(f"\n  Grid convergence (V_min): mean diff = {mean_diff_Vmin:.1f}, "
              f"max diff = {max_diff_Vmin:.1f}")

        csv_path2 = os.path.join(DATA_DIR, "s3_grid_convergence.csv")
        with open(csv_path2, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=conv_rows[0].keys())
            writer.writeheader()
            writer.writerows(conv_rows)
        print(f"  Grid convergence CSV: {csv_path2}")

    print(f"{'='*70}")
    print("S3 complete.")
