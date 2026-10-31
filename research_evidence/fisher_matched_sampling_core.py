#!/usr/bin/env python3
"""Research reference core: universal-hash rejection sampling for a Bernoulli
cover channel, exact output-bin distribution, and Fisher-natural entropy ascent.
Prior art: rejection sampling is NOT a novel steganographic contribution.
Demonstration uses NumPy RNG, NOT a production-grade CSPRNG.
Full 4-center MNIST-VAE experiment and model checkpoint are in the research ZIP.
"""
import numpy as np

def hash2(images, H):
    H = np.asarray(H, dtype=np.uint8)
    if H.ndim != 2 or H.shape[0] != 2:
        raise ValueError("H must have two binary rows")
    X = np.asarray(images, dtype=np.uint8).reshape(-1, H.shape[1])
    if not np.isin(X, [0, 1]).all() or not np.isin(H, [0, 1]).all():
        raise ValueError("binary carrier and matrix required")
    b = (X.astype(np.uint16) @ H.T.astype(np.uint16)) & 1
    return ((b[:, 0] << 1) | b[:, 1]).astype(np.uint8)

def exact_bin_distribution(prob, H):
    """Walsh inversion of E[(-1)^(a dot H X)] for factorized Bernoulli X."""
    p = np.asarray(prob, dtype=float).ravel()
    H = np.asarray(H, dtype=np.uint8)
    if H.shape != (2, len(p)) or np.min(p) < 0 or np.max(p) > 1:
        raise ValueError("invalid probabilities or hash matrix")
    phi = np.ones(4)
    for a in range(1, 4):
        selected = ((((a >> 1) & 1) * H[0]
                   + (a & 1) * H[1]) & 1).astype(bool)
        phi[a] = np.prod(1 - 2 * p[selected])
    q = np.asarray([
        sum(((-1) ** ((a & b).bit_count() % 2)) * phi[a]
            for a in range(4)) / 4
        for b in range(4)
    ])
    if np.any(q <= 0):
        raise ValueError("some message bins are unreachable")
    # Upper bound computed in logs to avoid reporting exact zero after underflow.
    lp = []
    for a in range(1, 4):
        selected = ((((a >> 1) & 1) * H[0]
                   + (a & 1) * H[1]) & 1).astype(bool)
        lp.append(float(np.log(np.abs(1 - 2 * p[selected])).sum()))
    tv_upper = float(0.5 * np.exp(np.logaddexp.reduce(lp)))
    # For fixed key H and uniform 2-bit ciphertext:
    # TV(P_stego, P_Bernoulli(p)) = 0.5 * sum_b |q_b - 1/4|.
    return q, tv_upper

def sample_cover(p, n, rng):
    p = np.asarray(p, dtype=float).reshape(-1)
    return (rng.random((n, len(p))) < p).astype(np.uint8)

def encode(message2, one_time_pad2, p, H, rng, max_draws=100000):
    """Condition genuine cover draws on the hashed, one-time-padded message."""
    m = np.asarray(message2, dtype=np.uint8)
    pad = np.asarray(one_time_pad2, dtype=np.uint8)
    if m.shape != pad.shape or np.any(m > 3) or np.any(pad > 3):
        raise ValueError("message and pad require equal-length 2-bit words")
    requested = np.bitwise_xor(m, pad)
    D = len(p)
    result = np.empty((len(m), D), dtype=np.uint8)
    attempts = np.zeros(len(m), dtype=np.int32)
    todo = np.arange(len(m))
    while len(todo):
        candidates = sample_cover(p, len(todo), rng)
        accepted = hash2(candidates, H) == requested[todo]
        attempts[todo] += 1
        result[todo[accepted]] = candidates[accepted]
        todo = todo[~accepted]
        if attempts.max() > max_draws:
            raise RuntimeError("rejection budget exhausted; abort, never reassign")
    assert np.array_equal(decode(result, pad, H), m)
    return result, attempts

def decode(binary_carriers, one_time_pad2, H):
    return np.bitwise_xor(hash2(binary_carriers, H),
                          np.asarray(one_time_pad2, dtype=np.uint8))

def fisher_entropy_direction(fisher, gradient):
    """First-order entropy-maximizing direction at unit Fisher quadratic norm."""
    F = np.asarray(fisher, dtype=float)
    g = np.asarray(gradient, dtype=float)
    d = np.linalg.solve(F, g)
    n2 = float(d @ F @ d)
    if n2 <= 0: raise ValueError("Fisher metric must be SPD")
    return d / np.sqrt(n2)

if __name__ == "__main__":
    rng = np.random.default_rng(20261031)
    p = np.linspace(.15, .85, 64)
    H = rng.integers(0, 2, (2, len(p)), dtype=np.uint8)
    q, tv = exact_bin_distribution(p, H)
    messages = rng.integers(0, 4, 200, dtype=np.uint8)
    pads = rng.integers(0, 4, 200, dtype=np.uint8)
    images, draws = encode(messages, pads, p, H, rng)
    print("Correct:", np.array_equal(decode(images, pads, H), messages))
    print("Bin probabilities:", q.tolist())
    print("Hash TV upper bound:", tv)
    print("Mean rejection draws:", float(draws.mean()))
