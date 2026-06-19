"""
S2: Natural Gradient vs. Euclidean Gradient on Diagonal Gaussian
=================================================================
Model: P_theta = N(theta, Sigma) with diagonal, fixed covariance.
       theta in R^d, Sigma = diag(sigma_1^2, ..., sigma_d^2).

This is the "most favorable" case: Fisher metric is diagonal and constant,
KL objective is quadratic, so NG converges in a single step.
The speedup reported here is therefore an upper bound on the improvement.

For the non-diagonal case (full Gaussian with mu and Sigma), see
sim_s2_nondiagonal.py (S2-EXT).
"""

import numpy as np
import csv, os

ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def kl_diagonal_gaussian(theta, theta_star, Sigma):
    """D_KL(N(theta, Sigma) || N(theta_star, Sigma))."""
    diff = theta - theta_star
    return 0.5 * np.sum(diff**2 / np.diag(Sigma))

def fisher_diagonal(Sigma):
    """F = Sigma^{-1} (diagonal, constant)."""
    return np.diag(1.0 / np.diag(Sigma))

def run_experiment(d=50, kappa=100, n_runs=50, seed=42):
    rng = np.random.default_rng(seed)

    # Geometric spacing of sigma_i to achieve desired condition number
    sigma_min = 0.2
    sigma_max = sigma_min * np.sqrt(kappa)
    sigmas = np.geomspace(sigma_min, sigma_max, num=d)
    Sigma  = np.diag(sigmas**2)
    F      = fisher_diagonal(Sigma)
    F_inv  = np.diag(1.0 / np.diag(F))

    rows = []
    iters_E = []
    iters_NG = []

    for run in range(n_runs):
        theta_star = rng.standard_normal(d)
        theta_E = theta_star + rng.standard_normal(d)
        theta_NG = theta_E.copy()
        eps = 1e-6
        max_iter = 2000

        kl_E = kl_diagonal_gaussian(theta_E, theta_star, Sigma)
        kl_NG = kl_E

        conv_E = None
        conv_NG = None

        for t in range(1, max_iter + 1):
            if conv_E is None:
                grad_E = F @ (theta_E - theta_star)
                eta_E = 1.0 / np.max(np.diag(F))
                theta_E -= eta_E * grad_E
                kl_E = kl_diagonal_gaussian(theta_E, theta_star, Sigma)
                if kl_E < eps:
                    conv_E = t

            if conv_NG is None:
                grad_NG = F @ (theta_NG - theta_star)
                theta_NG -= F_inv @ grad_NG  # eta_NG = 1
                kl_NG = kl_diagonal_gaussian(theta_NG, theta_star, Sigma)
                if kl_NG < eps:
                    conv_NG = t

            if conv_E is not None and conv_NG is not None:
                break

        conv_E = conv_E or max_iter
        conv_NG = conv_NG or max_iter
        iters_E.append(conv_E)
        iters_NG.append(conv_NG)

        rows.append({
            "run": run,
            "d": d,
            "kappa_F": kappa,
            "iters_E": conv_E,
            "iters_NG": conv_NG,
            "ratio": round(conv_E / max(conv_NG, 1), 1),
        })

    return rows, iters_E, iters_NG

if __name__ == "__main__":
    print("S2: NG-Stego (diagonal case -- most favorable)")
    rows, iters_E, iters_NG = run_experiment(d=50, kappa=100, n_runs=50, seed=42)

    mean_E = np.mean(iters_E)
    mean_NG = np.mean(iters_NG)
    print(f"  Mean iterations: Euclidean={mean_E:.1f}, NG={mean_NG:.1f}")
    print(f"  Speedup: {mean_E/mean_NG:.0f}x")

    csv_path = os.path.join(DATA_DIR, "s2_gradient_data.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV saved: {csv_path}")
