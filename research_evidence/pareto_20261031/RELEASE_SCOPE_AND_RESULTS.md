# R2.7 / R2.3 — Direct NG-Stego Algorithm 2 multiobjective validation (2026-10-31)

## Status: negative operational outcome, audited implementation
The manuscript's **Algorithm 2 update rule** (Monte-Carlo model-score Fisher estimate, exact KL gradient) is run with numerical damping and Armijo safeguards on the existing Bernoulli MNIST-VAE checkpoint `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`. Six separately seeded codebooks exclude the cover point. A shared 2-bit payload and 100 cover/100 stego observations per held-out codebook are used. Three codebooks train image and public-encoder RBF-SVM detectors; three disjoint codebooks test them. A white-box mixture likelihood-ratio detector is reported separately.

## Recomputed held-out findings (3 codebooks, 300 stego messages per method)

| Method | Public VAE decoder | Pixel-SVM AUC | White-box LRT AUC | Avg KL(P_z||Pcover) (nats) |
|--|--:|--:|--:|--:|
| No embedding | 23.3% | 0.530 | 0.500 | 0 |
| Fisher MC N=256, 1 iter | 51.3% | 0.906 | 0.998 | 31.5 |
| Fisher MC N=256, 3 iter | 65.7% | 0.988 | 0.999 | 62.3 |
| Fisher MC N=256, 10 iter | **85.0%** | **0.987** | **0.999** | **79.5** |
| Euclidean gradient, 10 iter | **95.0%** | **0.993** | **1.000** | **83.7** |
| iMEC adapted to same Bernoulli medium | **300/300 native decode** | 0.507 | not evaluated | not evaluated |
| Discop adapted to same Bernoulli medium | **300/300 native decode** | 0.508 | not evaluated | not evaluated |

Note the **different receiving decoders** (public VAE for path methods, method-native for adapted baselines), and the distinction between **codebook precomputation time** and **online encoding time**. The derived Pinsker total-variation bounds are largely vacuous; KL of endpoints to the cover is high.

## Scientific interpretation
These runs reveal no configuration combining high reliable decoding and low detectable shift for original Algorithm 2. Fisher changes the trajectory used to solve a target-KL optimization; absent constraints changing the target, convergence of Fisher and Euclidean methods to the same target implies the same final output distribution, hence the same final distribution-level security. Do not claim Fisher automatically improves cover/stego undetectability.

## Evidence and reproducibility
- Core sweep: [`pareto_algorithm2_v1.py`](pareto_algorithm2_v1.py)
- Numeric tables: [standard](pareto_algorithm2_summary.csv), [early stopping](pareto_algorithm2_summary_earlystop.csv).
- Detailed narrative: [audit](RAPPORT_PARETO_ALGORITHME2.md) and [reproduction guide](README_REPRODUCTION.md).
- The fully rerunnable 47-file archive (including exact benchmark wrapper, original adapted iMEC source, pretrained VAE, baseline runner, test script, numerical CSV/JSON and rendered report) was assembled locally with ZIP integrity check. SHA-256: `941043cee68dd9586f5084f2ed3b592281d3f73a864ab7e6af5e52348183ed98`.
- The GitHub tree **does not yet contain every dependency and full raw JSON** of the archive; GitHub-only full reproduction is therefore **not yet certified**, despite having core and aggregate results published.

## Editorial decision
These exploratory results strengthen the evidence for Reviewer 2, but **R2.3 and R2.7 remain partially satisfied**. They are not incorporated into the three official submission documents until a consistent reviewer-response strategy is chosen. The mathematical Fisher–Rao framework should be presented as a diagnostic/path-design contribution, **not as proven operational superiority**.
