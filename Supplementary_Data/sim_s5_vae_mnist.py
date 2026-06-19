"""
S5: Geodesic vs. Euclidean Embedding in a Learned MNIST Generator
=================================================================

We train a small VAE with a 2-D latent space on MNIST.  The decoder defines
a Bernoulli generative model p(x|z).  The Fisher information matrix on the
latent space (the pullback metric of the decoder) is

    F(z) = sum_i  1/(pi_i(z)(1-pi_i(z)))  grad_z pi_i(z) grad_z pi_i(z)^T.

We compare two embedding strategies between a cover latent z0 and a message
latent z1:
  - Euclidean straight line in the latent code.
  - Fisher-preconditioned natural-gradient (NG) path, which locally follows
the decoder pullback metric and approximates the Fisher-Rao geodesic.

A small CNN steganalyzer is trained on Euclidean embeddings and then applied
to both kinds of paths; the NG path is expected to accumulate a lower
detection score.

Outputs:
  data/s5_vae_mnist.pt           -- trained VAE checkpoint
  data/s5_vae_results.csv        -- quantitative comparison table
  figures/s5_latent_paths.pdf
  figures/s5_image_strip.pdf
  figures/s5_detector_profile.pdf
"""

import os
import csv
import json
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


# -----------------------------------------------------------------------------
# paths
# -----------------------------------------------------------------------------
ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
FIG_DIR = os.path.join(ROOT, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

CHECKPOINT = os.path.join(DATA_DIR, "s5_vae_mnist.pt")
RESULTS_CSV = os.path.join(DATA_DIR, "s5_vae_results.csv")
RESULTS_JSON = os.path.join(DATA_DIR, "s5_vae_summary.json")

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------------------------------------------------------
# VAE model
# -----------------------------------------------------------------------------
class VAE(nn.Module):
    def __init__(self, latent_dim=2):
        super().__init__()
        self.latent_dim = latent_dim
        # encoder
        self.enc = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        self.fc_mu = nn.Linear(64, latent_dim)
        self.fc_logvar = nn.Linear(64, latent_dim)
        # decoder (Bernoulli logits)
        self.dec = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 784),
        )

    def encode(self, x):
        h = self.enc(x.view(-1, 784))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterise(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode_logits(self, z):
        return self.dec(z)

    def decode_prob(self, z):
        return torch.sigmoid(self.decode_logits(z))

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterise(mu, logvar)
        return self.decode_prob(z), mu, logvar


def loss_vae(recon_x, x, mu, logvar):
    bce = F.binary_cross_entropy(recon_x, x.view(-1, 784), reduction="sum")
    kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return bce + kld


def train_vae(epochs=15, batch_size=256, lr=1e-3):
    print("Loading MNIST ...")
    transform = transforms.Compose([transforms.ToTensor()])
    train_ds = datasets.MNIST(DATA_DIR, train=True, download=True, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    model = VAE(latent_dim=2).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    print("Training VAE ...")
    t0 = time.time()
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for x, _ in train_loader:
            x = x.to(DEVICE)
            recon, mu, logvar = model(x)
            loss = loss_vae(recon, x, mu, logvar) / x.size(0)
            opt.zero_grad()
            loss.backward()
            opt.step()
            train_loss += loss.item()
        print(f"  epoch {epoch+1:02d}/{epochs}: loss = {train_loss/len(train_loader):.2f}  "
              f"({time.time()-t0:.1f}s)")

    torch.save(model.state_dict(), CHECKPOINT)
    print(f"Saved checkpoint to {CHECKPOINT}")
    return model


def load_or_train_vae():
    model = VAE(latent_dim=2).to(DEVICE)
    if os.path.exists(CHECKPOINT):
        print(f"Loading checkpoint {CHECKPOINT}")
        model.load_state_dict(torch.load(CHECKPOINT, map_location=DEVICE))
    else:
        model = train_vae(epochs=15)
    model.eval()
    return model

# -----------------------------------------------------------------------------
# Fisher metric on latent space (pullback of Bernoulli decoder)
# -----------------------------------------------------------------------------
def fisher_metric(model, z, eps=1e-5):
    """
    Compute F(z) = J^T W J for the Bernoulli decoder, where
    W_i = 1 / (pi_i (1-pi_i)).
    z is a torch tensor of shape (2,) (may require grad).
    Returns a torch tensor F of shape (2,2).
    """
    z = z.detach().clone().requires_grad_(True)
    pi = model.decode_prob(z)  # (784,)
    pi = torch.clamp(pi, eps, 1.0 - eps)
    # Jacobian of decoder probability w.r.t. z: shape (784, 2)
    J = torch.autograd.functional.jacobian(model.decode_prob, z, create_graph=True)
    W = 1.0 / (pi * (1.0 - pi))  # (784,)
    F = J.T @ (W.unsqueeze(1) * J)
    return F


def path_energy_numpy(model, path):
    """Discrete Fisher path energy of a numpy path (M,2)."""
    zs = torch.tensor(path, dtype=torch.float32, device=DEVICE)
    M = zs.shape[0]
    E = 0.0
    with torch.no_grad():
        for k in range(M - 1):
            mid = 0.5 * (zs[k] + zs[k + 1])
            F = fisher_metric(model, mid)
            dz = zs[k + 1] - zs[k]
            E += (dz @ (F @ dz)).item() * M
    return E


def compute_ng_path(model, z0, z1, n_steps=30, alpha=0.15):
    """
    Fisher-preconditioned gradient descent on 0.5 ||z - z1||^2.
    Returns a numpy array of shape (n_steps, 2) with z0 as first point and
    the final iterate as last point.
    """
    z = torch.tensor(z0, dtype=torch.float32, device=DEVICE, requires_grad=False)
    z_target = torch.tensor(z1, dtype=torch.float32, device=DEVICE)
    path = [z.cpu().numpy().copy()]
    for _ in range(n_steps - 1):
        z.requires_grad_(True)
        F = fisher_metric(model, z).detach()
        # gradient of 0.5 ||z - z_target||^2 is z - z_target
        g = z - z_target
        # preconditioned update
        try:
            dz = torch.linalg.solve(F, g)
        except Exception:
            dz = torch.linalg.lstsq(F, g).solution
        with torch.no_grad():
            z = z - alpha * dz
        path.append(z.cpu().numpy().copy())
    return np.array(path)

# -----------------------------------------------------------------------------
# helpers: class means, decoding images
# -----------------------------------------------------------------------------
@torch.no_grad()
def class_mean_latents(model, test_loader):
    """Return mean latent vector for each MNIST digit."""
    sums = [torch.zeros(2, device=DEVICE) for _ in range(10)]
    counts = [0 for _ in range(10)]
    for x, y in test_loader:
        x = x.to(DEVICE)
        mu, _ = model.encode(x)
        for digit in range(10):
            mask = (y == digit)
            if mask.any():
                sums[digit] += mu[mask].sum(dim=0)
                counts[digit] += mask.sum().item()
    return torch.stack([s / max(1, c) for s, c in zip(sums, counts)]).cpu().numpy()


def decode_image(model, z):
    with torch.no_grad():
        zt = torch.tensor(z, dtype=torch.float32, device=DEVICE)
        pi = model.decode_prob(zt).cpu().numpy()
    return pi.reshape(28, 28)

# -----------------------------------------------------------------------------
# Steganalyzer: small CNN
# -----------------------------------------------------------------------------
class Steganalyzer(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(32 * 7 * 7, 64), nn.ReLU(),
            nn.Linear(64, 1), nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)


def build_detector_dataset(model, class_means, n_train_pairs=45, n_steps=20):
    """
    Generate cover and stego images for training a detector.
    Stego examples come from Euclidean paths between digit class means.
    Cover examples come from small clouds around source means.
    """
    model.eval()
    covers, stegos = [], []
    pairs = [(i, j) for i in range(10) for j in range(i + 1, 10)]
    pairs = pairs[:n_train_pairs]

    with torch.no_grad():
        for src, tgt in pairs:
            z0 = class_means[src]
            z1 = class_means[tgt]
            t = np.linspace(0, 1, n_steps)
            for tt in t[1:]:
                z = (1 - tt) * z0 + tt * z1
                zt = torch.tensor(z, dtype=torch.float32, device=DEVICE)
                img = model.decode_prob(zt).cpu().numpy().reshape(28, 28)
                stegos.append(img)
            # cover cloud around source
            for _ in range(2):
                z = z0 + np.random.randn(2) * 0.5
                zt = torch.tensor(z, dtype=torch.float32, device=DEVICE)
                img = model.decode_prob(zt).cpu().numpy().reshape(28, 28)
                covers.append(img)

    X = np.stack(covers + stegos)[:, None, :, :].astype(np.float32)
    y = np.array([0.0] * len(covers) + [1.0] * len(stegos), dtype=np.float32)
    return X, y


def train_detector(model, class_means, epochs=15, batch_size=128):
    print("Training steganalyzer ...")
    X, y = build_detector_dataset(model, class_means)
    dataset = torch.utils.data.TensorDataset(torch.from_numpy(X), torch.from_numpy(y).unsqueeze(1))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    net = Steganalyzer().to(DEVICE)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    criterion = nn.BCELoss()
    t0 = time.time()
    for epoch in range(epochs):
        net.train()
        total_loss = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            pred = net(xb)
            loss = criterion(pred, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item() * xb.size(0)
        total_loss /= len(dataset)
        print(f"  detector epoch {epoch+1:02d}/{epochs}: loss = {total_loss:.4f}  "
              f"({time.time()-t0:.1f}s)")
    net.eval()
    return net


def detector_scores(net, images):
    """images: numpy array (N,1,28,28). Returns probabilities (N,)."""
    with torch.no_grad():
        x = torch.from_numpy(images).to(DEVICE)
        p = net(x).cpu().numpy().ravel()
    return p

# -----------------------------------------------------------------------------
# main experiment
# -----------------------------------------------------------------------------
def main():
    model = load_or_train_vae()

    # load test set for class means
    transform = transforms.Compose([transforms.ToTensor()])
    test_ds = datasets.MNIST(DATA_DIR, train=False, download=True, transform=transform)
    test_loader = DataLoader(test_ds, batch_size=500, shuffle=False)
    class_means = class_mean_latents(model, test_loader)
    print("Class mean latents:\n", class_means)

    # train detector on Euclidean embeddings
    detector = train_detector(model, class_means)

    # test pairs: choose visually / geometrically distinct digits
    test_pairs = [(0, 1), (3, 8), (8, 9)]
    n_steps = 30

    results = []
    all_paths = {}  # (src,tgt) -> {'euclid': path, 'ng': path}

    for src, tgt in test_pairs:
        print(f"\nPair {src}->{tgt}")
        z0 = class_means[src]
        z1 = class_means[tgt]

        # Euclidean path
        t = np.linspace(0, 1, n_steps)
        euclid = np.array([(1 - tt) * z0 + tt * z1 for tt in t])

        # NG path
        print("  computing NG path ...")
        ng = compute_ng_path(model, z0, z1, n_steps=n_steps, alpha=0.15)

        all_paths[(src, tgt)] = {"euclid": euclid, "ng": ng}

        # energies
        E_euclid = path_energy_numpy(model, euclid)
        E_ng = path_energy_numpy(model, ng)
        print(f"  energy: euclid={E_euclid:.3f}, ng={E_ng:.3f}")

        # detector scores along paths
        def score_path(path):
            imgs = np.stack([decode_image(model, z) for z in path])[:, None, :, :]
            p = detector_scores(detector, imgs)
            # accumulated log-odds (avoid inf)
            eps = 1e-6
            logodds = np.log((p + eps) / (1 - p + eps))
            return p, logodds.cumsum()

        p_e, acc_e = score_path(euclid)
        p_g, acc_g = score_path(ng)

        results.append({
            "src": src, "tgt": tgt,
            "E_euclid": float(E_euclid), "E_ng": float(E_ng),
            "E_reduction": float((E_euclid - E_ng) / E_euclid),
            "acc_euclid": float(acc_e[-1]), "acc_ng": float(acc_g[-1]),
            "acc_reduction": float((acc_e[-1] - acc_g[-1]) / acc_e[-1]),
            "final_p_euclid": float(p_e[-1]), "final_p_ng": float(p_g[-1]),
        })

    # save quantitative results
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved results to {RESULTS_CSV}")

    # summary averages
    avg = {k: float(np.mean([r[k] for r in results]))
           for k in results[0].keys() if k not in ("src", "tgt")}
    avg["src"] = "avg"
    avg["tgt"] = ""
    with open(RESULTS_JSON, "w") as f:
        json.dump({"per_pair": results, "average": avg}, f, indent=2)
    print("Average reductions:")
    for k in ["E_reduction", "acc_reduction"]:
        print(f"  {k}: {avg[k]:.1%}")

    # -------------------------------------------------------------------------
    # figures
    # -------------------------------------------------------------------------
    # background latent scatter from a subset of the test set
    print("Building latent scatter background ...")
    z_bg, y_bg = [], []
    with torch.no_grad():
        for x, y in test_loader:
            x = x.to(DEVICE)
            mu, _ = model.encode(x)
            z_bg.append(mu.cpu().numpy())
            y_bg.append(y.numpy())
            if len(y_bg) * x.size(0) >= 5000:
                break
    z_bg = np.vstack(z_bg)[:5000]
    y_bg = np.concatenate(y_bg)[:5000]

    # ---- figure 1: latent paths ----
    fig, ax = plt.subplots(figsize=(6, 5.5))
    scatter = ax.scatter(z_bg[:, 0], z_bg[:, 1], c=y_bg, cmap="tab10", s=5,
                         alpha=0.35, edgecolors="none")
    ax.scatter(class_means[:, 0], class_means[:, 1], c="black", s=80,
               marker="*", zorder=5, label="class means")
    colors = ["#d62728", "#2ca02c", "#9467bd"]
    for (src, tgt), col in zip(test_pairs, colors):
        e = all_paths[(src, tgt)]["euclid"]
        g = all_paths[(src, tgt)]["ng"]
        ax.plot(e[:, 0], e[:, 1], "--", color=col, lw=1.5,
                label=f"Euc {src}->{tgt}")
        ax.plot(g[:, 0], g[:, 1], "-", color=col, lw=2,
                label=f"NG {src}->{tgt}")
    ax.set_xlabel(r"$z_1$")
    ax.set_ylabel(r"$z_2$")
    ax.set_title("Latent-space paths under the decoder pullback metric")
    ax.legend(loc="best", fontsize=7)
    plt.colorbar(scatter, ax=ax, label="digit")
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "s5_latent_paths.pdf"), dpi=300)
    plt.close(fig)
    print("Saved s5_latent_paths.pdf")

    # ---- figure 2: image strip for pair 0->1 ----
    pair = (0, 1)
    e = all_paths[pair]["euclid"]
    g = all_paths[pair]["ng"]
    n_show = 12
    idx = np.linspace(0, n_steps - 1, n_show).astype(int)
    fig, axes = plt.subplots(2, n_show, figsize=(n_show * 0.9, 2.0))
    for k, i in enumerate(idx):
        axes[0, k].imshow(decode_image(model, e[i]), cmap="gray", vmin=0, vmax=1)
        axes[0, k].axis("off")
        axes[1, k].imshow(decode_image(model, g[i]), cmap="gray", vmin=0, vmax=1)
        axes[1, k].axis("off")
    axes[0, 0].set_ylabel("Euclidean", fontsize=9)
    axes[1, 0].set_ylabel("NG", fontsize=9)
    fig.suptitle(f"Generated images along embedding paths (digit {pair[0]} -> {pair[1]})", fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "s5_image_strip.pdf"), dpi=300)
    plt.close(fig)
    print("Saved s5_image_strip.pdf")

    # ---- figure 3: detector profile for pair 0->1 ----
    p_e, acc_e = score_path(e)
    p_g, acc_g = score_path(g)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
    ax1.plot(p_e, "--s", color="#d62728", markersize=3, label="Euclidean")
    ax1.plot(p_g, "-o", color="#2ca02c", markersize=3, label="NG")
    ax1.set_xlabel("embedding step")
    ax1.set_ylabel(r"$p_{\mathrm{stego}}$")
    ax1.set_title("Per-step detector probability")
    ax1.legend()
    ax1.set_ylim(-0.05, 1.05)

    ax2.plot(acc_e, "--s", color="#d62728", markersize=3, label="Euclidean")
    ax2.plot(acc_g, "-o", color="#2ca02c", markersize=3, label="Geodesic")
    ax2.set_xlabel("embedding step")
    ax2.set_ylabel("accumulated log-odds")
    ax2.set_title("Accumulated detector evidence")
    ax2.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "s5_detector_profile.pdf"), dpi=300)
    plt.close(fig)
    print("Saved s5_detector_profile.pdf")

    print("\nDone.")


if __name__ == "__main__":
    main()
